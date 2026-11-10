"""Window-manager and display layer for Linux (X11 and XWayland: wmctrl/xdotool/xrandr). Mirrors what the Swift app's
CGWindowList/AX calls give jev.py on macOS. Frames are [x, y, w, h] in top-left screen pixels, like System Events."""
import os, re, shutil, subprocess

def _run(argv, timeout=3):
    try: return subprocess.run(argv, capture_output=True, text=True, timeout=timeout).stdout
    except (OSError, subprocess.TimeoutExpired): return ''

def have(c): return shutil.which(c) is not None

def _comm(pid):
    try:
        with open(f'/proc/{pid}/comm') as f: return f.read().strip()
    except OSError: return ''

def shell(method, *args):
    """Jev's GNOME Shell extension (org.jev.Windows): the only way to see and move native Wayland windows. None if it is not loaded."""
    sig = {'Place': ['u', 'i', 'i', 'i', 'i'], 'Focus': ['u']}.get(method, [])
    argv = ['gdbus', 'call', '--session', '-d', 'org.jev.Windows', '-o', '/org/jev/Windows', '-m', f'org.jev.Windows.{method}']
    argv += [f'{a}' if t != 'u' else f'uint32 {a}' for t, a in zip(sig, args)]
    out = _run(argv, 2).strip()
    m = re.match(r"^\((.*),\)$", out)
    if not m: return None
    v = m.group(1)
    if v in ('true', 'false'): return v == 'true'
    import ast
    try: return ast.literal_eval(v)
    except (ValueError, SyntaxError): return None

def shell_windows():
    import json
    raw = shell('List')
    try: return [{'id': w['id'], 'desktop': 0, 'pid': w['pid'], 'frame': w['frame'], 'cls': w['gid'].removesuffix('.desktop') or w['cls'],
                  'app': app_name(w['gid'].removesuffix('.desktop') or w['cls'], w['pid']), 'title': w['title'], 'shell': True,
                  'focus': w['focus']} for w in json.loads(raw)] if raw else []
    except (ValueError, KeyError): return []

def windows():
    """Every top-level window: dict(id, desktop, pid, frame, cls, app, title). Empty if no X server answers."""
    rows = shell_windows()
    if rows: return rows
    rows = []
    for line in _run(['wmctrl', '-lGpx']).splitlines():
        p = line.split(None, 9)
        if len(p) < 9: continue
        try: wid, desk, pid, x, y, w, h = p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(p[6])
        except ValueError: continue
        cls = p[7].split('.')[-1]
        rows.append({'id': int(wid, 16), 'desktop': desk, 'pid': pid, 'frame': [x, y, w, h], 'cls': cls,
                     'app': app_name(cls, pid), 'title': p[9] if len(p) > 9 else ''})
    return rows or atspi_windows()

def _atspi_rows():
    import gi; gi.require_version('Atspi', '2.0'); from gi.repository import Atspi
    desk, rows = Atspi.get_desktop(0), []
    for i in range(desk.get_child_count()):
        a = desk.get_child_at_index(i); pid = a.get_process_id()
        if a.get_name() in ('gnome-shell', 'mutter-x11-frames'): continue
        for j in range(a.get_child_count()):
            w = a.get_child_at_index(j)
            if w.get_role_name() in ('frame', 'window', 'dialog') and w.get_name():
                rows.append({'id': pid * 1000 + j, 'desktop': 0, 'pid': pid, 'frame': [0, 0, 0, 0], 'cls': a.get_name(), 'title': w.get_name()})
    return rows

def atspi_windows():
    """Wayland fallback: AT-SPI lists apps and window titles (no geometry, no moving). Runs in a child process with a timeout:
    libatspi aborts the whole process when the accessibility bus is unreachable."""
    import json, sys
    try:
        out = subprocess.run([sys.executable, os.path.abspath(__file__), '--atspi-windows'], capture_output=True, text=True, timeout=4).stdout
        return [{**r, 'app': app_name(r['cls'], r['pid'])} for r in json.loads(out or '[]')]
    except Exception: return []

