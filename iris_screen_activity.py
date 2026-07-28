"""Signals when Iris is actively controlling the screen (mouse/keyboard,
browser automation, running commands) so the GUI can show a visible "I'm
working right now" indicator — a glow around the screen edges (see
ScreenAuraOverlay in iris_gui.py).

Visible by default: any tool that touches the mouse/keyboard/browser lights
the glow up for as long as it runs. The only way to suppress it is an
explicit background/scheduled task (queue_task) — the GUI marks those turns
with background_mode.flag before dispatching them, and this module checks
for that flag so backgrounded work stays invisible as intended.
"""
import contextlib
import os
import threading
import time

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iris_data")
ACTIVE_FLAG = os.path.join(_DATA_DIR, "ai_active.flag")
BACKGROUND_FLAG = os.path.join(_DATA_DIR, "background_mode.flag")


def _touch(path: str):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def is_background_mode() -> bool:
    return os.path.exists(BACKGROUND_FLAG)


@contextlib.contextmanager
def active():
    """Wrap any on-screen action (opening apps, browser automation, running
    commands, mouse/keyboard control) with this. Keeps the glow lit for the
    whole duration unless this turn is explicitly running in the background."""
    if is_background_mode():
        yield
        return
    stop = threading.Event()

    def _pulse():
        while not stop.is_set():
            _touch(ACTIVE_FLAG)
            stop.wait(0.5)

    t = threading.Thread(target=_pulse, daemon=True)
    t.start()
    try:
        yield
    finally:
        stop.set()
