# Vovy 0.5.8 — clean-room spec + data-egress audit (static analysis only)

## Size
main/index.js 6.5 MB, 136,949 lines (bundled, no source maps shipped), preload 142 KB, renderer ~25 chunks (UI, xterm, rive animations), 378 IPC handlers, ~55 distinct tool names (calendar, mail, notes, obsidian, music, messages, files, finance/shop analytics, teams/outlook/onedrive...).

## Where it talks to the network (what we must NOT reproduce)
- Their Supabase project (functions + storage, auth, downloads) — 41 refs
- PostHog analytics — 284 analytics refs; Sentry error reporting — 149 refs
- vovy.ai (accounts, plans, learn/courses)
- OpenAI realtime voice (api.openai.com) — the voice brain; your audio goes to OpenAI
- Google APIs (Gmail/Calendar/Drive tools), Firebase
=> Jeb sends none of this: no analytics, no Sentry, no Vovy account. Audio stays local (faster-whisper); text goes only to Gemini/Ollama that you control.

## Features worth rebuilding on Linux/Windows (our own code)
1. Push-to-talk + 8 s conversation window  (done in gate.py)
2. Promise = tool call; hollow promises corrected (done: gate.hollow_promise, tested)
3. Context blocks [now]/[memory]/[screen] as data (done)
4. start_task background worker so voice stays free (TODO)
5. Circle-to-ask / screen guidance overlay (TODO, needs GUI)
6. Floating character + notch "island" overlay (GUI — own art needed)
7. Tools: calendar/mail/notes/music via Linux equivalents (MPRIS for music, Obsidian vault, local notes; mail/calendar via your Gmail connector later)
8. Terminal watch, browser automation (playwright works on Linux), screen perception wait-for-change

## Mac-only parts and the Linux/Windows replacement
AppleScript (131 refs) -> D-Bus/MPRIS/xdg tools on Linux, PowerShell/COM on Windows. Accessibility helper `vovy-ax` -> AT-SPI on Linux, UI Automation on Windows. nut-js works on both for mouse/keyboard (Wayland needs ydotool/uinput).