def app_name(cls, pid=0):
    """WM_CLASS -> the name a person says ("Google-chrome" -> Google Chrome via its .desktop file, else the class)."""
    key = re.sub(r'[^a-z0-9]', '', cls.lower())
    for name, d in desktop_apps().items():
        if key in (re.sub(r'[^a-z0-9]', '', d['wm'].lower()), re.sub(r'[^a-z0-9]', '', d['id'].lower()), re.sub(r'[^a-z0-9]', '', d['exe'].lower())):
            return name
    return cls.replace('-', ' ').title() if cls else _comm(pid)

def active_id():
    out = _run(['xdotool', 'getactivewindow']).strip()
    return int(out) if out.isdigit() else 0

def active():
    wid = active_id()
    return next((w for w in windows() if w['id'] == wid), None)

_DESK = None
def desktop_apps(refresh=False):
    """{display name: {id, exe, wm, path}} from .desktop files, the Linux equivalent of /Applications."""
    global _DESK
    if _DESK is not None and not refresh: return _DESK
    out, dirs = {}, [os.path.expanduser('~/.local/share/applications'), '/usr/share/applications', '/usr/local/share/applications',
                     '/var/lib/flatpak/exports/share/applications', os.path.expanduser('~/.local/share/flatpak/exports/share/applications'),
                     '/var/lib/snapd/desktop/applications']
    for d in dirs:
        try: names = os.listdir(d)
        except OSError: continue
        for f in names:
            if not f.endswith('.desktop'): continue
            try:
                txt = open(os.path.join(d, f), errors='replace').read().split('[Desktop Action')[0]
            except OSError: continue
            kv = dict(l.split('=', 1) for l in txt.splitlines() if '=' in l and not l.startswith('#'))
            if kv.get('Type') != 'Application' or kv.get('NoDisplay') == 'true' or kv.get('Hidden') == 'true' or not kv.get('Name'): continue
            exe = re.sub(r'%[a-zA-Z]', '', kv.get('Exec', '')).split()
            exe = next((os.path.basename(t) for t in exe if t not in ('env', 'sh', 'bash', '-c') and '=' not in t), '')
            out.setdefault(kv['Name'], {'id': f[:-8], 'exe': exe, 'wm': kv.get('StartupWMClass', ''), 'path': os.path.join(d, f)})
    _DESK = out
    return out

def screens():
    """[(name, x, y, w, h, built_in)] main first, via xrandr (XWayland reports real monitors on GNOME)."""
    rows = []
    for line in _run(['xrandr', '--listmonitors']).splitlines()[1:]:
        m = re.match(r'\s*\d+:\s+[+*]*(\S+)\s+(\d+)/\d+x(\d+)/\d+\+(-?\d+)\+(-?\d+)\s+(\S+)', line)
        if m:
            primary = '*' in line.split()[1]
            rows.append((primary, m.group(6), int(m.group(4)), int(m.group(5)), int(m.group(2)), int(m.group(3))))
    rows.sort(key=lambda r: not r[0])
    out = [(n, x, y, w, h, bool(re.match(r'(eDP|LVDS|DSI)', n, re.I))) for _, n, x, y, w, h in rows]
    if not out:
        g = _run(['xdotool', 'getdisplaygeometry']).split()
        if len(g) == 2: out = [('Screen', 0, 0, int(g[0]), int(g[1]), True)]
    return out

def is_x11():
    return bool(windows_x11_ok())

def windows_x11_ok():
    return bool(_run(['wmctrl', '-m']).strip())


if __name__ == '__main__':
    import json, sys
    if sys.argv[1:] == ['--atspi-windows']:
        try: print(json.dumps(_atspi_rows()))
        except Exception: print('[]')
