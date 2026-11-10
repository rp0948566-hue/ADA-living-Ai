Back to [[Home]]

# Fifth pass: Jev speaks first (2026-11-10)

- Daily briefing: `linux/proactive.py` `briefing_due()` is true once a day, the first idle minute outside quiet hours; `linux/host.py` `nudge_tick` then runs the request "Today's briefing" (pref `briefing`, default on). Rule `SPEAK_FIRST` in `jev.py`: under 60 words, calendar, urgent things from notes and goals, weather, one news item with its source.
- "Not now": `jev.py --hush [hours]` (3 by default, `off` ends it) writes `DIR/hush`; `proactive.hushed()` silences nudges and the briefing until then.
- Fixed: `next_nudge` no longer erases other keys in `proactive.json`; `linux/voice.py` line 16 had `TONES` merged into a comment, which stopped all Linux speech.
- Hindi voice `hi_IN-pratham-medium` is downloaded on this laptop.
- Tests: `tests/test_mind.py` class SpeakFirst; 145 pass on Linux. Not built: Mac side, a Settings switch for the briefing, mail as a signal.
