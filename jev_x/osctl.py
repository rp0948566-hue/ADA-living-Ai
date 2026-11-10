"""OS control layer. One function per capability; each picks the best tool available on this OS."""
import os, platform, shutil, subprocess, sys, tempfile, time, webbrowser

SYS = platform.system()  # 'Linux' | 'Windows' | 'Darwin'
WAYLAND = SYS == 'Linux' and (os.environ.get('XDG_SESSION_TYPE') == 'wayland' or bool(os.environ.get('WAYLAND_DISPLAY')))
NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def have(cmd):
    return shutil.which(cmd) is not None


def run(argv, timeout=30, input=None):
    """Run argv (list) or a shell string; return (code, combined output)."""
    try:
        p = subprocess.run(argv, shell=isinstance(argv, str), capture_output=True, text=True, timeout=timeout,
                           input=input, creationflags=NO_WINDOW, errors='replace')
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, f'timed out after {timeout}s'
    except OSError as e:
        return 127, str(e)


def _ps(script, timeout=30):
    return run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], timeout)


def shell(cmd, timeout=60):
    """Full shell access: bash/sh on Linux+macOS, PowerShell on Windows."""
    if SYS == 'Windows':
        return _ps(cmd, timeout)
    return run(['bash', '-lc', cmd] if have('bash') else cmd, timeout)


def screenshot(path=None):
    path = path or os.path.join(tempfile.gettempdir(), f'jev-x-{int(time.time())}.png')
    tries = []
    if SYS == 'Darwin': tries.append(['screencapture', '-x', path])
    if SYS == 'Linux':
        for argv in (['grim', path], ['gnome-screenshot', '-f', path], ['spectacle', '-b', '-n', '-o', path],
                     ['scrot', '-o', path], ['import', '-window', 'root', path]):
            if have(argv[0]): tries.append(argv)
    for argv in tries:
        code, out = run(argv, 20)
        if code == 0 and os.path.exists(path): return path
    try:
        from PIL import ImageGrab
        ImageGrab.grab().save(path); return path
    except Exception as e:
        raise RuntimeError(f'no screenshot method worked ({e}); install grim, scrot or gnome-screenshot (Linux) or Pillow')


def _xdo(*a):
    if have('xdotool'): return run(['xdotool', *a])
    return 127, 'xdotool missing'


def _ydo(*a):
    if have('ydotool'): return run(['ydotool', *a])
    return 127, 'ydotool missing'


_BTN = {'left': 1, 'middle': 2, 'right': 3}


def move(x, y):
    if SYS == 'Linux':
        code, out = (_ydo('mousemove', '-a', '-x', str(x), '-y', str(y)) if WAYLAND and have('ydotool') else _xdo('mousemove', str(x), str(y)))
    elif SYS == 'Windows':
        code, out = _ps(f'Add-Type -A System.Windows.Forms;[Windows.Forms.Cursor]::Position=New-Object Drawing.Point({int(x)},{int(y)})')
    else:
        code, out = run(['cliclick', f'm:{x},{y}'])
    return code, out


def click(x, y, button='left', double=False):
    code, out = move(x, y)
    if code: return code, out
    n = 2 if double else 1
    if SYS == 'Linux':
        if WAYLAND and have('ydotool'):
            return _ydo('click', *(['0xC0'] if button == 'left' else ['0xC1'] if button == 'right' else ['0xC2']) * n)
        return _xdo('click', '--repeat', str(n), str(_BTN.get(button, 1)))
    if SYS == 'Windows':
        flags = {'left': (2, 4), 'right': (8, 16), 'middle': (32, 64)}[button if button in _BTN else 'left']
        sig = '[DllImport("user32.dll")]public static extern void mouse_event(int f,int x,int y,int d,int e);'
        body = ';'.join(f'[M.U]::mouse_event({f},0,0,0,0)' for _ in range(n) for f in flags)
        return _ps(f'Add-Type -MemberDefinition \'{sig}\' -Name U -Namespace M;{body}')
    return run(['cliclick', ('dc' if double else 'rc' if button == 'right' else 'c') + f':{x},{y}'])


def type_text(text):
    if SYS == 'Linux':
        if WAYLAND and have('ydotool'): return _ydo('type', text)
        return _xdo('type', '--delay', '8', '--', text)
    if SYS == 'Windows':
        esc = text.replace('{', '{{}').replace('}', '{}}').replace('+', '{+}').replace('^', '{^}').replace('%', '{%}').replace('~', '{~}')
        esc = esc.replace('(', '{(}').replace(')', '{)}').replace("'", "''")
        return _ps(f"Add-Type -A System.Windows.Forms;[Windows.Forms.SendKeys]::SendWait('{esc}')")
    return run(['osascript', '-e', 'on run a', '-e', 'tell application "System Events" to keystroke (item 1 of a)', '-e', 'end run', text])


