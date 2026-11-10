"""The Mac's other windows on Linux: Settings (SettingsWindow), Setup (Onboarding) and Agents. Each is one GTK window hosting its
ui/*.html page in WebKit2 with the same message-handler name and the same `{do: ...}` / `{action: ...}` messages as the Mac, so the
pages run unchanged. The brain (jev.py) does the work behind them, exactly as on the Mac."""
import json, os, subprocess, sys, threading

import gi
gi.require_version('Gtk', '3.0'); gi.require_version('WebKit2', '4.1')
from gi.repository import Gdk, GLib, Gtk, WebKit2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BRAIN = os.path.join(ROOT, 'jev.py')
KOFI = 'https://ko-fi.com/saarthr'
REPO = 'https://github.com/SaarthurR/atticus-mac'


def brain(args, extra=None, stdin=None):
    """py([...]) on the Mac: run the brain, return stdout."""
    env = dict(os.environ, **(extra or {}))
    r = subprocess.run(['sh', BRAIN, *args], capture_output=True, text=True, env=env, input=stdin, timeout=120)
    return r.stdout


def open_url(url):
    if url.split(':', 1)[0] in ('https', 'http', 'mailto'): Gtk.show_uri_on_window(None, url, Gdk.CURRENT_TIME)


class Page:
    """One window = one WebKit page + one message handler. send('fn', arg) calls ns.fn(arg) in the page (callJS)."""
    ns, handler, page, title, size, minimum = '', '', '', '', (780, 560), (700, 460)

    def __init__(self, app):
        self.app, self.win, self.web, self.loaded = app, None, None, False

    def build(self):
        w = Gtk.Window(title=self.title)
        w.set_default_size(*self.size); w.set_size_request(*self.minimum)
        w.set_icon_from_file(os.path.join(HERE, 'jev.png')); w.set_position(Gtk.WindowPosition.CENTER)
        w.connect('delete-event', lambda *_: (self.closed(), w.hide(), True)[2])   # closing hides it; reopening is instant, like the Mac's isReleasedWhenClosed = false
        cm = WebKit2.UserContentManager()
        cm.register_script_message_handler(self.handler)
        cm.connect(f'script-message-received::{self.handler}', self.message)
        cm.add_script(WebKit2.UserScript.new(   # page JS errors reach the host log, so a broken window is never silent
            f"window.addEventListener('error',e=>window.webkit.messageHandlers['{self.handler}'].postMessage({{jsError:(e.error&&e.error.stack)||(e.message+' @'+e.filename+':'+e.lineno)}}))",
            WebKit2.UserContentInjectedFrames.TOP_FRAME, WebKit2.UserScriptInjectionTime.START, None, None))
        web = WebKit2.WebView.new_with_user_content_manager(cm)
        web.connect('load-changed', lambda _w, ev: ev == WebKit2.LoadEvent.FINISHED and self.did_finish())
        web.connect('decide-policy', self.policy)
        with open(os.path.join(ROOT, 'ui', self.page)) as f: html = f.read()
        with open(os.path.join(ROOT, 'ui', 'orbs.js')) as f: orbs = f.read()
        web.load_html(html.replace('/*ORBS*/', orbs), None)
        w.add(web); self.win, self.web = w, web

    def policy(self, _w, decision, kind):   # links leave for the user's browser, never navigate the page
        if kind == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            uri = decision.get_navigation_action().get_request().get_uri()
            if uri and not uri.startswith(('about:', 'data:')): decision.ignore(); open_url(uri); return True
        return False

    def show(self):
        if not self.win: self.build()
        self.win.show_all(); self.win.present()

    def send(self, call, arg=None):   # safe from any thread
        args = [] if arg is None else [arg]
        GLib.idle_add(lambda: (self.web.evaluate_javascript(f"try{{{self.ns}.{call}(...{json.dumps(args)})}}catch(e){{window.webkit.messageHandlers['{self.handler}'].postMessage({{jsError:'{call}: '+e}})}}", -1, None, None, None, None, None) if self.web else None, False)[1])

    def message(self, _cm, result):
        try: b = json.loads(result.get_js_value().to_json(0))
        except (ValueError, TypeError, AttributeError): return
        if isinstance(b, dict) and 'jsError' in b: sys.stderr.write(f'[{self.title}] JS error: {b["jsError"]}\n')
        elif isinstance(b, dict): self.handle(b)

    def bg(self, fn, *a):   # off the main loop, like DispatchQueue.global().async
        threading.Thread(target=fn, args=a, daemon=True).start()

    def did_finish(self): self.loaded = True
    def closed(self): pass
    def handle(self, b): pass


