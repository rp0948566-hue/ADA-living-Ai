Back to [[Home]]

# Real goal (user, 2026-11-09)

Movie-level assistant: Jarvis / Vision / Friday (+ Ultron's voice for fun, never its hostility). Anyone can use it with zero keyboard/mouse: talk, it talks back, it does everything. Voice-first, for everyone, every OS.

Already in the repo toward that: wake word + hands-free (`linux/host.py` Wake, `listen.py` wake mode, Mac `wakeWord` pref), Whisper STT sized per machine (`linux/tier.py`), Piper TTS with tone tags `{calm}{deep}{menace}…` (`linux/voice.py`, `VOICE_STYLE` in `jev.py`), optional voice cloning (`voice_clone.py`), screen reading, browser agent, calendar/mail, routines, memory.
