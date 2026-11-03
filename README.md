# Jeb: voice AI assistant + live airspace map (Linux)

Jeb is a voice-driven assistant for a Linux laptop. When you ask for it, a native
desktop app shows a 3D globe with **real, live aircraft** and a small Mac-style notch
drops from the top-centre of the screen while Jeb listens and speaks.

Code lives in two folders of this repo:

| Folder | What | Language |
|---|---|---|
| [`jeb/`](jeb) | Voice daemon: speech-to-text, Gemini brain, tools, text-to-speech, event server | Python |
| [`jeb-ai/`](jeb-ai) | Native app: Tauri shell, Rust data backend, TypeScript UI (globe + notch) | Rust + TypeScript |
| [`jeb/analysis/`](jeb/analysis) | Written analyses of reference demo videos (behaviour/UI notes) | Markdown |
| [`jeb/PLAN.md`](jeb/PLAN.md) | Project plan | Markdown |

The repo root also contains an older, unrelated project (Iris); it is untouched.

## How it works

```
mic -> faster-whisper (STT) -> Gemini brain + tools -> Kokoro TTS -> speakers
                                   |
                         jeb/events.py  (SSE on 127.0.0.1:7777/events)
                                   |
                      jeb-ai (Tauri, Rust)
                        |-- notch window (drops from top, hides when idle)
                        '-- main map window (hidden until Jeb says "show the map")
                              Rust jeb-core pulls live data -> TypeScript/Cesium globe
```

- The map is **not** open by default. Ask Jeb to show the map/data (`show_map` tool); it hides on `hide_map`.
- The notch only drops for speech addressed to Jeb, and retracts ~1.8 s after it finishes.
- `narrate_airspace` gives a cinematic summary using only facts from live data.

## Real data only (no scripted/fake data)

| Source | Used for | Key needed |
|---|---|---|
| OpenSky `/api/states/all` | Global aircraft positions | None (anonymous, ~100 pulls/day, cached 15 min). Optional `OPENSKY_CLIENT_ID` / `OPENSKY_CLIENT_SECRET` for a 10 s refresh |
| adsb.lol `/v2/point/...` | Aircraft type, registration, squawk, Mach near the view | None |
| Planespotters photo API | Aircraft photo by registration | None |
| vrs-standing-data.adsb.lol | Route/schedule by callsign | None |
| Nominatim | Place search ("fly to Paris") | None |
| Esri World Imagery / Boundaries / Transportation / NatGeo | Satellite, labels, roads, light-mode map | None |
| NASA GIBS | Clouds, night lights | None |
| Google Gemini | The brain (required) | `GEMINI_API_KEY` |
| Cesium Ion (optional) | 3D buildings only | Your own token; app runs without it |

Only **one** key is required: `GEMINI_API_KEY`.

## Requirements

**Hardware/OS:** Linux (developed on Ubuntu GNOME, Wayland, NVIDIA RTX 5070 8 GB). The GPU is
optional for the current stack.

**System packages (Debian/Ubuntu):**
```bash
sudo apt install build-essential pkg-config libwebkit2gtk-4.1-dev libgtk-3-dev \
  libayatana-appindicator3-dev librsvg2-dev libssl-dev portaudio19-dev ffmpeg curl
```

**Toolchains:** Rust (stable, via rustup), Node.js 20+ with npm, Python 3.11+.

**Python packages** (in a venv): `faster-whisper`, `kokoro-onnx`, `sounddevice`, `numpy`, `google-genai`.

**Models:** Kokoro `kokoro-v1.0.onnx` and `voices-v1.0.bin` go in `jeb/models/` (not in git; see
`jeb/fetch_local.sh` for the download pattern). Whisper models download on first run.
Optional local fallback: Ollama with `llama3.1:8b`.

## Setup and run

### 1. Voice daemon
```bash
cd jeb
python3 -m venv .venv && source .venv/bin/activate
pip install faster-whisper kokoro-onnx sounddevice numpy google-genai
mkdir -p ~/.config/jeb
echo "GEMINI_API_KEY=your_key_here" > ~/.config/jeb/.env
python daemon.py
```
Optional settings: `JEB_MODEL` (default `gemini-2.5-flash`), `JEB_LOCAL_MODEL`, `JEB_VOICE` (default `bm_george`).

Run it as a background service: create `~/.config/systemd/user/jeb.service` pointing at
`.venv/bin/python daemon.py` with `WorkingDirectory` set to `jeb/`, then
`systemctl --user enable --now jeb.service`.

### 2. Native app
```bash
cd jeb-ai/ui && npm install
cd ../app
../ui/node_modules/.bin/tauri dev                       # development
../ui/node_modules/.bin/tauri build --bundles deb       # .deb installer
```
Debug binary: `jeb-ai/target/debug/jeb-app` (run with `DISPLAY=:0` on Wayland; the app forces
XWayland so the notch can be positioned over the top bar).

### 3. Tests
```bash
cd jeb && pytest                 # gate, indexer, speech tests
cd jeb-ai && cargo test -p jeb-core
cargo run -p jeb-core --example probe    # live data check against OpenSky/adsb.lol
```

## Features

- Globe with satellite imagery, street-level zoom with roads and labels (Esri), clouds and night lights (NASA GIBS).
- Dark and light themes (light = shaded-relief map); toggle persists.
- Live aircraft with dead-reckoning between pulls, heading-rotated icons, trails, projected path,
  route progress, aircraft photo, callsign/type/registration/speed/altitude.
- Notch popup window: centred, top of screen over the GNOME bar (GTK Dock hint), 190x30 idle, 300x70 with text.
- Voice assistant with gating (responds when addressed), memory notes in an Obsidian vault, code search tools.

## Known limits / not done

- Notch placement was verified by window geometry, not visually (Wayland blocks screenshots here).
- Voice and brain are still Python; Rust rewrites (whisper-rs, Gemini client) are not started.
- Chatterbox TTS (MIT) and NVIDIA PersonaPlex are planned, not installed. PersonaPlex needs a Hugging Face token and licence acceptance, 8 GB VRAM requires CPU offload, no tool calling.
- No autostart entry yet; light-mode plane icons are faint on the pale map.
- OpenSky anonymous quota is small; set OpenSky credentials for fresher data.
- Reference repo [Gods-Eye/ShadowBroker](https://github.com/rp0948566-hue/Gods-Eye) is AGPL-3.0; only used as a data-source reference, no code copied.

## Repo layout

```
jeb/            daemon.py controller.py events.py gate.py speech.py indexer.py worker.py gui/ analysis/
jeb-ai/core/    jeb-core Rust crate (live data)
jeb-ai/app/     Tauri app (main.rs, tauri.conf.json, capabilities)
jeb-ai/ui/      TypeScript UI (index.html, notch.html, src/main.ts, src/notch.ts)
```