class Settings(Page):
    ns, handler, page, title = 'st', 'st', 'settings.html', 'Jev Settings'
    size, minimum = (780, 560), (700, 460)

    def __init__(self, app, prefs):
        super().__init__(app); self.prefs, self.tab, self.timer = prefs, '', None

    def open(self, tab=''):
        self.tab = tab; self.show()
        if self.loaded: self.push(); self.refresh(); tab and self.send('tab', tab)
        if not self.timer: self.timer = GLib.timeout_add_seconds(2, self.tick)

    def tick(self):   # the live count beside Settings, microphones changed behind our back
        if not (self.win and self.win.get_visible()): self.timer = None; return False
        self.send('agents', {'count': len(self.app.agents.live()) if getattr(self.app, 'agents', None) else 0}); return True

    def did_finish(self):
        super().did_finish(); self.push(); self.refresh()
        self.bg(lambda: self.send('local', json.loads(brain(['--local-servers']) or '[]')))
        if self.tab: self.send('tab', self.tab); self.tab = ''

    def push(self):
        try:
            with open(os.path.join(os.path.dirname(self.prefs.path), 'routines.json')) as f: routines = json.load(f)
        except (OSError, ValueError): routines = []
        try: version = open(os.path.join(ROOT, 'VERSION')).read().strip()
        except OSError: version = ''
        self.send('dictation', {'history': [], 'words': self.prefs.d().get('dictateWords', []), 'stats': {'today': 0, 'words': 0, 'sessions': 0, 'minutes': 0}})
        self.send('whisper', {'models': [], 'server': False, 'installing': False})
        self.send('load', {'prefs': {'hotkeyLabel': '⌃⌥Space', 'dictateHotkeyLabel': '', **self.prefs.d()}, 'mics': mics(), 'version': version, 'update': 'Update with: git pull in your Jev folder.',
                           'managedUpdates': True, 'sharingUnavailable': False, 'hotkeyTaken': False, 'dictateHotkeyTaken': False,
                           'globeTaken': False, 'routines': routines})

    def refresh(self):   # usage, saved rules, plan: jev.py --state (off the main loop, it can run Claude Code)
        def run():
            s = brain(['--state'])
            if s.startswith('{'): self.send('state', json.loads(s))
        self.bg(run)

    def helper(self, args):
        self.bg(lambda: (brain(args), GLib.idle_add(lambda: (self.refresh(), False)[1])))

    def notice(self, text): self.send('notice', {'text': text})

    def apply(self, k, v):   # one setting changed, from this window or by voice
        self.prefs.set(k, v)
        a = self.app
        if k in ('routing', 'model', 'client', 'apiBase', 'apiKey', 'apiModel'): a.unwarm()   # a new key must not reuse a worker started with the old one
        if k == 'safe': a.js('mode', v is True)
        if k == 'speak' and v is False: a.shush()
        if k == 'paused' and v is True: a.close(False)
        if k == 'wakeWord' and getattr(a, 'wake', None): a.wake.set(v is True)
        if k == 'monitor' and v is False: self.notice('Overload alerts turn off after Jev restarts.')

    def handle(self, b):
        what = b.get('do')
        g = b.get
        if what == 'set' and isinstance(g('k'), str) and 'v' in b: self.apply(g('k'), g('v'))
        elif what == 'feedbackPreview':
            def run():
                out = brain(['--feedback'], stdin=json.dumps({'include': bool(g('include')), 'text': g('text') or '', 'version': 'linux'}))
                try: r = json.loads(out)
                except ValueError: r = {'error': 'Could not prepare feedback. Try again.'}
                r['revision'] = g('revision') or 0; self.url = r.get('url'); self.send('feedback', r)
            self.bg(run)
        elif what == 'feedbackInvalidate': self.url = None
        elif what == 'feedbackOpen' and getattr(self, 'url', None): open_url(self.url)
        elif what == 'dictationWord':
            words = [w for w in self.prefs.d().get('dictateWords', []) if w != g('old')]
            if isinstance(g('word'), str) and 0 < len(g('word')) <= 80 and len(words) < 500: self.prefs.set('dictateWords', words + [g('word')]); self.push()
            else: self.notice('Couldn’t save that word. Use 1–80 characters, up to 500 words.')
        elif what == 'dictationWordDelete': self.prefs.set('dictateWords', [w for w in self.prefs.d().get('dictateWords', []) if w != g('word')]); self.push()
        elif what in ('dictationDelete', 'dictationClear', 'meetings', 'meetingOpen', 'meetingDelete', 'meetingExport', 'meetingCopy',
                      'meetingPrepPrompt', 'meetingPrepOpen', 'meetingDemo', 'whisperDownload', 'whisperCancel', 'whisperDelete', 'whisperInstall'):
            if what == 'meetings': self.send('meetings', {'meetings': [], 'query': g('query') or ''})
            else: self.notice('That part of Jev is not on Linux yet.')
        elif what in ('record', 'recordDictate', 'cancelRecord', 'clearDictate', 'resetHotkey', 'globeKey'):
            self.notice('Set the shortcut in your desktop: Settings → Keyboard → Shortcuts → add a custom shortcut running “jev --toggle”.')
            self.send('rec', ''); self.push()
        elif what == 'unlearn' and isinstance(g('say'), str): self.helper(['--unlearn', g('say')])
        elif what == 'checkUpdate': self.notice('Update with: git pull in your Jev folder.')
        elif what == 'agents': self.app.agents.open()
        elif what == 'routineRemove' and isinstance(g('id'), str): self.bg(lambda: (brain(['--routine', 'remove', g('id')]), GLib.idle_add(lambda: (self.push(), False)[1])))
        elif what == 'github': open_url(REPO)
        elif what == 'kofi': open_url(KOFI)
        elif what == 'preview' and isinstance(g('sound'), str):
            import cues; cues.play(g('sound'), float(self.prefs.get('volume') or 0.16))
        elif what == 'setup': self.app.onboarding.open()
        elif what == 'models':
            base, key = self.prefs.get('apiBase') or '', self.prefs.get('apiKey') or ''
            def run():
                try: lst = json.loads(brain(['--models'], {'JEV_PROBE_BASE': base, 'JEV_PROBE_KEY': key}))
                except ValueError: lst = []
                self.send('models', {'base': base, 'key': key, 'list': lst})
            self.bg(run)
        elif what == 'localServers': self.bg(lambda: self.send('local', json.loads(brain(['--local-servers']) or '[]')))
        elif what == 'copy' and isinstance(g('text'), str):
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(g('text'), -1); self.notice('Copied.')
        elif what == 'openLog': open_url('file://' + os.path.join(os.path.dirname(self.prefs.path), 'log.jsonl'))
        elif what == 'clearRecent':
            try: os.remove(os.path.join(os.path.dirname(self.prefs.path), 'recent.jsonl'))
            except OSError: pass
            self.notice('Conversation forgotten.')
        elif what == 'profileImport': self.notice('Importing contacts and mail is Mac only.')
        elif what == 'me': self.me(b)
        elif what in ('forget', 'remember') and isinstance(g('line'), str): self.helper(['--' + what, g('line')])
        elif what == 'rule' and isinstance(g('old'), str) and isinstance(g('text'), str): self.helper(['--rule', g('old'), g('text')])
        elif what == 'apps': self.send('apps', [])
        elif what in ('allow', 'stopAllow'): self.send('allowDone', [])
        elif what in ('grant', 'enableAll', 'connectors'): self.app.onboarding.handle(b)
        elif what == 'quit': Gtk.main_quit()

    def me(self, b):   # the "About you" memory: --me add|set|drop|forget-source
        g, a = b.get, b.get('action')
        args = ['--me', a]
        if a == 'add' and isinstance(g('category'), str) and isinstance(g('text'), str): args += [g('category'), g('text')]
        elif a == 'set' and isinstance(g('id'), str) and isinstance(g('text'), str): args += [g('id'), g('text')]
        elif a == 'drop' and isinstance(g('id'), str): args.append(g('id'))
        elif a == 'forget-source' and isinstance(g('source'), str): args.append(g('source'))
        else: return
        self.helper(args)


