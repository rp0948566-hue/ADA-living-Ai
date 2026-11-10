#!/usr/bin/env python3
"""Jev for Linux: the box. The Linux counterpart of Jev.swift's App class (~2229-4130).
Same page (ui/ui.html with orbs.js inlined), same bridge (webkit.messageHandlers.h/.c in, ui.<fn>(...json) out),
same worker (jev.py --wait via worker.Worker) and the same stdout line protocol as spawn().
`host.py` starts it; `host.py --toggle` is the hotkey (a GNOME custom shortcut runs it)."""
import ctypes, json, os, re, socket, subprocess, sys, threading, time

os.environ.setdefault('GDK_BACKEND', 'x11')   # XWayland: GNOME's Wayland lets no app place or raise its own window
import gi
gi.require_version('Gtk', '3.0'); gi.require_version('Gdk', '3.0'); gi.require_version('WebKit2', '4.1')
from gi.repository import Gdk, GLib, Gtk, WebKit2

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from worker import Worker
import cues, panes, proactive, voice, wm

SOCK = os.path.join(os.environ.get('XDG_RUNTIME_DIR') or '/tmp', f'jev-{os.getuid()}.sock')


class Prefs:   # Jev.swift enum Prefs: the same settings.json the brain reads, with the same defaults for the keys the box uses
    path = os.path.join(os.environ.get('JEV_DIR') or os.path.expanduser('~/.config/jev'), 'settings.json')
    defaults = {'corner': 'top-left', 'linger': 'normal', 'client': 'claude', 'safe': True, 'tips': True, 'paused': False,
                'input': 'voice', 'routing': 'cheapest', 'apiBase': '', 'apiModel': '', 'boxW': 500, 'boxH': 420, 'autoCopy': False, 'speak': False, 'privateMode': False, 'readOnly': False, 'kidMode': False, 'micOff': False, 'ownerVoice': False, 'translateTo': '', 'spendCap': '', 'telegramToken': '', 'telegramChat': '', 'quietFrom': '22:00', 'quietTo': '07:00', 'vocabulary': '', 'homeUrl': '', 'homeToken': ''}

    @classmethod
    def d(cls):
        try:
            with open(cls.path) as f: v = json.load(f)
            return v if isinstance(v, dict) else {}
        except (OSError, ValueError): return {}

    @classmethod
    def get(cls, k, default=None): return cls.d().get(k, cls.defaults.get(k, default))

    @classmethod
    def set(cls, k, v):
        d = cls.d(); d[k] = v
        os.makedirs(os.path.dirname(cls.path), exist_ok=True)
        tmp = cls.path + '.tmp'
        with open(tmp, 'w') as f: json.dump(d, f)
        os.replace(tmp, cls.path)


def box_width(saved, bounds_w):   # Jev.swift boxWidth()
    try: saved = float(saved)
    except (TypeError, ValueError): saved = 500
    return int(min(min(900, max(340, saved)), bounds_w - 16))