def key(combo):
    """combo like 'ctrl+l', 'Return', 'alt+F4'."""
    if SYS == 'Linux':
        if WAYLAND and have('ydotool') and not have('xdotool'): return _ydo('key', combo)
        return _xdo('key', combo)
    if SYS == 'Windows':
        mods = {'ctrl': '^', 'control': '^', 'alt': '%', 'shift': '+'}
        named = {'return': '{ENTER}', 'enter': '{ENTER}', 'tab': '{TAB}', 'escape': '{ESC}', 'esc': '{ESC}', 'backspace': '{BACKSPACE}',
                 'delete': '{DEL}', 'up': '{UP}', 'down': '{DOWN}', 'left': '{LEFT}', 'right': '{RIGHT}', 'home': '{HOME}', 'end': '{END}',
                 'space': ' ', 'super': '^{ESC}'}
        parts = combo.lower().split('+'); k = parts[-1]
        k = named.get(k, '{%s}' % k.upper() if len(k) > 1 else k)
        return _ps(f"Add-Type -A System.Windows.Forms;[Windows.Forms.SendKeys]::SendWait('{''.join(mods.get(m, '') for m in parts[:-1])}{k}')")
    return run(['osascript', '-e', f'tell application "System Events" to keystroke "{combo[-1]}"'])


def list_windows():
    if SYS == 'Linux':
        if have('wmctrl'):
            code, out = run(['wmctrl', '-l'])
            if code == 0: return out
        if have('xdotool'): return _xdo('search', '--onlyvisible', '--name', '.')[1]
        return 'no window lister (install wmctrl)'
    if SYS == 'Windows':
        return _ps('Get-Process|?{$_.MainWindowTitle}|%{"$($_.Id)`t$($_.ProcessName)`t$($_.MainWindowTitle)"}')[1]
    return run(['osascript', '-e', 'tell application "System Events" to get name of every process whose background only is false'])[1]


def focus_window(title):
    if SYS == 'Linux':
        if have('wmctrl'): return run(['wmctrl', '-a', title])
        return _xdo('search', '--name', title, 'windowactivate')
    if SYS == 'Windows':
        t = title.replace("'", "''")
        return _ps(f"$s=New-Object -Com WScript.Shell;$s.AppActivate('{t}')")
    return run(['osascript', '-e', f'tell application "{title}" to activate'])


def open_target(target):
    """Open an app name, file, folder or URL."""
    if '://' in target:
        return (0, 'opened') if webbrowser.open(target) else (1, 'no browser')
    if SYS == 'Windows': return _ps(f"Start-Process '{target}'")
    if SYS == 'Darwin': return run(['open', '-a', target]) if not os.path.exists(target) else run(['open', target])
    if os.path.exists(target): return run(['xdg-open', target])
    exe = shutil.which(target) or shutil.which(target.lower().replace(' ', '-'))
    if exe:
        subprocess.Popen([exe], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return 0, f'started {exe}'
    return 1, f'{target!r} not found'


def clipboard_get():
    if SYS == 'Windows': return _ps('Get-Clipboard')[1]
    if SYS == 'Darwin': return run(['pbpaste'])[1]
    for argv in (['wl-paste', '-n'], ['xclip', '-o', '-selection', 'clipboard'], ['xsel', '-ob']):
        if have(argv[0]): return run(argv)[1]
    return 'no clipboard tool (install wl-clipboard or xclip)'


def clipboard_set(text):
    if SYS == 'Windows': return run(['clip'], input=text)
    if SYS == 'Darwin': return run(['pbcopy'], input=text)
    for argv in (['wl-copy'], ['xclip', '-selection', 'clipboard'], ['xsel', '-ib']):
        if have(argv[0]):   # these keep running to own the selection, so never wait on their pipes
            p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            p.stdin.write(text.encode()); p.stdin.close(); return 0, 'ok'
    return 127, 'no clipboard tool'


def notify(msg):
    if SYS == 'Linux' and have('notify-send'): return run(['notify-send', 'Jev-X', msg])
    if SYS == 'Darwin': return run(['osascript', '-e', f'display notification {msg!r} with title "Jev-X"'])
    if SYS == 'Windows': return _ps(f"msg * '{msg}'")
    return 127, 'no notifier'


def screen_size():
    if SYS == 'Linux' and have('xdotool'):
        out = _xdo('getdisplaygeometry')[1].split()
        if len(out) == 2: return int(out[0]), int(out[1])
    try:
        from PIL import Image
        return Image.open(screenshot()).size
    except Exception:
        return None


def capabilities():
    """What this machine can actually do right now (shown by --doctor)."""
    c = {'os': SYS, 'display': 'wayland' if WAYLAND else os.environ.get('DISPLAY', 'none') if SYS == 'Linux' else 'native'}
    if SYS == 'Linux':
        for t in ('xdotool', 'ydotool', 'wmctrl', 'grim', 'scrot', 'gnome-screenshot', 'xclip', 'wl-copy', 'notify-send', 'xdg-open'):
            c[t] = have(t)
    elif SYS == 'Windows': c['powershell'] = have('powershell')
    else: c['cliclick'] = have('cliclick')
    return c
