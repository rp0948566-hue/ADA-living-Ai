"""Proactive mode: Jev speaks first, but only about things that matter and never more than a budget allows.
Signals are plain checks (no model call, so no quota): next calendar event, low battery, full disk. `next_nudge()` returns one
sentence or None. Budget: one nudge per 10 min, six a day, the same thing never twice within 6 h.
`briefing_due()` is true once a day, the first time Jev is idle outside quiet hours. `hushed()` is the user's "not now" (jev.py --hush)."""
import glob, json, os, re, shutil, time
from datetime import datetime

HOME = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'jev')
STATE = os.path.join(HOME, 'proactive.json')
GAP, PER_DAY, REPEAT = 600, 6, 6 * 3600


def calendar_signals(now):
    try:
        with open(os.path.join(HOME, 'calendar.json')) as f: events = json.load(f)
    except (OSError, ValueError): return
    for e in events:
        try: mins = (datetime.fromisoformat(e['start']).timestamp() - now) / 60
        except (KeyError, ValueError, TypeError): continue
        if 0 <= mins <= 10: yield f"cal-{e['id']}", f"{e['title']} starts in {max(1, round(mins))} minutes."


def battery_signals(now):
    for d in glob.glob('/sys/class/power_supply/BAT*'):
        try:
            cap, status = int(open(d + '/capacity').read()), open(d + '/status').read().strip()
        except (OSError, ValueError): continue
        if cap <= 15 and status == 'Discharging': yield 'battery', f'Battery is at {cap} percent. Plug in soon.'


def disk_signals(now):
    u = shutil.disk_usage(os.path.expanduser('~'))
    if u.used / u.total >= .95: yield 'disk', f'Your disk is {round(100 * u.used / u.total)} percent full. I can help clear space.'


SIGNALS = (calendar_signals, battery_signals, disk_signals)


def quiet_now(now, start='22:00', end='07:00'):
    """True between start and end local time; the window may cross midnight."""
    t = time.localtime(now); m = t.tm_hour * 60 + t.tm_min
    a, b = (int(x[:2]) * 60 + int(x[3:5]) for x in (start, end))
    return a <= m < b if a <= b else m >= a or m < b


def quiet_window():
    """Settings quietFrom / quietTo (HH:MM); invalid or missing falls back to 22:00-07:00."""
    p = {}
    for d in (os.environ.get('JEV_DIR'), os.path.expanduser('~/.config/jev')):
        try:
            with open(os.path.join(d, 'settings.json')) as f: p = json.load(f); break
        except (TypeError, OSError, ValueError): continue
    ok = lambda v, d: v if isinstance(v, str) and re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', v) else d
    return ok(p.get('quietFrom'), '22:00'), ok(p.get('quietTo'), '07:00')


def next_nudge(now=None, state_path=STATE, signals=SIGNALS, quiet=None):
    now = now or time.time()
    if quiet and quiet_now(now, *quiet): return None
    try:
        with open(state_path) as f: st = json.load(f)
    except (OSError, ValueError): st = {}
    sent, log = st.get('sent', {}), [t for t in st.get('log', []) if now - t < 86400]
    if log and now - log[-1] < GAP or len(log) >= PER_DAY: return None
    for sig in signals:
        for key, text in sig(now):
            if now - sent.get(key, 0) < REPEAT: continue
            sent[key] = now; log.append(now)
            os.makedirs(os.path.dirname(state_path), mode=0o700, exist_ok=True)
            with open(state_path, 'w') as f: json.dump({**st, 'sent': {k: v for k, v in sent.items() if now - v < 86400}, 'log': log}, f)
            return text
    return None


def hushed(now=None, folder=None):
    """True while the user's "not now" lasts: jev.py --hush writes the end time into <settings folder>/hush."""
    for d in ([folder] if folder else (os.environ.get('JEV_DIR'), os.path.expanduser('~/.config/jev'))):
        try:
            with open(os.path.join(d, 'hush')) as f: return (now or time.time()) < float(f.read())
        except (TypeError, OSError, ValueError): continue
    return False


def briefing_due(now=None, state_path=STATE, quiet=None):
    """True once per local day, outside quiet hours; saying yes marks the day done."""
    now = now or time.time()
    if quiet and quiet_now(now, *quiet): return False
    try:
        with open(state_path) as f: st = json.load(f)
    except (OSError, ValueError): st = {}
    day = time.strftime('%Y-%m-%d', time.localtime(now))
    if st.get('brief') == day: return False
    os.makedirs(os.path.dirname(state_path), mode=0o700, exist_ok=True)
    with open(state_path, 'w') as f: json.dump({**st, 'brief': day}, f)
    return True
