"""Jev's browser agent on Linux, the counterpart of jev.py's web(): drive a page through its DOM (numbered controls,
click/fill by number), not the screen. Chromium-based browser over CDP (Playwright).

Two browsers, like the Mac:
  own  (default) a separate visible Brave/Chromium window with its own profile. The user watches it and can grab the mouse; `hide`
       minimizes it, `show` brings it back.
  yours  attach to the user's real browser — only if they started it with --remote-debugging-port (we never relaunch their browser
         or touch their profile without them doing it; `browser yours` prints how).

State (which browser, port, profile) lives in ~/.local/share/jev/browser.json. Needs playwright: pip install --target
~/.local/share/jev/py playwright (no browser download — we use the installed Brave/Chromium)."""
import re, json, os, shutil, subprocess, sys, time, urllib.request

HOME = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'jev')
STATE = os.path.join(HOME, 'browser.json')
PROFILE = os.path.join(HOME, 'browser-profile')   # Jev's own browser, never the user's
PORT = 9477
BROWSERS = ('brave', 'brave-browser', 'chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'microsoft-edge')
# what the model may act on; each gets a number in the read
TAG_JS = r"""() => {
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const sel = 'a[href], button, input:not([type=hidden]), textarea, select, [role=button], [role=link], [onclick], summary';
  const out = []; let i = 0;
  document.querySelectorAll(sel).forEach(e => {
    if (!vis(e)) return; e.setAttribute('data-jev-i', ++i);
    const label = (e.getAttribute('aria-label') || e.innerText || e.value || e.getAttribute('placeholder') || e.getAttribute('name') || e.getAttribute('title') || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    let kind = e.tagName.toLowerCase();
    if (kind === 'input') kind = (e.getAttribute('type') || 'text');
    out.push([i, kind, label]);
  });
  return out;
}"""


SENDS = re.compile(r'^(send\b|schedule send|send now|send invitation|invite|post\b|publish|reply all\b.*send)|\bsend\b.*(\(ctrl|⌘|enter)', re.I)


def binary():
    for b in BROWSERS:
        if shutil.which(b): return b
    return None


def load():
    try:
        with open(STATE) as f: return json.load(f)
    except (OSError, ValueError): return {}


def save(s):
    os.makedirs(HOME, mode=0o700, exist_ok=True)
    with open(os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f: json.dump(s, f)


def cdp_up(port):
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version', timeout=1); return True
    except OSError: return False


def ensure_own():
    """Jev's own browser running with CDP; launch it (visible) if needed. Returns the endpoint URL or an error string."""
    if cdp_up(PORT): return f'http://127.0.0.1:{PORT}'
    b = binary()
    if not b: return 'No Chromium-based browser found. Install Brave or Chromium (the AI can: sudo snap install brave).'
    profile = PROFILE
    if (shutil.which(b) or '').startswith('/snap'):   # a snap browser cannot write dot-folders in $HOME, and without its own profile it hands the page to the browser already open
        base = os.path.join(os.path.expanduser('~'), 'snap', os.path.basename(b).replace('-browser', ''), 'common')
        if os.path.isdir(base): profile = os.path.join(base, 'jev-profile')
    subprocess.Popen([b, f'--remote-debugging-port={PORT}', f'--user-data-dir={profile}', '--no-first-run',
                      '--no-default-browser-check', '--disable-sync', 'about:blank'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
    for _ in range(60):
        if cdp_up(PORT): return f'http://127.0.0.1:{PORT}'
        time.sleep(0.5)
    return 'The browser did not start in time.'


def endpoint():
    s = load()
    if s.get('which') == 'yours' and s.get('port') and cdp_up(s['port']): return f"http://127.0.0.1:{s['port']}", 'yours'
    url = ensure_own()
    return (url, 'own') if url.startswith('http') else (url, 'error')


def page(b):
    ctx = b.contexts[0] if b.contexts else b.new_context()
    return ctx.pages[-1] if ctx.pages else ctx.new_page()


def read_page(pg, note=''):
    try: controls = pg.evaluate(TAG_JS)
    except Exception: controls = []
    body = (pg.inner_text('body') if pg.query_selector('body') else '').strip()
    lines = [f"URL: {pg.url}", f"Title: {pg.title()}"]
    if note: lines.append(note)
    if body: lines.append('\nText:\n' + body[:4000])
    if controls:
        lines.append('\nControls (use the number):')
        lines += [f"  {i}. {kind}: {label}" or f"  {i}. {kind}" for i, kind, label in controls[:120]]
    return '\n'.join(lines)


def run(args):
    cmd = args[0] if args else 'read'
    if cmd == 'yours':
        return ('To let Jev drive your own browser, close it, then start it once like this (keeps your logins):\n'
                f'  {binary() or "brave"} --remote-debugging-port=9222\n'
                'then run: browser use-yours 9222. Until then Jev uses its own window.')
    if cmd == 'use-yours' and len(args) > 1 and args[1].isdigit():
        port = int(args[1])
        if not cdp_up(port): return f'No browser is listening on port {port}. Start it with --remote-debugging-port={port} first.'
        save({'which': 'yours', 'port': port}); return f'Jev will now drive your browser on port {port}. Use "browser use-own" to switch back.'
    if cmd == 'use-own':
        save({'which': 'own'}); return 'Jev will use its own browser window.'

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return 'The browser agent needs playwright: pip install --target ~/.local/share/jev/py playwright'
    url, which = endpoint()
    if which == 'error': return url
    with sync_playwright() as pw:
        try: b = pw.chromium.connect_over_cdp(url)
        except Exception as e: return f'Could not connect to the browser: {str(e)[:120]}'
        try:
            pg = page(b)
            if cmd in ('open', 'go', 'read') and len(args) > 1 and args[1].startswith(('http://', 'https://')):
                pg.goto(args[1], wait_until='commit', timeout=30000)
                try: pg.wait_for_load_state('domcontentloaded', timeout=15000)
                except Exception: pass
                return read_page(pg, f'(opened in Jev\'s own browser — you can watch it)' if which == 'own' else '(your browser)')
            if cmd in ('read', 'open', 'go'): return read_page(pg)
            if cmd == 'back': pg.go_back(wait_until='domcontentloaded', timeout=20000); return read_page(pg)
            if cmd in ('click', 'fill', 'type-after') or (cmd == 'type' and len(args) > 1):
                if cmd == 'type':   # type into the focused field
                    pg.keyboard.type(args[1]); return read_page(pg, f'Typed "{args[1][:40]}".')
                if cmd == 'type-after' and len(args) > 2:
                    pg.get_by_text(args[1], exact=False).first.click(timeout=5000); pg.keyboard.type(args[2])
                    return read_page(pg, f'Typed after "{args[1][:40]}".')
                n = args[1] if len(args) > 1 else ''
                if not n.isdigit(): return 'Say the control number from the read, e.g. browser click 3.'
                loc = pg.locator(f'[data-jev-i="{n}"]')
                if not loc.count(): return f'No control {n}. Read the page again; numbers change when the page changes.'
                if cmd == 'click':
                    label = (loc.first.get_attribute('aria-label') or loc.first.get_attribute('data-tooltip') or loc.first.inner_text() or '').strip()
                    if SENDS.search(label) and args[2:3] != ['--user-ok']:   # mail and invites go out only on the user's yes in chat
                        return (f'NOT DONE: control {n} ("{label[:40]}") sends or publishes. Show the user the draft and ask. Only after they say yes in chat '
                                f'run: browser click {n} --user-ok')
                    loc.first.click(timeout=8000)
                    try: pg.wait_for_load_state('domcontentloaded', timeout=8000)
                    except Exception: pass
                    return read_page(pg, f'Clicked {n}.')
                if cmd == 'fill':
                    if len(args) < 3: return 'Say the text: browser fill 3 "hello".'
                    loc.first.fill(args[2], timeout=8000); return read_page(pg, f'Filled {n}.')
            if cmd == 'hide':
                try: pg.evaluate("() => { try { window.resizeTo(0,0); } catch(e){} }")
                except Exception: pass
                for bn in BROWSERS:   # minimize the window the desktop way
                    if shutil.which('xdotool') and subprocess.run(['xdotool', 'search', '--class', bn, 'windowminimize', '%@'], capture_output=True).returncode == 0: break
                return 'Browser hidden (minimized). Use "browser show" to see it again.'
            if cmd == 'show':
                for bn in BROWSERS:
                    if shutil.which('xdotool') and subprocess.run(['xdotool', 'search', '--class', bn, 'windowactivate', '%@'], capture_output=True).returncode == 0: break
                return read_page(pg, '(shown)')
            if cmd == 'close':
                if which == 'own':
                    subprocess.run(['pkill', '-f', f'remote-debugging-port={PORT}'], capture_output=True)
                return 'Browser closed.' if which == 'own' else 'That is your browser; left open.'
            return ('browser open <url> | read | click <n> | fill <n> "text" | type "text" | type-after "anchor" "text" | back | '
                    'hide | show | close | yours | use-yours <port> | use-own')
        finally:
            b.close()


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        import tempfile
        PORT = 9478; PROFILE = tempfile.mkdtemp()   # module globals read via globals(); selftest only
        globals().update(PORT=PORT, PROFILE=PROFILE)
        assert ensure_own().startswith('http'), 'launch'
        print(run(['open', 'https://example.com']).split('\n', 3)[1])   # Title: Example Domain
        out = run(['read'])
        assert 'Controls' in out and 'example' in out.lower(), out
        subprocess.run(['pkill', '-f', f'remote-debugging-port={PORT}'], capture_output=True)
        print('browser ok')
    else:
        print(run(sys.argv[1:]))
