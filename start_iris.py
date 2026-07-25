"""J.A.R.V.I.S — one-command launcher (the whole software in one entry point).

Boots everything in order and keeps it running:
  1. Hermes Agent gateway  (the brain + tools + graph memory API @ :8642)
  2. Waits until the brain's health endpoint is live
  3. The J.A.R.V.I.S HUD GUI (sidebar + chat + voice-reactive orb)

Run it with:
    D:\\Jarvis.v3.0-main-main\\.venv\\Scripts\\python.exe start_jarvis.py
or just double-click  start_jarvis.bat

Ctrl+C (or closing the console) shuts the brain back down cleanly.
"""
import os
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
JARVIS_PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
JARVIS_PYW = os.path.join(ROOT, ".venv", "Scripts", "pythonw.exe")
HERMES_DIR = os.path.join(ROOT, "hermes-agent", "hermes-agent")
HERMES_EXE = os.path.join(HERMES_DIR, ".venv", "Scripts", "hermes.exe")
HEALTH_URL = "http://127.0.0.1:8642/health"


def log(msg):
    print(f"[jarvis] {msg}", flush=True)


def brain_is_up():
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    log("Starting J.A.R.V.I.S ...")

    # 1. Brain (Hermes gateway) — skip if something is already answering :8642
    hermes_proc = None
    if brain_is_up():
        log("Brain already running on :8642 — reusing it.")
    else:
        if not os.path.exists(HERMES_EXE):
            log(f"ERROR: Hermes not found at {HERMES_EXE}")
            log("Did the Hermes venv get created? See MEMORY / setup notes.")
            return 1
        log("Booting the brain (Hermes gateway)...")
        hermes_proc = subprocess.Popen(
            [HERMES_EXE, "gateway", "run"],
            cwd=HERMES_DIR,
        )

        # 2. Wait for health (up to ~60s)
        for i in range(60):
            if brain_is_up():
                log("Brain online.")
                break
            time.sleep(1)
        else:
            log("WARNING: brain didn't report healthy in 60s — launching GUI anyway.")

    # 3. GUI (HUD)
    log("Launching the HUD...")
    gui_py = JARVIS_PYW if os.path.exists(JARVIS_PYW) else JARVIS_PY
    gui_proc = subprocess.Popen([gui_py, os.path.join(ROOT, "jarvis_gui.py")], cwd=ROOT)

    log("J.A.R.V.I.S is up. Close the HUD window or press Ctrl+C here to stop.")
    try:
        gui_proc.wait()
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        for p in (gui_proc, hermes_proc):
            if p is not None and p.poll() is None:
                try:
                    p.terminate()
                except Exception:
                    pass
    log("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
