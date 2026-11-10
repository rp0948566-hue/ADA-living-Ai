# Jev on Linux: parity map

How the Mac app works, and the Linux part that stands in for each piece. The Mac code path is unchanged:
`jev.py` swaps in `linux/jev_linux.py` only when `sys.platform != 'darwin'` (and `JEV_PLATFORM != mac`).

## Architecture (macOS)
1. **Jev.swift `App`**: hotkey, speech, overlay `NSPanel` holding a `WKWebView` with `ui/ui.html`.
   The page posts to `webkit.messageHandlers.h` (its height) and `.c` (events: `send`, `allow`, `pick`, `copy`, `link`, `ready`, …).
   Swift calls the page as `ui.<fn>(...json)` (`callJS`, Jev.swift:869).
2. **Ask worker**: `spawn()` (Jev.swift:3986) starts `sh jev.py --wait` with env `JEV_UI=1 JEV_FRONT JEV_SCREEN JEV_COMMIT …`.
   `run()` writes `go` to the commit file, then one JSON line `{"front","task",…}` to stdin.
3. **Worker output**, one line each: `✓ answer` · `! msg` · `! setup` · `? q\tcmd\tanswerFile[\t…]` (Allow card, reply `y`/`n` into answerFile) ·
   `◇ {choices}` · `✎ {drawing}` · `@ point` · `▣ {window}` · `⇢ {}` · `⤴ {agent brief}` · `↺ {rewrite}` · `⚙ key value` · plain = progress line.
4. **Brain `jev.py`**: runs `claude -p` (or Devin/Pi) with `SYSTEM` (jev.py:499) and helper commands (`--look --place --show --hands --web --window …`).
   A custom server = `ANTHROPIC_BASE_URL` (jev.py:431).
5. **Native verbs** the brain calls as `$JEV_APP <verb>`: `--window-target --target-app --system-ui --raise --look --text --type --draw-target --calendar --hands`.

## Linux stand-ins
| Mac | Linux | Status |
|---|---|---|
| AppKit windows, CGWindowList, NSScreen | `linux/wm.py`: wmctrl/xdotool/xrandr; AT-SPI list on Wayland (child process: libatspi aborts on a missing bus) | done |
| `osa()`, `screens()`, `front()`, `place()`, `look()`, `notify()`, app lookup | `linux/jev_linux.py` `install()` | done, same receipts |
| `open`, `mdfind`, `pbpaste/pbcopy`, `say`, `trash`, `osascript` the model types | `linux/bin/*` on PATH | done |
| `trash` (Finder Trash) | `linux/bin/trash`: gio Trash, each item renamed "<name> (deleted by Jev - <request>)", `--why`/`--by` override; Restore keeps the original name | done |
| Screen Recording | `linux/shot.py`: GNOME/KDE Screenshot portal (the desktop asks once, "Allow Jev to take screenshots?"); `screentext` OCRs it for the text-only model | done |
| Calendar (EventKit) | `linux/jev_calendar.py`: same JSON as CalendarTool; Jev calendar in ~/.local/share/jev/calendar.json + calendar.ics mirror to import | done (no GNOME Online Accounts yet) |
| Auto-install | gate: installs/downloads (`pkexec apt-get install`, pip, npm, git clone, curl -o …) skip the card (pref `autoInstall`); sudo denied, `| sh` and uploads still ask | done (Linux + Mac brain) |
| System monitor | `linux/sysmon.py`: `sysinfo` tool + host background alerts (CPU/RAM/swap/disk/temps/GPU/battery), notify-send + spoken | done (Linux only) |
| Read-aloud voice (AVSpeech) | `linux/voice.py` + `linux/bin/say`: neural Piper, offline, deep natural male (en_US-ryan-medium); tone presets normal/calm/deep/fast/soft; falls back to spd-say/espeak-ng; `voiceName`/`voiceTone`/`voicePitch` (pitch needs sox) settings | done |
| Voice clone (ElevenLabs-style) | `linux/voice_clone.py`: Coqui XTTS v2 clones a voice from a ~6-20s sample; optional, not installed by default (PyTorch + model ~2 GB, slow on CPU); `voice_clone.py add/say/list` | scaffold done; heavy install gated |
| AI client: Nvidia / Gemini API | same `local` client (`run_local`); set `apiBase` + `apiKey` + `apiModel` in settings. Nvidia: `https://integrate.api.nvidia.com/v1`; Gemini: `https://generativelanguage.googleapis.com/v1beta/openai`. Local-only fields are not sent to hosted APIs | ready, untested with real keys |
| Browser agent (web()) | `linux/browser.py` via Playwright over CDP: own visible Brave/Chromium window (watch + take over) or the user's own browser (`browser yours`, they start it with --remote-debugging-port); `browser open/read/click n/fill n/type-after/back/hide/show`, numbered controls like the Mac | done (needs playwright + a Chromium browser) |
| Root commands (`sudo`) | gate: `sudo <apt/dnf/pacman/snap/flatpak/systemctl/dpkg/pkexec>` allowed when pref `sudo` on (set by `install.sh --sudo`, which also adds sudoers `timestamp_timeout` so the OS caches the password); `sudo rm/dd/tee/bash/su` and `-S`/`-A` stay denied. Jev never sees or stores the password | done (Linux) |
| Swift CLI verbs | `linux/native` | done except `--hands`, `--calendar`, `--draw-target` |
| `Hands` (AX see/click/menu/type, ~1400 lines) | `linux/hands.py` via AT-SPI | stub |
| `App` overlay, `spawn()/run()` | `linux/host.py` (GTK3+WebKit2 box: same ui.html, h/c bridge, `ui.*` calls, spawn() line parser) + `linux/worker.py` | done (typed asks, Allow/choices cards, ✕/Esc/drag/resize, fades) |
| Hotkey ⌃⌥Space | GNOME custom shortcut → `host.py --toggle` (UNIX socket); `linux/install.sh` | done; run `sh linux/install.sh` once |
| Speech in (Whisper) | `linux/listen.py`: faster-whisper small (CPU int8), live words, a 1.3 s pause sends; hotkey or mic button toggles | done |
| Read aloud (`say`) | `linux/bin/say` → spd-say; `deliver()` in host.py, Esc stops it | done |
| Hands | `linux/hands.py`: see/click/menu/type over AT-SPI labels; press/scroll/typing through a uinput keyboard+mouse (Wayland-safe); the box steps aside (`blur`) before keys | done; `drag` (absolute uinput pointer), `scroll-to`, `type-after` (AT-SPI insert_text) |
| Dock icon | `linux/jev.png` (from AppIcon.icns) + `~/.local/share/applications/jev.desktop`, pinned by install.sh | done |
| AI client | 4th client `local` in jev.py (`run_local`): Jev's own prompt + one bash tool to an OpenAI-style server, every call through `--gate` | done, `tests/test_linux_local.py` |
| Settings/onboarding/agents pages | same HTML in WebKitGTK (`linux/panes.py`; open with `host.py --settings/--setup/--agents`) | done. Not ported: meetings/whisper-model UI (notice), shortcut recorder (set a GNOME custom shortcut to `jev --toggle`), live mini-screen (text only), agent swim animation |
| Sound cues | `linux/cues.py`, freedesktop theme sounds via paplay/pw-play, same 4 cue prefs | done |
| Hotkey, speech, wake word | GNOME custom shortcut to a socket; faster-whisper; wake word = `listen.py wake <name>` (utterance VAD + whisper, name match) | done; hands-free 90 s idle fade and follow-up not ported |
| System prompt says Mac/AppleScript/mdfind | Linux wording | todo |

