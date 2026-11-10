"""Linux `--hands`: the Swift Hands enum (see/click/menu/scroll/press/type/wait) over AT-SPI labels, with a uinput
keyboard and mouse for keys, wheel and clicks (works on Wayland, where xdotool reaches only X11 windows).
Runs as its own process: libatspi aborts the whole process when the accessibility bus is missing."""
import fcntl, json, os, re, socket, struct, sys, time

# ---------------------------------------------------------------- uinput: a virtual keyboard + mouse
EV_SYN, EV_KEY, EV_REL = 0, 1, 2
REL_WHEEL, REL_HWHEEL, REL_X, REL_Y = 8, 6, 0, 1
EV_ABS, ABS_X, ABS_Y, ABS_MAX = 3, 0, 1, 65535
BTN_LEFT, BTN_RIGHT = 0x110, 0x111
KEYS = {'esc': 1, 'escape': 1, 'backspace': 14, 'delete': 111, 'tab': 15, 'enter': 28, 'return': 28, 'space': 57,
        'ctrl': 29, 'control': 29, 'shift': 42, 'alt': 56, 'option': 56, 'super': 125, 'meta': 125, 'win': 125,
        'cmd': 29, 'command': 29,   # ⌘ shortcuts are Ctrl shortcuts on Linux
        'capslock': 58, 'home': 102, 'up': 103, 'pageup': 104, 'left': 105, 'right': 106, 'end': 107, 'down': 108,
        'pagedown': 109, 'insert': 110, **{f'f{i}': 58 + i for i in range(1, 11)}, 'f11': 87, 'f12': 88}
for row, start in (('1234567890-=', 2), ('qwertyuiop[]', 16), ("asdfghjkl;'`", 30), ('\\zxcvbnm,./', 43)):
    for i, ch in enumerate(row): KEYS[ch] = start + i
SHIFTED = dict(zip('!@#$%^&*()_+{}:"~|<>?', '1234567890-=[];\'`\\,./'))


class Device:
    def __init__(self):
        self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
        io = lambda req, v: fcntl.ioctl(self.fd, req, v)
        io(0x40045564, EV_KEY); io(0x40045564, EV_REL)   # UI_SET_EVBIT
        for code in set(KEYS.values()) | {BTN_LEFT, BTN_RIGHT}: io(0x40045565, code)   # UI_SET_KEYBIT
        for code in (REL_X, REL_Y, REL_WHEEL, REL_HWHEEL): io(0x40045566, code)   # UI_SET_RELBIT
        fcntl.ioctl(self.fd, 0x405c5503, struct.pack('HHHH80sI', 3, 0x1234, 0x5678, 1, b'Jev hands', 0))   # UI_DEV_SETUP
        fcntl.ioctl(self.fd, 0x5501)   # UI_DEV_CREATE
        time.sleep(.35)   # the compositor must notice the new device before its first event

    def emit(self, t, code, value):
        os.write(self.fd, struct.pack('llHHi', 0, 0, t, code, value))

    def sync(self): self.emit(EV_SYN, 0, 0)

    def key(self, code, down):
        self.emit(EV_KEY, code, 1 if down else 0); self.sync(); time.sleep(.012)

    def combo(self, names):   # "ctrl+shift+t"
        codes = [KEYS[n] for n in names]
        for c in codes: self.key(c, True)
        for c in reversed(codes): self.key(c, False)

    def text(self, s):
        for ch in s:
            low = ch.lower()
            if ch == '\n': self.combo(['enter'])
            elif ch == ' ': self.combo(['space'])
            elif ch in SHIFTED: self.combo(['shift', SHIFTED[ch]])
            elif low in KEYS and len(low) == 1: self.combo(['shift', low] if ch != low else [low])
            else: return False
        return True

    def wheel(self, axis, n):
        for _ in range(abs(n)):
            self.emit(EV_REL, axis, -1 if n > 0 else 1); self.sync(); time.sleep(.02)

    def click(self, button=BTN_LEFT, times=1):
        for _ in range(times):
            self.key(button, True); self.key(button, False); time.sleep(.06)

    def close(self):
        time.sleep(.05); fcntl.ioctl(self.fd, 0x5502); os.close(self.fd)   # UI_DEV_DESTROY

