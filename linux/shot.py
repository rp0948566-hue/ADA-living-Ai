"""Whole-screen capture on Linux, the Screen Recording counterpart. Wayland blocks plain grabbers (scrot gives black),
so GNOME/KDE go through the desktop's Screenshot portal: the desktop asks the user once ("Allow Jev to take screenshots?")
and remembers it. X11 and wlroots fall back to the usual tools."""
import os, shutil, subprocess, urllib.parse


def portal(path, timeout=60):
    import gi
    from gi.repository import Gio, GLib
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    loop, out = GLib.MainLoop(), {}
    token = 'jev%d' % GLib.random_int()
    handle = f"/org/freedesktop/portal/desktop/request/{bus.get_unique_name()[1:].replace('.', '_')}/{token}"
    def response(_c, _s, _p, _i, _sig, params):
        code, res = params.unpack(); out.update(code=code, uri=res.get('uri', '')); loop.quit()
    sub = bus.signal_subscribe('org.freedesktop.portal.Desktop', 'org.freedesktop.portal.Request', 'Response', handle, None, 0, response)
    try:
        bus.call_sync('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop', 'org.freedesktop.portal.Screenshot', 'Screenshot',
                      GLib.Variant('(sa{sv})', ('', {'handle_token': GLib.Variant('s', token), 'interactive': GLib.Variant('b', False)})),
                      None, 0, -1, None)
        GLib.timeout_add_seconds(timeout, loop.quit); loop.run()   # the first time, the user's Allow click ends this
    finally: bus.signal_unsubscribe(sub)
    if out.get('code') != 0 or not out.get('uri', '').startswith('file://'): return False
    saved = urllib.parse.unquote(out['uri'][7:])
    shutil.move(saved, path)   # the portal saves into ~/Pictures; the shot is ours, not the user's
    return os.path.getsize(path) > 0


def capture(path):
    if os.environ.get('XDG_SESSION_TYPE') == 'wayland' or os.environ.get('WAYLAND_DISPLAY'):
        try:
            if portal(path): return True
        except Exception: pass
        tools = (['grim', path],)   # wlroots only; X grabbers are black under Wayland
    else:
        tools = (['gnome-screenshot', '-f', path], ['spectacle', '-b', '-n', '-o', path], ['scrot', '-o', path], ['import', '-window', 'root', path])
    for argv in tools:
        if shutil.which(argv[0]) and subprocess.run(argv, capture_output=True, timeout=20).returncode == 0 and os.path.getsize(path) > 0: return True
    return False


def text(path):
    """What the screen says, for a text-only model."""
    if not shutil.which('tesseract'): return ''
    return subprocess.run(['tesseract', path, '-', '--psm', '3'], capture_output=True, text=True, timeout=60).stdout
