Back to [[Home]]

# Built from the crowd analysis (2026-11-10) — see the "Crowd Voice" vault for the data

- **Audit log** (`jev.py` `audit()`/`actions_report()`, `--actions [N]`): every gate decision (allowed/blocked + reason) appended to `~/.config/jev/actions.jsonl` (0600, trims to last 2000 lines past 5 MB). Agents may run `--actions` without an Allow card. Answers "what did you do?". Tests: `tests/test_actions.py`.
- **Private mode** (pref `privateMode`, Settings switch, `--privacy`): gate refuses WebFetch/WebSearch, connectors, `--search/--read/--web`, curl/wget, browser helper. `--privacy` states plainly where words go (local model / remote server / cloud) and the mode. Tests: `tests/test_privacy.py`.
- **Smart home** (`--home list|state|call`, Settings → Home Assistant address + token): Home Assistant REST over stdlib. A `call` is deliberately NOT a trusted read helper, so it gets the normal Allow card. Tests: `tests/test_home.py` (fake HA server).
- **Boundary rules** (`TRUST_RULES`, always in the prompt): refuse malware/hacking/spying/bulk spam/impersonation/weapons; no jailbreaking; confirm item+total before spending; flag medical/legal/money limits; never pretend to be human; never change own rules without a shown diff and a yes; say what failed + why + next step. Tests: `tests/test_trust.py`.
- **Read-only mode** (pref `readOnly`, Settings switch): gate refuses Write/Edit/NotebookEdit and any Bash that is not a read helper (`readonly_block`).
- **Where were we** (`--resume [N]`): last asks + answers from `log.jsonl`; trusted read helper.
- **Undo** (`linux/bin/trash --undo [words]`): restores the newest item Jev trashed to its original path, never overwrites, ignores items the user trashed.
- **Quiet hours** (`linux/proactive.py`, prefs `quietFrom`/`quietTo`, default 22:00-07:00): no spoken nudges inside the window. Host passes `quiet=quiet_window()`.
- **My words** (pref `vocabulary`, Settings): Whisper `initial_prompt` via `models.vocab_prompt` (Linux listener).
- Crowd analysis final tally (stopped 2026-11-10 by the user): 76.3M messages read, 4.99M about AI, 198k wishes, 216k complaints. HN 239/240 months (missing newest 2.5 months), Reddit 1,199/7,874 units (~9%), Stack Exchange 306/362 sites (no Stack Overflow). Full showcase: Crowd Voice vault → Reports/Findings.
- Safe forms of risky wishes (2026-11-10, `tests/test_guard.py`, 10 tests):
  - Trusted folder: `jev.py --trust <folder> [minutes]` (`trust()`, `trusted_write()`, file `~/.config/jev/trust.json`). File edits inside skip the Allow card; commands never. Refuses home, `/`, hidden and system folders, more than 24 h. Granting always shows a card; the file cannot be edited by the AI (`must_ask()`).
  - `must_ask()` in `gate()`: payment-looking clicks (`PAY` regex, shows `spendCap`), `voice_clone.py add`, and `--trust` always need the user's yes, whatever Safe mode or "don't ask" say.
  - Kid mode (`kidMode`): `KID_MODE` prompt block + same gate as Read-only (`KID_WHY`). Cannot be switched by voice (`switches()` skips `kidMode`, `ownerVoice`).
  - `SAFE_WAYS` prompt block: the safe offer for each risky wish (no-limits talk, buy for me, clone a voice, watch someone, rewrite yourself, loneliness).
  - Failed actions: tool errors are written to `actions.jsonl` as `result`; `--actions failed` lists failed and blocked with why.
  - Microphone off (`micOff`): `listen.py` opens no recorder, host skips wake; `--privacy` reports mic state.
  - Interpreter language (`translateTo`): `translate_block()`.
  - Owner voice (`ownerVoice`): `linux/voiceid.py`, numpy voiceprint, first voice after switching on is the owner, threshold .93. Basic: a similar voice or a recording can pass. Not calibrated on real voices.
- Second pass (2026-11-10, `tests/test_guard.py` now 12 tests):
  - Mic dot: `self.dot` in `linux/host.py`, red 14 px popup top-right, shown while `self.waking`. CSS, not cairo (python3-gi-cairo is missing here).
  - End of turn: `quiet_needed(words)` in `linux/listen.py`: 1.8 s after a hanging word or comma, 0.6 s after `.?!`, else 0.8 s.
  - `jev.py --undo [words]`: Linux runs `linux/bin/trash --undo`; Mac uses `undo_trash()` (reads `trash <path>` from `actions.jsonl`, moves the item back from `~/.Trash`, never overwrites).
  - `TRUST_RULES` gained the facts rule: name the source, say when unsure, never invent a source, quote, number or link.
- Still open: speaker-model owner lock. Nothing is built or run on a Mac.
- Mac app (`Jev.swift`) only got default prefs for the new keys; not built or tested on a Mac.
