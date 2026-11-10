"""Linux replacements for jev.py's macOS functions. install(g) rebinds them in jev.py's globals, so every caller
(the box, fast commands, the AI's helper commands) uses the Linux version and the Mac code path stays untouched.
Receipts and return shapes match the Mac functions line for line; see docs/LINUX-PORT.md."""
import os, re, shutil, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wm

HERE = os.path.dirname(os.path.abspath(__file__))


def install(g):
    run = subprocess.run
    os.environ['PATH'] = os.path.join(HERE, 'bin') + os.pathsep + os.environ.get('PATH', '')   # open/mdfind/pbpaste/say/trash/osascript stand-ins
    os.environ.setdefault('JEV_APP', os.path.join(HERE, 'native'))   # the Linux counterpart of Jev.app's command-line verbs
    g['APP'] = os.environ['JEV_APP']
    g['SYSTEM'] = g['SYSTEM'].replace('You are Jev, a Mac helper', 'You are Jev, a Linux helper').replace('URL scheme, osascript or hands', 'URL scheme, xdg-open or hands')
    # Linux trash labels each item "deleted by Jev - <the user's request>" itself; --why/--by only when the user names a reason or name
    for k in ('NEVER', 'ASK_FIRST'):
        g[k] = g[k].replace('Files: trash "<path>", never rm.', 'Files: trash "<path>" (auto-labelled; add --why "<reason>" or --by "<name>" only if the user says), never rm.') + (' Linux tools: sysinfo (live CPU/RAM/disk/temperature/GPU/battery + warnings), screentext (the screen as text).'
                ' Spoken voice: say --tone normal|calm|deep|fast|soft "text" (neural). Clone a voice (optional, heavy): voice_clone.py add <name> <sample.wav>, then say <name> "text".'
                 ' Browser agent: browser open <url> | read | click <n> | fill <n> "text" | type-after "anchor" "text" | back | hide | show — numbers come from read; it uses Jev\'s own visible browser the user can watch; "browser yours" drives the user\'s real browser. Prefer it over hands for web pages.'
                ' Software or files the task needs: get them yourself, no asking: pkexec apt-get install -y <pkg> (the system asks for the password),'
                ' pip install --target ~/.local/share/jev/py <pkg>, npm install -g --prefix ~/.local <pkg>, git clone, curl -L -o ~/Downloads/<file> <url>; never sudo, never pipe a download into a shell.')
    if g['pref']('sudo', False):   # the user set up sudoers caching; the OS asks for the password once and remembers it
        for k in ('NEVER', 'ASK_FIRST'):
            g[k] = g[k].replace('never sudo,', 'sudo <apt/dnf/pacman/snap/flatpak/systemctl ...> for system changes (the system asks for the password, not you; never sudo rm/dd/tee/bash),')

    def osa(script, *args, timeout=60):
        return ''   # AppleScript does not exist here; every caller treats '' as "no answer"

    def screens():
        return wm.screens()

    def front():
        app = os.environ.get('JEV_FRONT')
        w = wm.active()
        if app: return app, next((x['title'] for x in wm.windows() if x['app'] == app), '')
        return (w['app'], w['title']) if w else ('', '')

    def restore_focus(app, task, cmds): return None   # no focus guard on Linux: the window manager does not steal focus back

    def free_focus(user=False): return None

    def request_screen():
        if os.environ.get('JEV_SCREEN'): return os.environ['JEV_SCREEN']
        w = next((x for x in wm.windows() if x['app'] == os.environ.get('JEV_FRONT')), None) or wm.active()
        if w and w['frame'][2]:
            x, y = w['frame'][0] + 50, w['frame'][1] + 50
            return next((n for n, sx, sy, sw, sh, _ in wm.screens() if sx <= x < sx + sw and sy <= y < sy + sh), 'current')
        return 'current'

    def placement_window(proc, title):
        key = lambda s: ' '.join(re.split(r'[\s_-]+', s.casefold())).strip()
        want = key(title)
        for _ in range(4):
            rows = [w for w in wm.windows() if key(w['app']) == key(proc) or key(w['cls']) == key(proc)]
            found = [w for w in rows if key(w['title']) == want] or [w for w in rows if want and want in key(w['title'])] if title else rows[:1]
            if len(found) == 1: return found[0]['title'], None
            if found: return None, f'NOT DONE: more than one {proc} window matches "{title or found[0]["title"]}"; nothing moved. Ask which one.'
            time.sleep(0.4)
        return None, f'no window found for "{proc}" {title}'

    def place(proc, where='full', screen='current', title=''):
        native = where == 'fullscreen'
        if native: where = 'full'
        if where not in ('left', 'right', 'full', 'center'):
            return 'where must be left, right, full, fullscreen or center'
        if screen == 'current': screen = request_screen()
        name, problem = placement_window(proc, title)
        if problem: return problem
        win = next(w for w in wm.windows() if w['title'] == name and (wm.app_name(w['cls']) == proc or w['app'] == proc or w['cls'].lower() == proc.lower()))
        if not win.get('shell') and (not win['frame'][2] or not shutil.which('wmctrl') or os.environ.get('XDG_SESSION_TYPE') == 'wayland' and win['frame'][2] == 0):
            return (f'NOT DONE: this Wayland session does not let apps move windows ({proc}). Say so; do not report success. '
                    'Log in with "Ubuntu on Xorg" to arrange windows.')
        scr = wm.screens()
        pick = {'laptop': lambda s: s[5], 'monitor': lambda s: not s[5]}.get(
            screen, (lambda s: s[0] == screen) if screen != 'current' else (lambda s: True))
        n, x, y, w, h, _ = next((s for s in scr if pick(s)), scr[0])
        px, py, ww, wh = win['frame']
        cw, ch = min(ww, w), min(wh, h)
        bx, by, bw, bh = {'left': (x, y, w // 2, h), 'right': (x + w // 2, y, w - w // 2, h), 'full': (x, y, w, h),
                          'center': (x + (w - cw) // 2, y + (h - ch) // 2, cw, ch)}[where]
        if win.get('shell'):
            ok = wm.shell('Place', win['id'], bx, by, bw, bh)
            time.sleep(0.4)
            now = next((w2 for w2 in wm.windows() if w2['id'] == win['id']), None)
            if ok and now and abs(now['frame'][0] - bx) < 40 and abs(now['frame'][2] - bw) < 60: return f'{proc} window -> {where} of {n}'
            return f'NOT DONE: {proc} window did not move to {n}. Say so; do not report success.'
        wid = hex(win['id'])
        run(['wmctrl', '-i', '-r', wid, '-b', 'remove,maximized_vert,maximized_horz,fullscreen'], capture_output=True)
        run(['wmctrl', '-i', '-r', wid, '-e', f'0,{bx},{by},{bw},{bh}'], capture_output=True)
        if native: run(['wmctrl', '-i', '-r', wid, '-b', 'add,fullscreen'], capture_output=True)
        time.sleep(0.3)
        now = next((w2 for w2 in wm.windows() if w2['id'] == win['id']), None)
        if not now: return f'Moved {proc}, but could not check where its window is. Look at the screen before saying it worked or moving it again.'
        l, t, ww2, hh2 = now['frame']
        if not (x <= l + ww2 // 2 < x + w and y <= t + hh2 // 2 < y + h):
            return f'NOT DONE: {proc} window did not move to {n}. Say so; do not report success.'
        return f'{proc} window -> {"fullscreen" if native else where} of {n}'

    def installed_apps():
        return set(wm.desktop_apps())

    def _entry(app): return wm.desktop_apps().get(app, {})
    def proc_of(app): return _entry(app).get('exe') or app
    def app_id(app): return _entry(app).get('id', '')
    def app_running(bid):
        exe = next((d['exe'] for d in wm.desktop_apps().values() if d['id'] == bid), bid)
        return bool(exe) and run(['pgrep', '-x', exe[:15]], capture_output=True).returncode == 0
    def quit_app(bid):
        if not app_running(bid): return True
        exe = next((d['exe'] for d in wm.desktop_apps().values() if d['id'] == bid), bid)
        run(['pkill', '-x', exe[:15]], capture_output=True, timeout=2)
        for _ in range(10):
            if not app_running(bid): return True
            time.sleep(0.1)
        return False

    def notify(text):
        run(['notify-send', 'Jev', text], capture_output=True)

    def _capture(path):
        """Full virtual screen to path (png/jpg by extension). Tries each tool this desktop has."""
        import shot
        if shot.capture(path): return True
        try:
            from PIL import ImageGrab; ImageGrab.grab(xdisplay=None).save(path); return True
        except Exception: return False

    def look(cleanup=True, window=None):
        """Every display at 1280 px wide -> [(path, label)] (same labels as macOS)."""
        from PIL import Image
        scr = wm.screens()
        fd, whole = tempfile.mkstemp(prefix='jev-full-', suffix='.png'); os.close(fd)
        shots = []
        try:
            if not _capture(whole): return []
            img = Image.open(whole).convert('RGB')
            sx = img.width / max(1, max(s[1] + s[3] for s in scr)); sy = img.height / max(1, max(s[2] + s[4] for s in scr))
            ask = os.environ.get('JEV_ASK') or None
            for i, (name, x, y, w, h, built_in) in enumerate(scr, 1):
                crop = img.crop((int(x * sx), int(y * sy), int((x + w) * sx), int((y + h) * sy)))
                crop = crop.resize((1280, max(1, round(1280 * crop.height / crop.width))))
                try: fd, path = tempfile.mkstemp(prefix=f'jev-screen-{i}-', suffix='.jpg', dir=ask)
                except OSError: fd, path = tempfile.mkstemp(prefix=f'jev-screen-{i}-', suffix='.jpg')
                os.close(fd); crop.save(path, 'JPEG', quality=70)
                if cleanup and not ask:
                    import atexit; atexit.register(lambda p=path: os.path.exists(p) and os.remove(p))
                shots.append((path, f'Screen {i}: "{name}" ({"built-in laptop screen" if built_in else "external monitor"}; click spots as {i}:x,y in picture pixels)'))
        finally:
            os.path.exists(whole) and os.remove(whole)
        return shots

    def hands(*args):
        """The only model-facing native helper (Mac: hands() over Hands.swift). Linux: linux/hands.py over AT-SPI + uinput."""
        if not args or args[0] not in g['HANDS_VERBS'] or any(a.startswith('--') for a in args[1:]):
            return 'Use --hands see|menu|click|scroll|scroll-to|press|drag|type|type-after|wait; no flags.', False
        if not g['wait_commit']():
            return 'The request was cancelled before the transcript was confirmed.', False
        # safe mode: a click that sends, buys or deletes asks first, as hands_action's authorize does on the Mac
        if g['pref']('safe', True) and args[0] in ('click', 'press') and os.environ.get('JEV_ASK') and \
                re.search(r'\b(send|buy|pay|purchase|order|delete|remove|post|submit|transfer)\b', ' '.join(args[1:]), re.I):
            if not (g['task_allowed']('*') or g['told_not_to_ask']()):
                answer = g['ask_user']({'q': 'Allow this click?', 'cmd': ' '.join(args), 'task': True}, 600)
                if answer == 'task': g['allow_for_task']('*')
                if answer not in ('y', 'task'): return 'The user said no. Do not try another way.', False
        try:
            r = run([sys.executable, os.path.join(HERE, 'hands.py'), *args], capture_output=True, text=True, timeout=45)
        except subprocess.TimeoutExpired:
            return 'not_done: hands timed out', False
        return (r.stdout.strip() or r.stderr.strip()[-300:] or 'not_done'), r.returncode == 0

    for f in (osa, screens, front, restore_focus, free_focus, request_screen, placement_window, place, installed_apps, proc_of, app_id,
              app_running, quit_app, notify, look, hands):
        g[f.__name__] = f