class App:
    def __init__(self):
        self.busy = self.hovering = self.pinned = self.composing = False
        self.gen, self.proc, self.warm = 0, None, None
        self.ask_file, self.retry_offer, self.answer, self.text, self.comp_h, self.over_text = '', False, '', '', 0, False
        self.hand = False
        self.listening, self.ear_ready, self.ear_error, self.voice, self.mine = False, False, '', None, ''
        subprocess.Popen([sys.executable, os.path.join(os.path.dirname(HERE), 'telegram_bridge.py')], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)   # phone bridge: idles until a bot token is set
        # speech in: one long-lived listener (linux/listen.py), so the Whisper model loads once
        self.ear = subprocess.Popen([sys.executable, os.path.join(HERE, 'listen.py')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
                                    env=dict(os.environ, PYTHONPATH=os.path.expanduser('~/.local/share/jev/py'),
                                             JEV_ALLOW_DOWNLOAD='0' if Prefs.get('allowDownload') is False else '1'))
        threading.Thread(target=self.hear_loop, daemon=True).start()
        self.waking, self.hands_free, self.wake = False, False, Wake(self)
        self.streamed, self.speaker = False, voice.Speaker()
        if Prefs.get('monitor', True):   # overload / heat alerts (linux/sysmon.py), checked in the background, no model involved
            import sysmon
            def alert(msg):
                subprocess.run(['notify-send', '-u', 'critical', '-i', os.path.join(HERE, 'jev.png'), 'Jev ⚠️', msg], capture_output=True)
                if Prefs.get('speak'): GLib.idle_add(lambda: (not self.busy and not self.listening and self.voice is None and
                                                              subprocess.Popen([os.path.join(HERE, 'bin', 'say'), 'Warning. ' + msg]), False)[1])
            threading.Thread(target=sysmon.watch, args=(alert,), daemon=True).start()

        # the mic dot: a small red dot in the top-right corner whenever the microphone is open while the box is hidden (wake-word listening)
        self.dot = Gtk.Window(type=Gtk.WindowType.POPUP); self.dot.set_default_size(14, 14); self.dot.set_keep_above(True)
        self.dot.set_accept_focus(False); self.dot.set_tooltip_text('Jev is listening for its name. Turn this off in Settings: Microphone off.')
        if self.dot.get_screen().get_rgba_visual(): self.dot.set_visual(self.dot.get_screen().get_rgba_visual())
        css = Gtk.CssProvider(); css.load_from_data(b'window{background:#ff3b30;border-radius:7px}')   # CSS, not cairo: python3-gi-cairo is not always installed
        self.dot.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.win.set_decorated(False); self.win.set_keep_above(True); self.win.set_skip_taskbar_hint(True); self.win.set_skip_pager_hint(True)
        self.win.set_type_hint(Gdk.WindowTypeHint.UTILITY); self.win.stick(); self.win.set_title('Jev')
        self.win.set_icon_from_file(os.path.join(HERE, 'jev.png'))
        visual = self.win.get_screen().get_rgba_visual()
        if visual: self.win.set_visual(visual)
        self.win.set_app_paintable(True)
        self.win.connect('key-press-event', self.key)
        self.win.connect('focus-out-event', self.focus_out)
        self.win.connect('delete-event', lambda *_: (self.close(True), True)[1])

        cm = WebKit2.UserContentManager()
        # the box's dark rounded glass (NSVisualEffectView .hudWindow + 0.85 tint, radius 18); WebKit paints over the window, so the page carries it
        # shortcut: no backdrop blur, GTK has none for X11 windows
        cm.add_style_sheet(WebKit2.UserStyleSheet('html{background:rgba(18,18,20,.85)!important;border-radius:18px;height:100vh}',
                           WebKit2.UserContentInjectedFrames.TOP_FRAME, WebKit2.UserStyleLevel.USER, None, None))
        for name in ('h', 'c'):
            cm.register_script_message_handler(name)
            cm.connect(f'script-message-received::{name}', self.message, name)
        self.web = WebKit2.WebView.new_with_user_content_manager(cm)
        self.web.set_background_color(Gdk.RGBA(0, 0, 0, 0))
        self.web.connect('decide-policy', self.policy)
        self.web.connect('button-press-event', self.press)
        self.web.connect('motion-notify-event', self.motion)
        self.web.connect('enter-notify-event', lambda *_: self.enter(True))
        self.web.connect('leave-notify-event', lambda *_: self.enter(False))
        self.win.add(self.web)
        self.win.set_default_size(box_width(Prefs.get('boxW'), self.screen()[2]), 76)
        with open(os.path.join(ROOT, 'ui', 'ui.html')) as f: html = f.read()
        with open(os.path.join(ROOT, 'ui', 'orbs.js')) as f: orbs = f.read()
        self.web.load_html(html.replace('/*ORBS*/', orbs), None)   # loadPage(): orbs.js inlined at its marker
        self.settings, self.onboarding = panes.Settings(self, Prefs), panes.Onboarding(self, Prefs)
        self.agents = panes.Agents(self, Prefs)
        self.web.show(); self.win.realize(); self.win.set_opacity(0)   # set_opacity is deprecated in GTK3 but still the window-level fade

    def dock_anchor(self):   # GNOME's dock marks an app running only while it has a window: a minimized one keeps Jev there all the time,
        w = self.anchor = Gtk.Window(title='Jev')   # and clicking it (which restores it) opens the typing box instead
        w.set_default_size(240, 80); w.set_icon_from_file(os.path.join(HERE, 'jev.png'))
        def state(_w, e):
            if e.changed_mask & Gdk.WindowState.ICONIFIED and not e.new_window_state & Gdk.WindowState.ICONIFIED:
                GLib.idle_add(lambda: (w.iconify(), self.shortcut(True), False)[2])
        w.connect('window-state-event', state); w.connect('delete-event', lambda *_: (w.iconify(), True)[1])
        w.show_all(); GLib.timeout_add(300, lambda: (w.iconify(), False)[1])

    def open_window(self, which):   # `jev --settings|--setup|--agents` (and the menu entries the Mac has in its menu bar)
        {'settings': self.settings.open, 'setup': self.onboarding.open, 'agents': self.agents.open_view}[which]()

    def screen(self):   # the pointer's monitor work area, else the primary one
        d = Gdk.Display.get_default(); seat = d.get_default_seat()
        _, x, y = seat.get_pointer().get_position()
        m = d.get_monitor_at_point(x, y) or d.get_primary_monitor() or d.get_monitor(0)
        g = m.get_workarea(); return g.x, g.y, g.width, g.height

    # ---- the page bridge
    def js(self, call, arg=None):   # callJS(web, "ui." + call, [arg])
        args = [] if arg is None else [arg]
        self.web.evaluate_javascript(f'ui.{call}(...{json.dumps(args)})', -1, None, None, None, None, None)

    def message(self, _cm, result, name):
        try: body = json.loads(result.get_js_value().to_json(0))
        except (ValueError, TypeError, AttributeError): return
        if name == 'h': return self.size(body)
        if not isinstance(body, dict): return
        b = body.get
        if isinstance(b('fold'), int) and isinstance(b('h'), (int, float)):
            self.resize(b('h')); return GLib.timeout_add(250, lambda: (self.js('foldSettled', b('fold')), False)[1])
        if isinstance(b('comp'), (int, float)): self.comp_h = b('comp')
        if isinstance(b('overText'), bool): self.over_text = b('overText')
        if isinstance(b('boxH'), (int, float)): Prefs.set('boxH', b('boxH'))
        if isinstance(b('focus'), bool):
            self.composing = b('focus')
            if not self.composing and not self.hovering and not self.busy: self.hide(3)
        link = b('link')
        if isinstance(link, str) and link.split(':', 1)[0].lower() in ('https', 'http', 'mailto'): Gtk.show_uri_on_window(None, link, Gdk.CURRENT_TIME)
        if isinstance(b('copy'), str) and b('copy'):
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(b('copy'), -1); self.js('copied')
        if b('mic') is not None and (not self.busy or self.retry_offer):   # the box's mic button: talk, then a pause sends it
            self.stop_listening() if self.listening else self.start_listening()
        if b('workerRetry') is not None and not self.busy: self.pinned = False; self.typed(self.text, keep=True)
        if b('retry') is not None and not self.busy: self.typed(self.text, keep=True)
        if isinstance(b('send'), str): self.typed(b('send'), keep=True)
        if b('ready') is not None:
            self.js('size', Prefs.get('boxH'))
            if Prefs.get('tips') and not Prefs.get('pointCoached'): self.js('pointCoach')
        if b('pointCoached') is not None: Prefs.set('pointCoached', True)
        if b('safe') is not None: Prefs.set('safe', True); self.js('mode', True)
        if isinstance(b('model'), str): Prefs.set('apiModel' if Prefs.get('apiBase') else 'routing', b('model'))
        if b('resume') is not None:
            Prefs.set('paused', False); self.js('paused', False); self.hide(1.5)
        if isinstance(b('pick'), str) and self.ask_file:
            self.retry_offer = False; self.write(self.ask_file, b('pick')); self.ask_file = ''
        if b('off') in ('tips', 'support'): Prefs.set(b('off'), False)
        if isinstance(b('improve'), bool): Prefs.set('improve', b('improve'))
        if isinstance(b('allow'), bool) and self.ask_file:   # "Allow for this task" answers "task": no more cards for this ask
            self.write(self.ask_file, 'task' if b('allow') and b('task') is True else 'y' if b('allow') else 'n'); self.ask_file = ''
        # shortcut: setup, agents, mini screen, pointing, memory and kofi open Mac-only windows; they arrive with those ports

    def size(self, body):   # the 'h' handler: the page's height (or [w, h] for the dictation pill)
        size = body if isinstance(body, list) else [body]
        if size and isinstance(size[-1], (int, float)) and size[-1] > 0: self.resize(size[-1])

    def resize(self, h):   # grows down from the top
        w, _ = self.win.get_size()
        self.win.resize(w, int(h))

    def model_choices(self):   # modelChoices()
        if Prefs.get('client') != 'claude': return {'list': [], 'pick': ''}
        if not Prefs.get('apiBase'): return {'list': ['cheapest', 'balanced', 'capable'], 'pick': Prefs.get('routing')}
        pick = Prefs.get('apiModel') or ''
        return {'list': [pick] if pick else [], 'pick': pick}

    # ---- showing and hiding
    def show(self):
        self.gen += 1; self.js('visible', True); self.js('mode', bool(Prefs.get('safe'))); self.js('models', self.model_choices())
        if self.win.get_visible() and self.win.get_opacity() > 0:
            return self.fade(1)
        x, y, w, _ = self.screen()
        bw = box_width(Prefs.get('boxW'), w); _, h = self.win.get_size()
        self.win.resize(bw, h)
        self.win.move(x + w - bw - 14 if Prefs.get('corner') == 'top-right' else x + 14, y + 10)
        self.win.show_all(); self.fade(1)

    def fade(self, to, done=None, step=.12):   # NSAnimationContext alphaValue fades
        g = self.gen
        def tick():
            if g != self.gen and to == 0: return False   # shown again meanwhile
            o = self.win.get_opacity(); o = min(to, o + step) if to > o else max(to, o - step)
            self.win.set_opacity(o)
            if o == to:
                if done: done()
                return False
            return True
        GLib.timeout_add(16, tick)

    def linger(self, s): return s * {'short': .5, 'long': 2}.get(Prefs.get('linger'), 1)

    def hide(self, s):
        g = self.gen
        def later():
            if g != self.gen or self.busy or self.hovering or self.pinned or self.composing or self.listening: return False
            if self.voice and self.voice.poll() is None: return False   # still reading the answer aloud; its end hides the box
            self.fade(0, lambda: g == self.gen and self.gone(), .06)
            return False
        GLib.timeout_add(int(s * 1000), later)

    def gone(self):
        self.win.hide(); self.js('visible', False)

    def close(self, clear):   # ✕ ends the conversation; clicking away keeps it
        self.hush(); self.gen += 1; g = self.gen
        self.pinned = self.composing = False
        self.fade(0, lambda: g == self.gen and self.gone(), .1)

    def shush(self):   # stop reading aloud
        self.speaker.stop()
        if self.voice and self.voice.poll() is None:
            self.voice.terminate(); subprocess.run(['spd-say', '-C'], capture_output=True)
        self.voice = None

    def hush(self):
        if self.listening: self.listening = False; self.tell_ear('cancel')
        if self.proc: self.proc.cancel(); self.proc = None
        self.busy = False; self.ask_file = ''; self.retry_offer = False

    def cancel(self):
        cues.cue('soundStop'); self.hush(); self.js('stopped', 'Answer stopped'); self.hide(1.5)

    def escape(self):   # one layer per press: voice, listening, a card, the answer, then the box
        if self.voice and self.voice.poll() is None: return self.shush()
        if self.listening:
            self.listening = False; cues.cue('soundStop'); self.tell_ear('cancel'); self.js('msg', ''); return self.close(False)
        if self.busy: return self.cancel()
        self.close(False)

    # ---- input
    def key(self, _w, e):
        if e.keyval == Gdk.KEY_Escape: self.escape(); return True
        return False

    def focus_out(self, *_):   # clicking anywhere else closes the box once the answer is up
        if self.win.get_visible() and not self.busy and not self.composing and not self.hovering: self.close(False)
        return False

    def over_x(self, x, y):   # the × is native's corner, wider than its dot
        w, _ = self.win.get_size()
        return x > w - 42 and y < 42

    def press(self, _w, e):
        if e.button != 1 or e.type != Gdk.EventType.BUTTON_PRESS: return False
        w, h = self.win.get_size()
        if e.x < 6 or e.x > w - 6:   # side edges: width, saved like boxW
            self.pinned = True
            self.win.begin_resize_drag(Gdk.WindowEdge.WEST if e.x < 6 else Gdk.WindowEdge.EAST, 1, int(e.x_root), int(e.y_root), e.time)
            GLib.timeout_add(400, lambda: (Prefs.set('boxW', self.win.get_size()[0]), False)[1])
            return True
        if self.over_x(e.x, e.y): self.close(True); return True
        if e.y > h - self.comp_h or self.over_text:   # the typing box or answer text: a normal click
            self.pinned = True; self.win.present_with_time(e.time); return False
        self.pinned = True
        self.win.begin_move_drag(1, int(e.x_root), int(e.y_root), e.time)
        return False

    def motion(self, _w, e):
        self.pointer(f'[{e.x},{e.y}],{json.dumps(self.over_x(e.x, e.y))}')
        return False

    def enter(self, on):
        if self.hovering != on: self.js('hover', on)
        self.hovering = on
        if not on:
            self.pointer('[]')
            if not self.busy: self.hide(3)
        return False

    def pointer(self, args):   # the page marks .hot and says whether the cursor is a hand
        def done(web, res, _):
            try: hand = web.evaluate_javascript_finish(res).to_boolean()
            except GLib.Error: return
            if hand != self.hand:
                self.hand = hand
                gw = self.win.get_window()
                if gw: gw.set_cursor(Gdk.Cursor.new_from_name(gw.get_display(), 'pointer' if hand else 'default'))
        self.web.evaluate_javascript(f'ui.pointer({args})', -1, None, None, None, done, None)

    def policy(self, _w, decision, kind):   # links never navigate the box itself
        if kind == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            uri = decision.get_navigation_action().get_request().get_uri()
            if uri and not uri.startswith(('about:', 'data:')):
                decision.ignore(); return True
        return False

    def shortcut(self, typing=False):   # typing: clicked from the dock/launcher, so open the typing box, not the mic
        # the hotkey (Settings: input "type" opens the box ready to type)
        if Prefs.get('paused'): self.js('paused'); self.show(); return self.hide(4)
        if self.listening: return self.stop_listening()   # GNOME shortcuts only report the press: press to talk, press again to send
        if self.voice and self.voice.poll() is None or self.speaker.speaking(): self.shush()   # the mic must never hear Jev's own voice
        if self.busy and not self.retry_offer: return self.cancel()
        self.mine = self.front_app()
        if Prefs.get('input') != 'type' and not typing: return self.start_listening()
        if self.composing and self.win.get_visible() and self.win.get_opacity() > 0: return self.close(False)
        self.unwarm(); self.warm = self.spawn()
        self.win.set_focus_on_map(True); self.show(); self.win.present(); self.web.grab_focus(); self.js('compose', True)

    def front_app(self):   # `mine`: the app the user was in, read before the box takes focus
        try:
            r = subprocess.run([sys.executable, os.path.join(HERE, 'hands.py'), '--front'], capture_output=True, text=True, timeout=2,
                               env={**{k: v for k, v in os.environ.items() if k != 'JEV_FRONT'}, 'JEV_HOST_PID': str(os.getpid())})
            return r.stdout.strip() or (wm.active() or {}).get('app', '')
        except (OSError, subprocess.TimeoutExpired): return ''

    # ---- speech: start(), heard(), stop() with the Whisper listener
    def nudge_tick(self):   # proactive mode: speak first, only when nothing else is going on
        if (Prefs.get('proactive', True) and Prefs.get('onboarded') and not (self.busy or self.listening or self.composing or self.speaker.speaking() or self.win.get_visible()) and not proactive.hushed()):
            if Prefs.get('briefing', True) and proactive.briefing_due(quiet=proactive.quiet_window()): self.typed("Today's briefing"); return True   # once a day, the first idle minute
            text = proactive.next_nudge(quiet=proactive.quiet_window())
            if text:
                subprocess.Popen(['notify-send', '-a', 'Jev', 'Jev', text], stderr=subprocess.DEVNULL)
                if Prefs.get('speak', True): self.speaker.say(text)
        return True

    def wake_tick(self):   # Mac wakeTick: listen for the name only while nothing else uses the mic or the screen
        if self.speaker.speaking(): self.quiet_at = time.time() + 1.5   # the room still rings a moment after the voice stops
        if self.speaker.speaking() and Prefs.get('interrupt', True) and self.ear_ready and not self.listening and not self.waking:
            if not getattr(self, 'barge', False): self.barge = True; self.tell_ear('interrupt')   # saying "stop" while Jev talks cuts it off
            return True
        if getattr(self, 'barge', False): self.barge = False; self.tell_ear('cancel')
        busy = (time.time() < getattr(self, 'quiet_at', 0) or not Prefs.get('wakeWord') or Prefs.get('paused') or Prefs.get('micOff') or not self.ear_ready or self.busy or self.listening or self.composing
                or self.voice is not None or self.speaker.speaking() or (self.win.get_visible() and not self.hands_free) or not Prefs.get('onboarded'))
        if busy and self.waking: self.waking = False; self.tell_ear('cancel')
        elif not busy and not self.waking:
            self.waking = True; self.tell_ear('wake ' + (Prefs.get('wakeWordName') or 'Jev'))
        if self.waking != self.dot.get_visible():
            x, y, w, _h = self.screen(); self.dot.move(x + w - 24, y + 10); self.dot.set_visible(self.waking)
        return True

    def tell_ear(self, cmd):
        try: self.ear.stdin.write(cmd + '\n'); self.ear.stdin.flush()
        except (OSError, ValueError): pass

    def hear_loop(self):
        for line in self.ear.stdout:
            try: GLib.idle_add(self.heard, json.loads(line))
            except ValueError: pass
        GLib.idle_add(self.heard, {'error': self.ear_error or 'Speech stopped. Restart Jev to talk again.'})

    def start_listening(self):
        if not self.ear_ready:
            self.show(); self.js('msg', self.ear_error or 'Speech is still loading. Try again in a moment, or type.'); return self.hide(6)
        replying = self.retry_offer and self.ask_file
        if not replying:
            self.unwarm(); self.warm = self.spawn(); self.text = ''
        if self.waking: self.waking = False   # the ear leaves wake mode itself when 'start' arrives
        self.shush(); self.listening = True; cues.cue('soundStart')
        self.win.set_focus_on_map(False); self.show()
        self.js('listen') if not replying else self.js('draft', '')
        self.tell_ear('start')

    def stop_listening(self):
        if self.listening: cues.cue('soundRelease'); self.tell_ear('stop'); self.js('think')

    def heard(self, j):
        if os.environ.get('JEV_DEBUG') and 'level' not in j: print('heard', j, file=sys.stderr, flush=True)
        if 'ready' in j: self.ear_ready = True
        elif 'downloading' in j:   # one disclosed line on the box itself; never a popup, never silent (see docs/JEV-BRIEF.html)
            self.show(); self.js('msg', f"Setting up voice ({j['downloading']} MB)…"); self.hide(6)
        elif 'stop' in j:
            self.barge = False; self.shush(); self.quiet_at = time.time() + 1.5
        elif 'wake' in j:
            if self.waking: self.waking = False; cues.cue('soundStart'); self.hands_free = True; self.start_listening()
        elif 'error' in j:
            self.ear_error, self.ear_ready = j['error'], False
            if self.listening: self.listening = False; self.js('msg', j['error']); self.hide(6)
        elif 'denied' in j:   # mic switched off, or not the owner's voice: say why, run nothing
            self.listening = False; self.hands_free = False; self.js('msg', j['denied']); self.hide(6)
        elif not self.listening: pass
        elif 'level' in j: self.js('level', j['level'])
        elif 'words' in j: self.text = j['words']; self.js('words', j['words'])
        elif 'final' in j:
            self.listening = False; self.hands_free = False; t = j['final'].strip()
            if not t: self.js('msg', ''); return self.hide(.2)   # nothing heard: end quietly, no error line
            if self.retry_offer and self.ask_file: return self.js('respond', t)
            self.text = t; self.js('words', t); self.run(t)
        return False

    def deliver(self, a):   # Settings: read answers aloud, copy them
        if Prefs.get('autoCopy'): Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(a, -1)
        if Prefs.get('speak') and self.streamed:   # already spoken piece by piece: just hide when the voice ends
            def wait():
                while self.speaker.speaking(): time.sleep(.15)
                GLib.idle_add(lambda: (self.hide(2), False)[1])
            threading.Thread(target=wait, daemon=True).start()
        elif Prefs.get('speak'):
            self.shush()
            spoken = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', a); spoken = re.sub(r'[*_`#>|$\\]', '', spoken)
            tone = Prefs.get('voiceTone') or 'normal'
            self.voice = v = subprocess.Popen([os.path.join(HERE, 'bin', 'say'), '--tone', tone, spoken], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            threading.Thread(target=lambda: (v.wait(), GLib.idle_add(lambda: (v is self.voice and self.hide(2), False)[1])), daemon=True).start()

    def blur(self):   # Hands is about to press keys: the box steps aside so they reach the user's app (the Mac panel never takes key focus)
        if self.win.get_visible() and self.win.is_active():
            self.composing = False; self.win.hide(); self.win.set_focus_on_map(False); self.win.show_all()
        return False

    def typed(self, t, keep=False):
        if self.retry_offer and self.ask_file: return self.js('respond', t)
        if self.busy or not t.strip(): return
        self.text = t
        self.js('listen', keep); self.show(); self.js('words', t); self.run(t)

    # ---- the worker: spawn() and run()
    def spawn(self):
        box = []
        front = self.mine or (wm.active() or {}).get('app', '')   # `mine`: the app the user was in
        try:
            w = Worker(lambda l: GLib.idle_add(self.feed, box[0], l), lambda c: GLib.idle_add(self.exited, box[0], c), front=front,
                       env={'JEV_STREAM': '1'} if Prefs.get('speak') else None)   # the brain streams its answer so speech starts at once
        except OSError: return None
        box.append(w); return w

    def unwarm(self):
        if self.warm: self.warm.cancel(); self.warm = None

    def run(self, t):
        self.busy = True; self.answer = ''; self.streamed = False
        self.js('think')
        if self.warm and self.warm.p.poll() is not None: self.warm = None
        w = self.warm or self.spawn(); self.warm = None
        if not w:
            self.busy = False; self.pinned = True; self.js('workerFailed'); return self.show()
        self.proc = w; w.run(t)

    def write(self, path, value):
        try:
            with open(path + '.tmp', 'w') as f: f.write(value)
            os.replace(path + '.tmp', path)
        except OSError: pass

    def feed(self, w, line):   # spawn()'s line parser
        if w is not self.proc: return False   # buffered output from a cancelled request stays cancelled
        if os.environ.get('JEV_DEBUG'): print('line', line, file=sys.stderr, flush=True)
        if line == '! setup': self.onboarding.open(True); return False
        if line == '! feedback': self.settings.open('feedback'); return False
        if line == '! improve': self.js('improve'); return False
        if line.startswith('~ '):   # a piece of the answer, spoken while the model is still writing
            if Prefs.get('speak'):
                if not self.streamed: self.shush()
                self.streamed = True; self.speaker.say(line[2:], Prefs.get('voiceTone') or 'normal')
            return False
        if line.startswith('▣ '): return False   # the live mini window is Mac only (panes.MiniScreen shows the window's name instead)
        if line.startswith('▤ '): self.show_agent = line[2:]; return False
        if line.startswith('▥ '): self.agents.open_view(line[2:]); return False
        if line.startswith('@ ') and not line.endswith(' answer'): return False   # shortcut: no on-screen pointer yet
        if line.startswith('? '):
            p = line[2:].split('\t')
            if not 3 <= len(p) <= 6: return False
            self.retry_offer = len(p) >= 5 and p[4] == 'retry'
            self.ask_file = p[2]; self.show()
            self.js('ask', [p[0], p[1], 'retry' if self.retry_offer else '', p[5] if self.retry_offer and len(p) == 6 else '', len(p) == 4 and p[3] == 'task'])
            return False
        if line.startswith('⚙ '):
            p = line.split(' ')
            if len(p) == 3 and p[1] not in ('paused',) and (p[1] != 'safe' or p[2] == 'true') and not p[1].startswith('hotkey'):
                Prefs.set(p[1], p[2] == 'true' if p[2] in ('true', 'false') else p[2])
            return False
        if line.startswith('◇ '):
            try: j = json.loads(line[2:])
            except ValueError: return False
            self.retry_offer = True; self.ask_file = j.get('a', ''); self.show(); self.js('pick', j); return False
        if line.startswith('⇢ '): return False
        if line.startswith('⤴ '):
            try: brief = json.loads(line[2:])
            except ValueError: return False
            self.busy = False; self.js('finished'); self.agents.prepare(brief); return False
        if line.startswith('↺ '):
            try: j = json.loads(line[2:])
            except ValueError: return False
            if isinstance(j.get('t'), str): self.pinned = True; self.js('rewrite', [j['t'], j.get('mode') or 'replace', False])
            return False
        if line.startswith('✓'):
            result = line[2:].replace(' ', '\n')
            self.answer = '✓ ' + result; self.js('line', self.answer); cues.cue('soundDone')
            self.deliver(result)
            return False
        if line.startswith('! '): self.js('msg', line[2:])
        else: self.js('line', line)
        return False

    def exited(self, w, code):
        if w is self.warm: self.warm = None
        if w is not self.proc: return False   # a cancelled run ending late must not touch the next one
        self.busy = False; self.proc = None; self.js('finished')
        self.hide(self.linger(max(6, min(30, len(self.answer) / 12))))   # longer answers stay longer
        return False


class Wake:   # the Settings toggle: app.wake.set(bool)
    def __init__(self, app): self.app = app; GLib.timeout_add(1000, app.wake_tick); GLib.timeout_add_seconds(60, app.nudge_tick)
    def set(self, on): self.app.wake_tick()


def listen(app):   # one instance; `--toggle` presses the hotkey
    try: os.unlink(SOCK)
    except OSError: pass
    s = socket.socket(socket.AF_UNIX); s.bind(SOCK); os.chmod(SOCK, 0o600); s.listen(4)
    def loop():
        while True:
            c, _ = s.accept()
            cmd = c.recv(64).decode(errors='replace').strip()
            if cmd == 'blur':
                done = threading.Event(); GLib.idle_add(lambda: (app.blur(), done.set(), False)[2]); done.wait(1)
                try: c.sendall(b'ok')
                except OSError: pass
            c.close()
            if cmd == 'toggle': GLib.idle_add(lambda: (app.shortcut(), False)[1])
            elif cmd == 'type': GLib.idle_add(lambda: (app.shortcut(True), False)[1])
            elif cmd == 'quit': GLib.idle_add(Gtk.main_quit)
            elif cmd in ('settings', 'setup', 'agents'): GLib.idle_add(lambda: (app.open_window(cmd), False)[1])
    threading.Thread(target=loop, daemon=True).start()


def send(cmd):
    c = socket.socket(socket.AF_UNIX); c.connect(SOCK); c.sendall(cmd.encode()); c.close()


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg in ('--toggle', '--type', '--quit', '--settings', '--setup', '--agents') and not os.environ.get('JEV_FRESH'):
        try: send(arg[2:]); sys.exit(0)
        except OSError:
            if arg == '--quit': sys.exit(0)
            os.environ['JEV_FRESH'] = '1'   # the fresh copy must start, not look for one to message again
            os.execv(sys.executable, [sys.executable, os.path.abspath(__file__), '--show' if arg == '--toggle' else arg])   # not running: start it, open the box or window
    try: ctypes.CDLL(None).prctl(15, b'jev', 0, 0, 0)   # PR_SET_NAME: the task manager lists this process as jev, not python3
    except Exception: pass
    GLib.set_prgname('Jev')   # its AT-SPI name, so Hands never mistakes the box for the user's app
    Gdk.set_program_class('Jev'); GLib.set_application_name('Jev')   # same X11 class and Wayland app id: the dock matches jev.desktop and shows only the logo
    app = App(); listen(app)
    app.dock_anchor()
    if arg in ('--show', '--type'): GLib.timeout_add(600, lambda: (app.shortcut(arg == '--type'), False)[1])   # after the page loads
    elif arg in ('--settings', '--setup', '--agents'): GLib.timeout_add(600, lambda: (app.open_window(arg[2:]), False)[1])
    elif not Prefs.get('onboarded'): GLib.timeout_add(900, lambda: (app.onboarding.open(True), False)[1])   # first run: the Setup window, as on the Mac
    Gtk.main()