class Pointer(Device):
    """Absolute pointer (a virtual tablet) so drag and clicks land on a point, not wherever the mouse happens to be."""
    def __init__(self):
        self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)
        io = lambda req, v: fcntl.ioctl(self.fd, req, v)
        io(0x40045564, EV_KEY); io(0x40045564, EV_ABS)
        for code in (BTN_LEFT, BTN_RIGHT): io(0x40045565, code)
        for code in (ABS_X, ABS_Y):
            io(0x40045567, code)   # UI_SET_ABSBIT
            fcntl.ioctl(self.fd, 0x401c5504, struct.pack('HHiiiiii', code, 0, 0, 0, ABS_MAX, 0, 0, 0))   # UI_ABS_SETUP
        fcntl.ioctl(self.fd, 0x405c5503, struct.pack('HHHH80sI', 3, 0x1234, 0x5679, 1, b'Jev pointer', 0))
        fcntl.ioctl(self.fd, 0x5501)
        time.sleep(.35)
        self.w, self.h = screen_size()

    def move(self, x, y):
        self.emit(EV_ABS, ABS_X, int(max(0, min(1, x / self.w)) * ABS_MAX)); self.emit(EV_ABS, ABS_Y, int(max(0, min(1, y / self.h)) * ABS_MAX))
        self.sync(); time.sleep(.05)

    def drag(self, a, b):
        self.move(*a); self.key(BTN_LEFT, True)
        for i in range(1, 11): self.move(a[0] + (b[0] - a[0]) * i / 10, a[1] + (b[1] - a[1]) * i / 10)   # a stepped path, as a hand moves
        self.key(BTN_LEFT, False)


def screen_size():
    import gi
    gi.require_version('Gdk', '3.0')
    from gi.repository import Gdk
    g = Gdk.Display.get_default().get_monitor(0).get_geometry()
    return g.width, g.height


def step_aside():
    """Keys go to the focused window: if that is Jev's own box, the box steps aside first (the Mac panel never takes key focus)."""
    try:
        c = socket.socket(socket.AF_UNIX); c.settimeout(1)
        c.connect(os.path.join(os.environ.get('XDG_RUNTIME_DIR') or '/tmp', f'jev-{os.getuid()}.sock'))
        c.sendall(b'blur'); c.recv(8); c.close(); time.sleep(.25)
    except OSError: pass


def paste(text):   # characters a US key map cannot type: through the clipboard
    import subprocess
    for cmd in (['wl-copy'], ['xclip', '-selection', 'clipboard']):
        try:
            subprocess.run(cmd, input=text, text=True, timeout=3, check=True); return True
        except (OSError, subprocess.SubprocessError): continue
    return False


# ---------------------------------------------------------------- AT-SPI: apps, windows and labelled controls
def atspi():
    import gi
    gi.require_version('Atspi', '2.0')
    from gi.repository import Atspi
    return Atspi

INTERACTIVE = {'push button', 'toggle button', 'check box', 'radio button', 'menu item', 'check menu item', 'radio menu item',
               'link', 'entry', 'text', 'password text', 'combo box', 'page tab', 'list item', 'tree item', 'spin button',
               'slider', 'menu', 'table cell', 'icon', 'button', 'switch', 'search bar'}


def apps(A):
    d = A.get_desktop(0)
    return [a for a in (d.get_child_at_index(i) for i in range(d.get_child_count())) if a]


def name(x):
    try: return (x.get_name() or '').strip()
    except Exception: return ''


def front_app(A):
    """The app whose window is active (JEV_FRONT names the one the user was in before the box opened)."""
    want = os.environ.get('JEV_FRONT', '').casefold()
    found = None
    me = int(os.environ.get('JEV_HOST_PID') or 0)
    for a in apps(A):
        try:
            if me and a.get_process_id() == me: continue   # the box itself: asking it would wait on its own busy main loop
        except Exception: continue
        if want and name(a).casefold() == want: return a
        for i in range(min(a.get_child_count(), 30)):
            w = a.get_child_at_index(i)
            try:
                if w and w.get_state_set().contains(A.StateType.ACTIVE) and name(a) not in ('python3', 'host.py', 'Jev', 'gnome-shell'):
                    found = found or a
            except Exception: continue
    return found


def find_app(A, word):
    w = word.casefold()
    for a in apps(A):
        if name(a).casefold() == w: return a
    return next((a for a in apps(A) if w in name(a).casefold()), None)


def walk(x, depth=0, limit=[0]):
    if depth == 0: limit[0] = 0
    if limit[0] > 5000 or depth > 40: return
    limit[0] += 1
    yield x, depth
    try: n = x.get_child_count()
    except Exception: return
    for i in range(min(n, 400)):
        try: c = x.get_child_at_index(i)
        except Exception: continue
        if c: yield from walk(c, depth + 1, limit)