## Known limits
- GNOME Wayland does not let apps move or read native windows; placement says NOT DONE there. "Ubuntu on Xorg" gets everything.
- Claude Code rejects non-Claude model names (`unrecognized_model`): leave the model empty so `haiku` passes through.
  Its own prompt is ~20k tokens, which a 4096-token llama-server cannot hold.
- Mac regression tests: `JEV_PLATFORM=mac python3 -m unittest discover -s tests` (2 failures on Linux before any change).

## Native launcher (Rust)
`launcher/` builds the `jev` binary (`cargo build --release`; `linux/install.sh` does it and copies it to `~/.local/bin/jev`). It is the process the task manager shows as "Jev", and the dock entry (`jev.desktop`, `StartupWMClass=Jev`) runs it. `jev` opens the box; `jev --toggle|--quit|--settings|--setup|--agents` pass through. The brain is still Python behind it; Windows and macOS builds of the same launcher need only `cargo build` there. Porting the brain to Rust is module by module, not done.

## Voice (final)
Piper Ryan + `voice.deepen()` (pitch -2.5 st, weight, clear 3 kHz, metal comb, faint ring-mod, cold reverb), pace 1.15. The AI steers its own voice: the brain adds `VOICE_STYLE` to the prompt when the host sets `JEV_STREAM=1`, the model writes `{calm} {soft} {deep} {menace} {loud} {fast} {slow}` in its answer, and `voice.Speaker` applies pace/loudness/pitch per piece. The brain streams (`stream_chat`) and prints `~ piece` lines (`SpeechChunks`: first piece after a clause or 5 words), so speech starts while the model is still writing; the final `✓` line has the tags stripped. Gemini runs with `reasoning_effort: none`. Not done: moving windows of Wayland-native apps (`--place` needs an Xorg session or a GNOME extension).

## Agent web + API notes
Safe mode is a setting (`safe`); it is off in this install. The brain tells the model about `linux/bin/browser` (own Brave window, snap profile under `~/snap/brave/common/jev-profile`) next to `--search`/`--read`. Tool output keeps its first 3000 chars (page start), not the last 1500. Gemini: 429 waits and retries up to 3 times; Gemini 3 tool calls pass `thought_signature` back (`stream_chat`). Model in use: `gemini-3.5-flash` (`gemini-2.5-flash` allows 5 calls/min on the free tier; 2.5-flash-lite is closed to new users).
