"""IRIS — one-command launcher (the whole software in one entry point).

Boots everything in order and keeps it running:
  1. Hermes Agent gateway  (the brain + tools + graph memory API @ :8642)
  2. Waits until the brain's health endpoint is live
  3. The IRIS HUD GUI (sidebar + chat + voice-reactive orb)

Run it with:
    D:\\Jarvis.v3.0-main-main\\.venv\\Scripts\\python.exe start_iris.py
or just double-click  start_iris.bat

Ctrl+C (or closing the console) shuts the brain back down cleanly.
"""
import os
import subprocess
import sys
import threading
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


class GatewaySupervisor:
    """Keeps the Hermes gateway running. It's been observed to exit on its
    own after 10-20 minutes (unrelated to anything Jarvis-side — seen even
    while idle) with nothing logged as a clean shutdown, which silently
    kills chat until someone notices and relaunches by hand. This watches
    the process and brings it straight back up instead."""

    def __init__(self):
        self._stop = threading.Event()
        self._proc = None
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.terminate()
            except Exception:
                pass

    def _spawn(self):
        log("Booting the brain (Hermes gateway)...")
        self._proc = subprocess.Popen([HERMES_EXE, "gateway", "run"], cwd=HERMES_DIR)
        for _ in range(60):
            if self._stop.is_set():
                return
            if brain_is_up():
                log("Brain online.")
                return
            time.sleep(1)
        log("WARNING: brain didn't report healthy in 60s.")

    def _run(self):
        if brain_is_up():
            log("Brain already running on :8642 — reusing it.")
        else:
            self._spawn()

        while not self._stop.is_set():
            time.sleep(5)
            if self._stop.is_set():
                return
            proc_died = self._proc is not None and self._proc.poll() is not None
            if proc_died or not brain_is_up():
                if not brain_is_up():
                    log("Brain stopped responding — restarting it...")
                    self._spawn()


def main():
    log("Starting J.A.R.V.I.S ...")

    if not os.path.exists(HERMES_EXE):
        log(f"ERROR: Hermes not found at {HERMES_EXE}")
        log("Did the Hermes venv get created? See MEMORY / setup notes.")
        return 1

    # 1. Brain (Hermes gateway) — supervised, auto-restarts if it dies.
    supervisor = GatewaySupervisor()
    supervisor.start()
    for _ in range(60):
        if brain_is_up():
            break
        time.sleep(1)

    # 2. GUI (HUD)
    log("Launching the HUD...")
    gui_py = JARVIS_PYW if os.path.exists(JARVIS_PYW) else JARVIS_PY
    gui_proc = subprocess.Popen([gui_py, os.path.join(ROOT, "iris_gui.py")], cwd=ROOT)

    log("J.A.R.V.I.S is up. Close the HUD window or press Ctrl+C here to stop.")
    try:
        gui_proc.wait()
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        supervisor.stop()
        if gui_proc.poll() is None:
            try:
                gui_proc.terminate()
            except Exception:
                pass
    log("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