def showing(A, x):
    try:
        s = x.get_state_set()
        return s.contains(A.StateType.SHOWING) or s.contains(A.StateType.VISIBLE)
    except Exception: return False


def controls(A, app):
    rows = []
    for x, _ in walk(app):
        try: role = x.get_role_name()
        except Exception: continue
        if role in INTERACTIVE and showing(A, x):
            label = name(x)
            if not label and role in ('entry', 'text', 'password text'):
                label = '(text field)'
            if label: rows.append((role, label, x))
    return rows


def pick(rows, target):
    t = target.casefold().strip('"')
    exact = [r for r in rows if r[1].casefold() == t]
    return (exact or [r for r in rows if t in r[1].casefold()] or [None])[0]


def act(A, x, how=''):
    """Click a control: its own accessible action first (works covered and unfocused), else the mouse at its centre."""
    try:
        if not how and x.get_n_actions() > 0:
            names = [x.get_action_name(i) for i in range(x.get_n_actions())]
            i = next((names.index(n) for n in ('click', 'press', 'activate', 'jump', 'toggle') if n in names), 0)
            if x.do_action(i): return True
    except Exception: pass
    try: x.grab_focus()
    except Exception: pass
    step_aside()
    d = Device()
    try:
        r = x.get_extents(A.CoordType.SCREEN)
        if r.width <= 0: return False
        d.click(BTN_RIGHT if how == 'right' else BTN_LEFT, 2 if how == 'double' else 1)   # shortcut: clicks where the pointer is after focus; absolute pointing needs a tablet device
        return True
    finally: d.close()


def see(A, args):
    app = find_app(A, args[0]) if args else front_app(A)
    if not app: return 'not_done: no app with an accessible window is in front. Name the app: see "<app>".', 1
    rows = controls(A, app)
    lines = [f'App: {name(app)}'] + [f'- {role} "{label}"' for role, label, _ in rows[:120]]
    if len(rows) > 120: lines.append(f'… {len(rows) - 120} more')
    if not rows: lines.append('(no labelled controls exposed; use press/type, or the window reader)')
    return '\n'.join(lines), 0