def mics():   # microphoneChoices(): [{uid, name}] from PipeWire/Pulse
    out = []
    try:
        r = subprocess.run(['pactl', '-f', 'json', 'list', 'sources'], capture_output=True, text=True, timeout=5)
        out = [{'uid': s['name'], 'name': s.get('description') or s['name']} for s in json.loads(r.stdout) if not s['name'].endswith('.monitor')]
    except (OSError, ValueError, subprocess.SubprocessError, KeyError): pass
    return out


# ---------------------------------------------------------------- Setup (Onboarding)
class Onboarding(Page):
    ns, handler, page, title = 'ob', 'ob', 'onboarding.html', 'Jev Setup'
    size, minimum = (640, 640), (640, 640)

    def __init__(self, app, prefs):
        super().__init__(app); self.prefs, self.timer, self.tick_n, self.checking, self.shown = prefs, None, 0, False, False

    def open(self, automatic=False):
        if automatic and self.shown: return
        self.shown = True; self.show()
        if not self.timer: self.timer = GLib.timeout_add(1000, self.tick)

    def closed(self):
        self.timer = None

    def tick(self):   # permissions 1×/s, the AI client every 5 s (it starts Claude Code, too slow for every second)
        if not (self.win and self.win.get_visible()): self.timer = None; return False
        self.tick_n += 1; self.push()
        if self.tick_n % 5 == 1: self.check_plan()
        return True

    def did_finish(self): super().did_finish(); self.push(); self.check_plan()

    @staticmethod
    def perms(app=None, prefs=None):   # what Jev can do here; Linux asks the user for none of these, so most are simply on
        p = prefs.d() if prefs else {}
        return {'mic': bool(mics()), 'speech': bool(getattr(app, 'ear_ready', True)), 'ax': os.access('/dev/uinput', os.W_OK),
                'screen': bool(p.get('screenOK')), 'auto': True, 'calendar': True, 'tools': bool(p.get('agentUserTools')), 'chrome': True}

    def push(self):
        s = self.perms(self.app, self.prefs); p = self.prefs
        self.send('set', s); self.send('mode', p.get('talkMode') == 'toggle')
        self.send('prefs', {'meeting': bool(p.get('meeting')), 'draw': bool(p.get('draw')), 'routing': p.get('routing') or 'cheapest', 'hotkeyLabel': p.get('hotkeyLabel') or '',
                            'safe': p.get('safe') is not False, 'dictateMode': p.get('dictateMode') or 'verbatim', 'dictateHotkeyLabel': p.get('dictateHotkeyLabel') or '', 'globeTaken': False})
        self.send('server', {'apiBase': p.get('apiBase') or '', 'apiModel': p.get('apiModel') or ''})

    def check_plan(self):   # Claude Code installed, signed in, paid plan? (jev.py --check)
        if self.checking: return
        self.checking = True
        def run():
            try: c = json.loads(brain(['--check']))
            except ValueError: c = {'ok': False, 'need': 'install', 'text': 'Could not run Jev’s helper (python3 missing?).'}
            self.checking = False; self.send('plan', c)
        self.bg(run)

    def fix_plan(self):   # the plan row's button: install the AI client or sign in, in a terminal window the user can watch
        def run():
            try: c = json.loads(brain(['--check']))
            except ValueError: c = {}
            need, client = c.get('need') or '', c.get('client') or 'claude'
            if not need and c.get('ok') is False: return GLib.idle_add(lambda: (self.app.settings.open(), False)[1])
            if need == 'upgrade': return open_url('https://claude.ai/upgrade')
            if client == 'devin': cmd = 'curl -fsSL https://cli.devin.ai/install.sh | bash && devin auth login' if need == 'install' else 'devin auth login'
            elif client == 'pi': cmd = "curl -fsSL https://pi.dev/install.sh | sh && echo 'In Pi, use /login or /model to choose your provider.' && pi" if need == 'install' else 'pi'
            else: cmd = 'curl -fsSL https://claude.ai/install.sh | bash' + ('' if client == 'server' else ' && ~/.local/bin/claude auth login') if need == 'install' else 'claude auth login'
            script = f'export PATH="$HOME/.local/bin:$PATH"; echo "Jev: setting up {client}"; {cmd}; echo; echo "Done. You can close this window."; read -r -p "" _'
            for term in (['gnome-terminal', '--'], ['kgx', '-e'], ['konsole', '-e'], ['xfce4-terminal', '-x'], ['x-terminal-emulator', '-e']):
                try: subprocess.Popen([*term, 'bash', '-c', script]); break
                except OSError: continue
            self.check_plan()
        self.bg(run)

    def grant(self, i):
        p = self.prefs
        if i == 'claude': self.fix_plan()
        elif i == 'connectors': open_url('https://claude.ai/settings/connectors')
        elif i == 'tools': self.app.settings.apply('agentUserTools', True)
        elif i == 'screen':   # the desktop's own "Allow Jev to take screenshots?" box, once
            def run():
                import shot
                ok = shot.capture(os.path.join(os.environ.get('XDG_RUNTIME_DIR') or '/tmp', 'jev-perm.png'))
                if ok: p.set('screenOK', True)
            self.bg(run)
        elif i == 'ax':
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'toolkit-accessibility', 'true'], capture_output=True)   # AT-SPI: the window reader
            if not os.access('/dev/uinput', os.W_OK): self.app.settings.notice('Keys and clicks need access to /dev/uinput: run linux/install.sh once, then log out and in.')
        self.push()

    def allow(self, need, app=''):   # an agent's setup card
        self.grant({'accessibility': 'ax', 'screen': 'screen', 'microphone': 'mic', 'calendar': 'calendar'}.get(need, ''))

    def granted(self, need, app=''):
        return self.perms(self.app, self.prefs).get({'accessibility': 'ax', 'screen': 'screen', 'microphone': 'mic', 'calendar': 'calendar', 'automation': 'auto'}.get(need, ''), False)

    def enable_all(self, connected):   # Jev's own switches at once; on Linux nothing else needs a settings pane
        self.grant('tools'); self.grant('ax'); self.grant('screen')
        if not connected: self.grant('connectors')
        self.app.settings.notice('Everything is on.')

    def handle(self, b):
        g, what = b.get, b.get('do')
        if what == 'done': self.prefs.set('onboarded', True); self.win.hide(); self.closed()
        elif what == 'kofi': open_url(KOFI)
        elif what == 'feedback': self.app.settings.open('feedback')
        elif what == 'enableAll': self.enable_all(g('connected') == 'true')
        elif what == 'provider' and g('client') in ('claude', 'devin', 'pi'):
            self.app.settings.apply('client', g('client'))
            for k in ('apiBase', 'apiKey', 'apiModel'):
                if k in b: self.app.settings.apply(k, g(k))
            self.app.settings.push(); self.check_plan()
        elif what == 'probe' and isinstance(g('base'), str):
            base, key = g('base'), g('key') or ''
            if not key and base == self.prefs.get('apiBase'): key = self.prefs.get('apiKey') or ''
            def run():
                try: lst = json.loads(brain(['--models'], {'JEV_PROBE_BASE': base, 'JEV_PROBE_KEY': key}))
                except ValueError: lst = []
                self.send('models', lst)
            self.bg(run)
        elif what == 'localServers': self.bg(lambda: self.send('local', json.loads(brain(['--local-servers']) or '[]')))
        elif what == 'connectors':
            def run():
                try: c = json.loads(brain(['--connectors']))
                except ValueError: c = {'connected': [], 'signin': []}
                self.send('connectors', c)
            self.bg(run)
        elif what == 'set' and isinstance(g('k'), str):
            choices = {'routing': ('cheapest', 'balanced', 'capable'), 'dictateMode': ('verbatim', 'cleanup')}
            if g('k') in ('meeting', 'draw', 'improve'): self.app.settings.apply(g('k'), g('v') == 'true')
            elif g('v') in choices.get(g('k'), ()): self.app.settings.apply(g('k'), g('v'))
            else: return
            self.app.settings.push(); self.push()
        elif what in ('recordDictate', 'cancelRecord', 'clearDictate', 'globeKey'): self.app.settings.handle({'do': what}); self.push()
        elif isinstance(g('id'), str): self.grant(g('id'))


