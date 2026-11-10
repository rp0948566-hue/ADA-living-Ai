# Jev-X: Linux, Windows and macOS

Cross-platform port of the Jev idea: say a task, a local LLM drives your computer.
The original macOS app (`Jev.swift`, `jev.py`) is untouched; `jev_x/` is a separate, stdlib-only Python package.

| Piece | File |
|---|---|
| OS control (shell, files, windows, mouse, keys, clipboard, screenshot, notify) | `jev_x/osctl.py` |
| Tool schemas + dispatcher | `jev_x/tools.py` |
| Model client (any OpenAI-compatible server) | `jev_x/llm.py` |
| Agent loop | `jev_x/agent.py` |
| CLI, web UI | `jev_x/__main__.py`, `jev_x/web.py` |

## Run
1. Model: `./start-local-model.sh` (llama.cpp + the Qwen 27B GGUF; skips if a server is already on port 8089).
2. Install: `./install-linux.sh` or `.\install-windows.ps1`. Prints a capability table and checks the model.
3. Use: `python3 -m jev_x "open the calculator"`, `python3 -m jev_x` (chat), `python3 -m jev_x --serve` (browser UI on 127.0.0.1:7777).

## Switch to an API later
No code change. Set `~/.config/jev-x/config.json` (or env `JEV_X_BASE_URL`, `JEV_X_API_KEY`, `JEV_X_MODEL`) to any OpenAI-compatible endpoint.

## Access
Full: shell, file read/write, GUI input. Only catastrophic commands (`rm -rf /`, `mkfs`, `dd` to a disk, shutdown, fork bomb) are blocked; `JEV_X_UNSAFE=1` removes that. The web UI binds to 127.0.0.1 only.

## Limits
- The model is text-only: it cannot see screenshots, so it drives GUIs through `windows`, `shell` and keys.
- Wayland: mouse/keys need `ydotool` (with its daemon) or XWayland apps with `xdotool`; screenshots need `grim` or `scrot`.
- Windows and macOS backends are written but untested; only Linux was run.
- Not ported: the Swift overlay, hotkey, wake word, Whisper dictation, meetings, learned shortcuts. Test: `python3 -m unittest tests_x.test_jev_x`.