def cli(args):
    if not args: print('Use --hands see|menu|click|drag|scroll|scroll-to|press|type|type-after|wait'); return 1
    verb, rest = args[0], args[1:]
    try:
        if verb == '--front':   # for the box: the app in front before it opens
            a = front_app(atspi()); print(name(a) if a else ''); return 0
        if verb == 'wait':
            time.sleep(min(30, float(rest[0]) if rest else 1)); print('done'); return 0
        if verb == 'press':
            keys = rest[0].lower().replace(' ', '').split('+') if rest else []
            times = int(rest[1]) if len(rest) > 1 and rest[1].isdigit() else 1
            if not keys or any(k not in KEYS for k in keys): print(f'not_done: unknown key in "{rest[0] if rest else ""}"'); return 1
            step_aside(); d = Device()
            try:
                for _ in range(min(times, 50)): d.combo(keys)
            finally: d.close()
            print(f'done: pressed {rest[0]}' + (f' ×{times}' if times > 1 else '')); return 0
        if verb == 'scroll':
            way = rest[0] if rest else 'down'
            n = (30 if 'all' in rest else 10 if 'pages' in rest else 5) * (1 if way in ('down', 'right') else -1)
            step_aside(); d = Device()
            try: d.wheel(REL_HWHEEL if way in ('left', 'right') else REL_WHEEL, -n if way in ('left', 'right') else n)
            finally: d.close()
            print(f'done: scrolled {way}'); return 0
        A = atspi()
        if verb == 'see':
            out, code = see(A, rest); print(out); return code
        if verb == 'click':
            if not rest: print('not_done: click <label>'); return 1
            how = 'double' if 'double' in rest[1:] else 'right' if 'right' in rest[1:] else ''
            app = front_app(A)
            row = pick(controls(A, app), rest[0]) if app else None
            if not row: print(f'not_done: no control labelled "{rest[0]}" in {name(app) or "the front app"}. Run see first.'); return 1
            if act(A, row[2], how): print(f'done: clicked {row[0]} "{row[1]}" in {name(app)}'); return 0
            print(f'not_done: {row[0]} "{row[1]}" did not respond to a click'); return 1
        if verb == 'menu':
            app = find_app(A, rest[0]) if rest else None
            if not app or len(rest) < 2: print('not_done: menu <app> "File > Save"'); return 1
            node = app
            for part in [p.strip() for p in rest[1].split('>')]:
                rows = [(r, l, x) for r, l, x in ((x.get_role_name(), name(x), x) for x, _ in walk(node)) if 'menu' in r]
                row = pick(rows, part)
                if not row: print(f'not_done: no menu item "{part}"'); return 1
                act(A, row[2]); node = row[2]; time.sleep(.3)
            print(f'done: chose {rest[1]} in {name(app)}'); return 0
        if verb == 'drag':
            if len(rest) != 2: print('not_done: drag <from> <to>'); return 1
            app = front_app(A); rows = controls(A, app) if app else []
            ends = [pick(rows, t) for t in rest]
            if not all(ends): print(f'not_done: no control labelled "{rest[ends.index(None)]}" in {name(app) or "the front app"}. Run see first.'); return 1
            pts = []
            for _, _, x in ends:
                r = x.get_extents(A.CoordType.SCREEN)
                if r.width <= 0: print('not_done: that control has no on-screen position'); return 1
                pts.append((r.x + r.width / 2, r.y + r.height / 2))
            step_aside(); p = Pointer()
            try: p.drag(*pts)
            finally: p.close()
            print(f'done: dragged "{ends[0][1]}" to "{ends[1][1]}"'); return 0
        if verb == 'scroll-to':
            if len(rest) != 1: print('not_done: scroll-to "text"'); return 1
            app = front_app(A)
            if not app: print('not_done: no app in front'); return 1
            want = rest[0].casefold()
            for tries in range(13):   # on screen already or scrollable into view by the app; else wheel down and look again
                hit = next((x for x, _ in walk(app) if want in name(x).casefold()), None)
                if hit and showing(A, hit):
                    try: hit.scroll_to(A.ScrollType.ANYWHERE)
                    except Exception: pass
                    print(f'done: "{rest[0]}" is on screen'); return 0
                if hit:
                    try:
                        if hit.scroll_to(A.ScrollType.ANYWHERE): print(f'done: scrolled to "{rest[0]}"'); return 0
                    except Exception: pass
                step_aside(); d = Device()
                try: d.wheel(REL_WHEEL, 5)
                finally: d.close()
                time.sleep(.3)
            print(f'not_done: could not find "{rest[0]}" by scrolling'); return 1
        if verb == 'type-after':
            if len(rest) != 2 or not rest[0]: print('not_done: type-after "<exact anchor>" "text"'); return 1
            anchor, text = rest; app = front_app(A)
            for x, _ in (walk(app) if app else []):
                try:
                    if x.get_role_name() not in ('entry', 'text', 'password text', 'terminal', 'document text', 'document web'): continue
                    body = A.Text.get_text(x, 0, x.get_character_count())
                except Exception: continue
                if body.count(anchor) == 1:   # exactly one match, so the caret position is unambiguous
                    at = body.index(anchor) + len(anchor)
                    if x.insert_text(at, text, len(text.encode())):
                        print('done: Typing dispatched. Do not repeat typing without inspecting it.'); return 0
                elif body.count(anchor) > 1: print(f'not_done: "{anchor}" appears more than once; use a longer exact anchor'); return 1
            print(f'not_done: no editable text contains "{anchor}"'); return 1
        if verb == 'type':
            if len(rest) < 2: print('not_done: type <field> "text" [submit] [append]'); return 1
            field, text, flags = rest[0], rest[1], rest[2:]
            app = front_app(A)
            row = pick([r for r in controls(A, app) if r[0] in ('entry', 'text', 'password text', 'combo box', 'search bar', 'spin button')], field) if app else None
            done = False
            if row:
                x = row[2]
                try:
                    if 'append' in flags:
                        n = x.get_character_count(); done = x.insert_text(n, text, len(text.encode()))
                    else: done = x.set_text_contents(text)
                    x.grab_focus()
                except Exception: done = False
            if not done:   # no editable label: type into whatever has focus
                step_aside(); d = Device()
                try: done = d.text(text) or (paste(text) and (d.combo(['ctrl', 'v']) or True))
                finally: d.close()
            if done and 'submit' in flags:
                step_aside(); d = Device(); d.combo(['enter']); d.close()
            print(('done: Typing dispatched. Do not repeat typing without inspecting it.' if done else 'not_done: could not type there')); return 0 if done else 1
        print(f'not_done: {verb} is not available on this Linux build yet; use see/click/drag/press/type/type-after/scroll/scroll-to/menu.'); return 1
    except Exception as e:
        print(f'not_done: {type(e).__name__}: {e}'); return 1


if __name__ == '__main__':
    sys.exit(cli(sys.argv[1:]))