# ---------------------------------------------------------------- Agents: a shelf of chips + the Agents view
class MiniScreen:
    """The Mac streams the agent's window live (ScreenCaptureKit). Linux shows what the agent is on (app and window) as text:
    a live picture of another app's window needs a screen-share prompt on Wayland, so it is not ported."""
    def __init__(self, publish): self.publish, self.target = publish, None

    def receive(self, target): self.target = target; self.publish({**target, 'shown': True, 'live': False})
    def reset(self): self.target = None


class Agents:
    LIVE = ('running', 'needs-you', 'waiting-screen', 'queued')

    def __init__(self, app, prefs):
        self.app, self.prefs = app, prefs
        self.proc, self.restarts, self.rows, self.offers, self.named = None, 0, {}, {}, []
        self.shelf = self.view = self.shelf_web = self.view_web = None
        self.ready, self.dismissed, self.lingering, self.hovered, self.last_box, self.selected = set(), set(prefs.d().get('agentDismissed') or []), False, '', None, ''
        self.mini = MiniScreen(lambda v: self.js(self.surface_of_mini, 'mini', v)); self.surface_of_mini = 'shelf'
        GLib.idle_add(lambda: (self.start(), False)[1])   # restore accepted work even if the user never opens Agents
        GLib.timeout_add(500, self.tick)

    # -- the supervisor: `jev.py --agents`, one JSON object per line each way
    def start(self):
        if self.proc: return
        try:
            p = subprocess.Popen(['sh', BRAIN, '--agents'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1, start_new_session=True)
        except OSError: return self.retry()
        self.proc = p
        def read():
            for line in p.stdout:
                try: ev = json.loads(line)
                except ValueError: continue
                GLib.idle_add(lambda ev=ev: (self.receive(ev), False)[1])
            p.wait()
            GLib.idle_add(lambda: (self.exited(p), False)[1])
        threading.Thread(target=read, daemon=True).start()
        self.send({'action': 'list'})

    def exited(self, p):
        if self.proc is not p: return
        self.proc, self.last_box = None, None; self.retry()

    def retry(self):
        self.restarts += 1; GLib.timeout_add_seconds(min(60, 2 ** self.restarts), lambda: (self.start(), False)[1])

    def send(self, data):
        self.start()
        try: self.proc.stdin.write(json.dumps(data) + '\n'); self.proc.stdin.flush()
        except (OSError, AttributeError, ValueError): self.proc and self.proc.terminate()

    def stop_all(self):   # Pause: queued rows stop first, so stopping a running one cannot start them
        for r in sorted((r for r in self.rows.values() if r.get('status') in self.LIVE), key=lambda r: r.get('status') != 'queued'):
            self.send({'action': 'stop', 'id': r['id']})

    # -- derived state
    def sorted(self): return sorted(self.rows.values(), key=lambda r: r.get('created') or 0, reverse=True)
    def live(self): return [r for r in self.rows.values() if r.get('status') == 'running']
    def badge(self): return {'count': len(self.live()), 'attention': any(r.get('status') == 'needs-you' for r in self.rows.values())}
    def quiet(self): return bool(self.prefs.get('agentsHidden'))   # screen sharing is not detectable here; the user's own switch

    @staticmethod
    def lingers(r):
        import time
        return r.get('status') in ('done', 'failed') and time.time() - max(r.get('ended') or 0, r.get('seenAt') or 0) < 600

    def has_chips(self):
        return self.lingering or any(r.get('status') in self.LIVE and r['id'] not in self.dismissed for r in self.rows.values())

    # -- windows
    def make(self, surface):
        w = Gtk.Window()
        cm = WebKit2.UserContentManager(); cm.register_script_message_handler('agents')
        cm.connect('script-message-received::agents', lambda _c, res: self.message(res, surface))
        cm.add_script(WebKit2.UserScript.new("window.addEventListener('error',e=>window.webkit.messageHandlers.agents.postMessage({jsError:(e.error&&e.error.stack)||(e.message+' @'+e.filename+':'+e.lineno)}))",
            WebKit2.UserContentInjectedFrames.TOP_FRAME, WebKit2.UserScriptInjectionTime.START, None, None))   # a broken Agents page must not be silent
        web = WebKit2.WebView.new_with_user_content_manager(cm)
        with open(os.path.join(ROOT, 'ui', 'agents.html')) as f: html = f.read()
        with open(os.path.join(ROOT, 'ui', 'orbs.js')) as f: orbs = f.read()
        web.load_html(html.replace('/*ORBS*/', orbs), None)
        web.connect('decide-policy', lambda w, d, k: Page.policy(None, w, d, k))   # same link rule as the other windows: the page's own load must not be blocked (it was: a white window)
        if surface == 'shelf':
            w.set_decorated(False); w.set_keep_above(True); w.set_skip_taskbar_hint(True); w.set_skip_pager_hint(True); w.set_accept_focus(False)
            w.set_type_hint(Gdk.WindowTypeHint.UTILITY); w.stick(); w.set_default_size(260, 52)
            vis = w.get_screen().get_rgba_visual()
            if vis: w.set_visual(vis)
            w.set_app_paintable(True); web.set_background_color(Gdk.RGBA(0, 0, 0, 0))
        else:
            web.set_background_color(Gdk.RGBA(.06, .06, .07, 1))   # the page body is transparent (the Mac window is vibrancy); GTK would show white
            w.set_title('Agents'); w.set_default_size(760, 580); w.set_size_request(520, 340); w.set_position(Gtk.WindowPosition.CENTER)
            w.connect('delete-event', lambda *_: (self.close_view(), w.hide(), True)[2])
            w.connect('key-press-event', lambda _w, e: e.keyval == Gdk.KEY_Escape and (self.close_view(), w.hide(), True)[2])
        w.set_icon_from_file(os.path.join(HERE, 'jev.png')); w.add(web)
        return w, web

    def ensure_shelf(self, preload=False):
        if self.shelf or not (preload or any(r.get('status') in self.LIVE for r in self.rows.values())): return
        self.shelf, self.shelf_web = self.make('shelf'); self.place_shelf()
        if not preload: self.shelf.show_all()

    def place_shelf(self):
        d = Gdk.Display.get_default(); seat = d.get_default_seat(); _, x, y = seat.get_pointer().get_position()
        m = d.get_monitor_at_point(x, y) or d.get_primary_monitor(); g = m.get_workarea()
        w, h = self.shelf.get_size(); saved = (self.prefs.get('agentFrames') or {}).get('shelf')
        self.shelf.move(*(saved if saved else (g.x + g.width - w - 12, g.y + 8)))

    def open_view(self, i=''):
        self.start()
        if not self.view: self.view, self.view_web = self.make('view')
        self.js('view', 'visible', True); self.view.show_all(); self.view.present()
        i = i or next((r['id'] for r in self.sorted() if r.get('status') in self.LIVE), '')
        if i: self.selected = i; self.js('view', 'select', i); self.preview(i, 'view')
        self.js('view', 'list', self.sorted())

    open = open_view

    def close_view(self):
        self.end_preview(); self.js('view', 'visible', False)
        if self.has_chips() and not self.quiet() and self.shelf: self.shelf.show_all(); self.js('shelf', 'resume')

    def js(self, surface, call, value=None):
        web = self.view_web if surface == 'view' else self.shelf_web
        if web and surface in self.ready:
            args = [{} if value is None else value]
            GLib.idle_add(lambda: (web.evaluate_javascript(f'agents.{call}(...{json.dumps(args)})', -1, None, None, None, None, None), False)[1])

    def preview(self, i, surface, target=None):
        self.hovered, self.surface_of_mini = i, surface
        row = self.rows.get(i) or {}
        t = target or row.get('target')
        if i and t: self.mini.receive(t)
        else: self.end_preview()

    def end_preview(self): self.hovered = ''; self.mini.reset()

    # -- page messages
    def message(self, res, surface):
        try: b = json.loads(res.get_js_value().to_json(0))
        except (ValueError, TypeError, AttributeError): return
        if isinstance(b, dict) and 'jsError' in b: sys.stderr.write(f'[agents {surface}] JS error: {b["jsError"]}\n')
        if not isinstance(b, dict) or not isinstance(b.get('action'), str): return
        a, i = b['action'], b.get('id') if isinstance(b.get('id'), str) else ''
        if a == 'ready':
            self.ready.add(surface); self.js(surface, 'mode', surface)
            self.js(surface, 'prefs', {'dismissed': list(self.dismissed), 'stack': self.prefs.get('agentStack') or '', 'tab': self.prefs.get('agentTab') or ''})
            self.js(surface, 'list', self.sorted())
            if surface == 'shelf': self.js('shelf', 'visible', bool(self.shelf and self.shelf.get_visible()))
        elif a == 'size' and surface == 'shelf' and self.shelf and isinstance(b.get('h'), (int, float)):
            w, _ = self.shelf.get_size(); self.shelf.resize(w, int(max(52, b['h'])))
        elif a == 'drag' and surface == 'shelf' and self.shelf:
            d = Gdk.Display.get_default(); _, x, y = d.get_default_seat().get_pointer().get_position()
            self.shelf.begin_move_drag(1, x, y, Gdk.CURRENT_TIME)
            GLib.timeout_add(1500, self.remember)
        elif a == 'dismiss':
            if (self.rows.get(i) or {}).get('status') == 'done': self.send({'action': 'seen', 'id': i})
            self.dismissed.add(i); self.prefs.set('agentDismissed', sorted(self.dismissed))
            if self.hovered == i and self.surface_of_mini == 'shelf': self.end_preview()
        elif a == 'stack': self.prefs.set('agentStack', b.get('value') or '')
        elif a == 'tab': self.prefs.set('agentTab', 'chats' if b.get('value') == 'chats' else '')
        elif a in ('view', 'show'):
            self.open_view(i)
            if (self.rows.get(i) or {}).get('status') == 'done': self.send({'action': 'seen', 'id': i})
        elif a == 'lingering': self.lingering = b.get('value') is True; self.tick()
        elif a == 'close' and surface == 'view' and self.view: self.view.hide(); self.close_view()
        elif a == 'hover':
            if not i: self.end_preview()
            elif self.hovered != i or self.surface_of_mini != surface: self.preview(i, surface)
        elif a == 'miniRect': pass   # the Mac lays its live window over this rect; here the page shows the window's name
        elif a == 'attention':
            if not self.quiet() and self.shelf: self.shelf.show_all()
        elif a in ('open', 'reveal'):
            self.open_made(i, b.get('target') if isinstance(b.get('target'), str) else None, a == 'reveal')
            if a == 'open' and (self.rows.get(i) or {}).get('status') == 'done': self.send({'action': 'seen', 'id': i})
        elif a == 'connect': open_url('https://claude.ai/settings/connectors')
        elif a == 'answer':
            self.send(b); q = (self.rows.get(i) or {}).get('question') or {}
            if b.get('answer') == 'y' and q.get('need') and q.get('_a') == b.get('question'): self.allow(i, q)
        else: self.send(b)

    def open_made(self, i, target=None, reveal=False):   # what the agent made (link or file), else its view
        row = self.rows.get(i)
        if not row:
            if target and target.split(':', 1)[0] in ('http', 'https'): open_url(target)
            return
        raw = target or next((m.get('url') for m in row.get('made') or [] if m.get('url')), None) or next(iter(row.get('links') or []), None)
        if raw:
            if raw.split(':', 1)[0] in ('http', 'https'): return open_url(raw)
            path = raw[7:] if raw.startswith('file://') else os.path.expanduser(raw)
            path = os.path.normpath(path if path.startswith('/') else os.path.join(row.get('directory') or '', path))
            if os.path.exists(path): return open_url('file://' + (os.path.dirname(path) if reveal else path))
        if reveal and row.get('directory'): return open_url('file://' + row['directory'])
        self.open_view(i)

    def remember(self):
        if self.shelf:
            x, y = self.shelf.get_position(); frames = self.prefs.get('agentFrames') or {}; frames['shelf'] = [x, y]; self.prefs.set('agentFrames', frames)
        return False

    # -- events from the supervisor
    def allow(self, i, q):   # Allow on an agent's setup card
        need, app, ask = q.get('need') or '', q.get('app') or '', q.get('_a') or ''
        if need == 'page-js': return self.prefs.set('pageJS', True)
        if need == 'connector': return open_url('https://claude.ai/settings/connectors')
        self.app.onboarding.allow(need, app)
        tries = [0]
        def poll():
            tries[0] += 1
            if tries[0] > 900 or ((self.rows.get(i) or {}).get('question') or {}).get('_a') != ask: return False
            if self.app.onboarding.granted(need, app): self.send({'action': 'granted', 'id': i}); return False
            return True
        GLib.timeout_add_seconds(1, poll)

    def receive(self, ev):
        kind = ev.get('event') or ''
        if kind == 'list' and isinstance(ev.get('agents'), list):
            self.restarts = 0; self.rows = {r['id']: r for r in ev['agents'] if isinstance(r, dict) and 'id' in r}
            self.named = ev.get('named') or []
            if self.hovered and self.hovered not in self.rows: self.end_preview()
            if any(self.lingers(r) for r in self.rows.values()): self.ensure_shelf(True)
            for s in ('shelf', 'view'): self.js(s, 'list', self.sorted())
            self.js('view', 'named', self.named)
        elif kind == 'chats': self.js('view', 'chats', ev.get('chats') or [])
        elif kind == 'named':
            self.named = ev.get('named') or []; self.js('view', 'named', self.named)
            if ev.get('reply') is not None: self.js('view', 'namedReply', ev['reply'])
        row = ev.get('agent')
        if isinstance(row, dict) and row.get('id'):
            i, q = row['id'], lambda r: ((r or {}).get('question') or {}).get('_a')
            asks = kind == 'state' and row.get('status') == 'needs-you' and q(row) is not None and q(row) != q(self.rows.get(i))
            finished = (self.rows.get(i) or {}).get('status') in self.LIVE and self.lingers(row)
            self.rows[i] = row
            if asks and not self.quiet():
                import cues; cues.play('Ping', float(self.prefs.get('volume') or 0.16))   # a new question from a working agent
            if row.get('status') == 'needs-you' or finished: self.dismissed.discard(i)
            if kind == 'state':
                self.ensure_shelf(self.lingers(row)); self.js('shelf', 'state', row); self.js('view', 'state', row)
                if self.hovered == i and row.get('target'): self.preview(i, self.surface_of_mini, row['target'])
            elif kind == 'offer':
                self.offers[i] = row if ev.get('followup') is True else {}; self.accept(i)
            elif kind == 'done':
                if self.quiet() or row.get('routine') is not None: self.notify(row); self.send({'action': 'notified', 'id': i})
            elif kind == 'ping' and row.get('status') == 'done':
                if self.quiet():
                    if row.get('notified') is not True: self.notify(row); self.send({'action': 'notified', 'id': i})
                else: self.expand(i)
            elif kind == 'steered':
                self.dismissed.discard(i); self.ensure_shelf(); self.js('shelf', 'state', row); self.js('view', 'state', row); self.js('shelf', 'visible', True)
                if not self.quiet() and self.shelf: self.shelf.show_all()
                self.app.js('agentSteered', row)
        elif kind == 'text': self.js('view', 'text', ev)
        self.app.js('agentCount', self.badge()); self.tick()

    def prepare(self, brief):   # a hand-off from the box (⤴): the supervisor answers with an offer, then accept() starts it
        self.ensure_shelf(True); self.send({'action': 'prepare', 'brief': brief})

    def accept(self, i):
        if self.prefs.get('paused') is True: return
        row = self.rows.get(i)
        if not row: return
        full = sum(1 for r in self.rows.values() if r.get('status') in ('running', 'needs-you', 'waiting-screen') and r.get('ended') is None) >= 3
        row['status'], row['step'] = ('queued', 'Queued') if full else ('running', 'Starting…')
        self.ensure_shelf(); self.place_shelf(); self.dismissed.discard(i)
        self.js('shelf', 'arrive', i); self.js('shelf', 'state', row); self.js('shelf', 'visible', True); self.app.js('agentCount', self.badge())
        GLib.timeout_add(150, lambda: (self.js('shelf', 'land', i), False)[1])   # the swim animation is not ported: the chip lands at once
        if not self.quiet() and self.shelf: self.shelf.show_all()
        offer = self.offers.pop(i, {})
        text = (offer.get('brief') + '\nKnown context (data):\n' + (offer.get('context') or '')) if offer.get('brief') else None
        self.send({'action': 'start', 'id': i, 'text': text})
        self.app.pinned = False; self.app.js('agentStarted', row)
        if not self.quiet():
            import cues; cues.play('Blow', float(self.prefs.get('volume') or 0.16))

    def notify(self, row):
        subprocess.Popen(['sh', BRAIN, '--agent-notify', row.get('summary') or row.get('title') or 'Your task is done'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def expand(self, i):   # a finish shows on its own chip, opened with its result
        self.dismissed.discard(i); self.ensure_shelf(True); self.js('shelf', 'expand', i)
        import cues; cues.play('Hero', min(1, float(self.prefs.get('volume') or 0.16) * 2))

    def show(self, i):   # a main ask showed an agent (▤): a done one's card in the box; one working or failed opens in the view
        row = self.rows.get(i)
        if not row: return
        if row.get('status') != 'done': return self.open_view(i)
        self.app.show(); self.app.pinned = True; self.app.js('agentDone', row)

    def tick(self):   # the box's state goes to the supervisor (it holds pings while the box is busy); the shelf shows only when there is something on it
        if not self.rows:
            if self.shelf: self.shelf.hide()
            return True
        a = self.app
        box = {'action': 'box', 'busy': bool(a.busy), 'typing': bool(a.composing), 'listening': bool(a.listening), 'quiet': self.quiet()}
        if box != self.last_box: self.last_box = box; self.send(box)
        if self.shelf:
            if self.quiet() or not self.has_chips():
                if self.shelf.get_visible(): self.shelf.hide(); self.js('shelf', 'visible', False)
            elif not self.shelf.get_visible() and any(r.get('status') in self.LIVE for r in self.rows.values()): self.shelf.show_all()
        return True
