"""Calendar on Linux, the EventKit counterpart of Jev.swift's CalendarTool: same JSON in, same JSON out.
Events live in ~/.local/share/jev/calendar.json; calendar.ics beside it mirrors them so GNOME Calendar, Thunderbird or
Google Calendar can import/subscribe. shortcut: Jev's own calendar only, not GNOME Online Accounts (needs Evolution
Data Server bindings, gir1.2-ecal-2.0), upgrade when those are installed."""
import json, os, uuid
from datetime import datetime, timezone

HOME = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'jev')
STORE, ICS = os.path.join(HOME, 'calendar.json'), os.path.join(HOME, 'calendar.ics')
CAL = {'id': 'jev', 'title': 'Jev', 'writable': True}


def date(v):
    try:
        d = datetime.fromisoformat(v)
        return d if d.utcoffset() is not None else None
    except (TypeError, ValueError): return None


def load():
    try:
        with open(STORE) as f: return json.load(f)
    except (OSError, ValueError): return []


def save(events):
    os.makedirs(HOME, mode=0o700, exist_ok=True)
    tmp = STORE + '.tmp'
    with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'w') as f: json.dump(events, f, indent=1)
    os.replace(tmp, STORE)
    utc = lambda v: date(v).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    esc = lambda s: s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Jev//Linux//EN', 'X-WR-CALNAME:Jev']
    for e in events:
        lines += ['BEGIN:VEVENT', f"UID:{e['id']}", f"DTSTAMP:{utc(e['modified'])}", f"DTSTART:{utc(e['start'])}", f"DTEND:{utc(e['end'])}",
                  f"SUMMARY:{esc(e['title'])}", 'END:VEVENT']
    with open(ICS, 'w') as f: f.write('\r\n'.join(lines + ['END:VCALENDAR']) + '\r\n')


def row(e):
    return {'id': e['id'], 'title': e['title'], 'start': e['start'], 'end': e['end'], 'calendarID': CAL['id'], 'calendar': CAL['title'],
            'writable': True, 'allDay': False, 'attendees': [], 'modified': e['modified']}


def run(data):
    action, events = data.get('action', ''), load()
    now = datetime.now().astimezone().isoformat()
    if action == 'list':
        start, end = date(data.get('from')), date(data.get('to'))
        if not start or not end or end <= start or (end - start).days > 4 * 365: return {'error': 'Use a valid range shorter than four years.'}
        q = (data.get('query') or '').casefold()
        rows = sorted((row(e) for e in events if date(e['start']) < end and date(e['end']) > start and q in e['title'].casefold()), key=lambda r: date(r['start']))
        return {'events': rows, 'calendars': [CAL]}
    if action not in ('add', 'move', 'delete'): return {'error': 'Unknown calendar action.'}
    if action == 'add':
        if not str(data.get('title', '')).strip(): return {'error': 'A title is required.'}
        if data.get('calendarID') not in (None, CAL['id']): return {'error': 'Choose a writable calendar from list.'}
        e = {'id': uuid.uuid4().hex, 'title': data['title'].strip()}
    else:
        want = data.get('event') or {}
        matches = [e for e in events if row(e) == want]
        if len(matches) != 1: return {'error': 'Event changed or disappeared. Read it again and ask for approval again.'}
        e = matches[0]
        if action == 'delete':
            save([x for x in events if x is not e]); return {'deleted': want}
    start, end = date(data.get('start')), date(data.get('end'))
    if not start or not end or end <= start: return {'error': 'Use a start and a later end with timezone offsets.'}
    e.update(start=start.isoformat(), end=end.isoformat(), modified=now)
    save(events if action == 'move' else events + [e])
    return {'event': row(e)}


if __name__ == '__main__':   # self-check against a scratch store
    import tempfile
    HOME = tempfile.mkdtemp(); STORE, ICS = os.path.join(HOME, 'c.json'), os.path.join(HOME, 'c.ics')
    a = run({'action': 'add', 'title': 'Dentist', 'start': '2026-11-10T10:00:00+05:30', 'end': '2026-11-10T11:00:00+05:30'})['event']
    l = run({'action': 'list', 'from': '2026-11-10T00:00:00+05:30', 'to': '2026-11-11T00:00:00+05:30'})
    assert l['events'] == [a], l
    m = run({'action': 'move', 'event': a, 'start': '2026-11-10T12:00:00+05:30', 'end': '2026-11-10T13:00:00+05:30'})['event']
    assert m['start'].startswith('2026-11-10T12') and 'SUMMARY:Dentist' in open(ICS).read()
    assert run({'action': 'move', 'event': a, 'start': m['start'], 'end': m['end']}).get('error')   # stale copy refused
    assert run({'action': 'delete', 'event': m}) == {'deleted': m} and load() == []
    print('calendar ok')
