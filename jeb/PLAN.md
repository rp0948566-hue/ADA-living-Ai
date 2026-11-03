# Jeb — plan

Repos: `OpenJarvis/` (brain/backend), `Handy/` (speech-to-text). Both fetched as tarballs of `main` (no `git` installed).

## Pipeline
mic -> Handy (STT, hidden: `handy --start-hidden --no-tray`) -> patched to POST text to `http://127.0.0.1:7777/utterance` -> `jeb-daemon` -> gate -> OpenJarvis (`jarvis serve`, headless, no GUI) -> Gemini (free key) -> streamed sentences -> TTS speaks each sentence as it arrives.

## Components
1. **Handy patch** (`Handy/src-tauri`): replace the paste step with an HTTP POST to the daemon. Always-on listening (VAD) instead of hotkey-only. Alt-tap = force-listen override.
2. **jeb-daemon** (Python, systemd --user service, no window, no terminal):
   - Gate (no LLM, zero tokens): rules for wake-name "Jeb", direct questions, commands, silence/idle context, ignoring talk to other people. Alt-tap = always respond. Alt used in a shortcut (any other key pressed while Alt held) = ignored.
   - Only utterances passing the gate reach the LLM. Everything else is logged to memory as text only (no token spend).
   - Proactive suggestions: triggered by events (screen change, error on terminal, calendar), rate-limited, never mid-typing.
   - Honesty rule in system prompt: never claim an action was done unless the tool result says so; say "I don't know" when unsure.
   - Streaming: flush to TTS at each sentence boundary while the model keeps generating.
   - Persona prompt: natural speech, varied tone, no "sir"/greeting templates, no filler hooks.
3. **Token savings**: gate first, short rolling context, memory retrieval (top-k notes only), cache, small model for routing, thinking only on complex tasks.
4. **Computer control** (hidden): keyboard/mouse via `ydotool` (Wayland, needs uinput), terminal via subprocess, screen via screenshot on demand (not continuous) sent to Gemini vision.
5. **Memory**: Obsidian vault `~/Documents/Jeb` (vault name Jeb): daily notes, facts, people, projects; graph links between notes; daemon appends and updates.
6. **Skills**: expose the Claude Code skills in `~/.claude/skills` and plugins to Jeb as tools (read SKILL.md on demand, not preloaded, to save tokens).

## Needs from you (blockers)
- `sudo` once: `git`, `ydotool`/uinput access, Handy build libs (webkit2gtk, alsa, etc.), Rust + bun to build Handy, Obsidian install.
- Python 3.14 is installed; OpenJarvis needs `>=3.10,<3.14` -> need `uv` (installs 3.13).
- Gemini API key: put it in `~/.config/jeb/.env` as `GEMINI_API_KEY=...` yourself.
- Name: default Jeb, but he answers to any name or none (no fixed wake word). Never addressed as "sir"; no scripted greeting.

## Build order
1. Toolchain (git, uv, rust, bun, system libs). 2. OpenJarvis headless + Gemini. 3. Daemon + gate + streaming TTS. 4. Handy build + patch. 5. Obsidian + vault. 6. Alt key logic (evdev). 7. Computer control. 8. Skills bridge. 9. Systemd user services, hidden at login. 10. Tests for gate (typing, shortcuts, accidental Alt, side conversation).

## Movie behaviour (added)
- No wake word needed. Jeb answers like someone already in the room: speaks on first words, no scripted opener.
- Clap trigger: 2-3 claps detected from mic (energy-spike pattern, no LLM) = "I'm here" response. Camera + screen used as context on demand.
- Inputs: mic, speaker, camera, screen.

## Decisions (update)
- Base loop: study `binRick/jarvis` + `yashkuceriya/Jarvis` and reuse their pipeline code. Handy dropped as STT (use faster-whisper + Silero VAD + openWakeWord-style gating); OpenJarvis stays as the brain.
- TTS (free, no ElevenLabs): **Kokoro** first (light, fast streaming, Apache-2.0), **Chatterbox** (MIT) for expressive/emotion lines if GPU allows; Bark only for laughs/sighs (no streaming). Benchmark time-to-first-audio on this machine before choosing. Verify licences on model cards.
- Name: default "Jeb"; reacts to any name and to none.

## Persona notes (own words, from film research)
- Movie AIs: JARVIS (calm, dry, deadpan, anticipates needs), FRIDAY (Irish-accented, more casual), KAREN (Spider-Man suit, chirpy, user-facing), EDITH (glasses, drones), plus Ultron/Vision as the dark and evolved forms.
- Takeaways: speaks first only when it adds something; short lines; dry wit matched to the user's mood; banter grows casual over time; admits uncertainty; never says "sir" by default; no canned openers.
- Weak research: sources were shallow. Better source = film scripts/fan wikis; do a second pass later.
