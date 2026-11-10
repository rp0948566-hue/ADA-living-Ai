"""Tool schemas the model sees, and the dispatcher that runs them."""
import os, re, json
from . import osctl

OUT_MAX = int(os.environ.get('JEV_X_OUT_MAX', '1500'))   # small: local models have small contexts

# Catastrophic-only guard. Everything else is allowed (full access). JEV_X_UNSAFE=1 removes it.
_BAD = re.compile(r'(rm\s+-[a-z]*[rf][a-z]*\s+(/|~|\$HOME|/\*)(\s|$)|mkfs|dd\s+.*of=/dev/(sd|nvme|hd)|:\(\)\s*\{|>\s*/dev/(sd|nvme)|format\s+[a-z]:|Remove-Item\s+.*-Recurse.*[A-Z]:\\\s*$|shutdown|reboot|poweroff)', re.I)


def _t(name, desc, props=None, req=None):
    return {'type': 'function', 'function': {'name': name, 'description': desc,
            'parameters': {'type': 'object', 'properties': props or {}, 'required': req or []}}}


S, I = {'type': 'string'}, {'type': 'integer'}
SCHEMAS = [
    _t('shell', 'Run a shell command (bash on Linux/macOS, PowerShell on Windows). Full access.', {'cmd': S, 'timeout': I}, ['cmd']),
    _t('read_file', 'Read a text file.', {'path': S}, ['path']),
    _t('write_file', 'Write (overwrite) a text file.', {'path': S, 'content': S}, ['path', 'content']),
    _t('list_dir', 'List a directory.', {'path': S}, ['path']),
    _t('open', 'Open an app, file, folder or URL.', {'target': S}, ['target']),
    _t('windows', 'List open windows.'),
    _t('focus', 'Bring a window to the front by (part of) its title.', {'title': S}, ['title']),
    _t('click', 'Click at screen pixel x,y.', {'x': I, 'y': I, 'button': S, 'double': {'type': 'boolean'}}, ['x', 'y']),
    _t('type', 'Type text into the focused window.', {'text': S}, ['text']),
    _t('key', 'Press a key or combo, e.g. Return, ctrl+l, alt+F4.', {'combo': S}, ['combo']),
    _t('screenshot', 'Save a screenshot; returns the file path and screen size.'),
    _t('clipboard_get', 'Read the clipboard.'),
    _t('clipboard_set', 'Set the clipboard.', {'text': S}, ['text']),
    _t('notify', 'Show a desktop notification.', {'msg': S}, ['msg']),
    _t('done', 'Finish the task with a short final answer for the user.', {'answer': S}, ['answer']),
]


def clip(s, n=OUT_MAX):
    s = str(s)
    return s if len(s) <= n else s[:n // 2] + f'\n…[{len(s) - n} chars cut]…\n' + s[-n // 2:]


def _fmt(r):
    code, out = r
    return clip(out if code == 0 else f'[exit {code}] {out}') or 'ok'


def blocked(cmd):
    return None if os.environ.get('JEV_X_UNSAFE') == '1' else (_BAD.search(cmd) and 'blocked: catastrophic command (set JEV_X_UNSAFE=1 to allow)')


def call(name, a):
    """Run one tool; always returns a string (errors included) so the model can react."""
    try:
        if name == 'shell':
            b = blocked(a['cmd'])
            return b or _fmt(osctl.shell(a['cmd'], int(a.get('timeout') or 60)))
        if name == 'read_file':
            with open(os.path.expanduser(a['path']), errors='replace') as f: return clip(f.read(OUT_MAX * 4), OUT_MAX * 4)
        if name == 'write_file':
            p = os.path.expanduser(a['path']); os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
            with open(p, 'w') as f: f.write(a['content'])
            return f"wrote {len(a['content'])} chars to {p}"
        if name == 'list_dir':
            p = os.path.expanduser(a.get('path') or '.')
            return clip('\n'.join(sorted(e + ('/' if os.path.isdir(os.path.join(p, e)) else '') for e in os.listdir(p))))
        if name == 'open': return _fmt(osctl.open_target(a['target']))
        if name == 'windows': return clip(osctl.list_windows())
        if name == 'focus': return _fmt(osctl.focus_window(a['title']))
        if name == 'click': return _fmt(osctl.click(int(a['x']), int(a['y']), a.get('button') or 'left', bool(a.get('double'))))
        if name == 'type': return _fmt(osctl.type_text(a['text']))
        if name == 'key': return _fmt(osctl.key(a['combo']))
        if name == 'screenshot': return f'{osctl.screenshot()} (screen {osctl.screen_size()})'
        if name == 'clipboard_get': return clip(osctl.clipboard_get())
        if name == 'clipboard_set': return _fmt(osctl.clipboard_set(a['text']))
        if name == 'notify': return _fmt(osctl.notify(a['msg']))
        return f'unknown tool {name}'
    except Exception as e:   # tool failures go back to the model, never crash the loop
        return f'error: {type(e).__name__}: {e}'
