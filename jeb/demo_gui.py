"""Feeds fake events to the GUI so the layout can be checked without mic/speaker. Not used in production."""
import time, events
events.serve(); print("http://127.0.0.1:7777", flush=True)
time.sleep(6)
events.emit("model", name="gemini-3.1-flash-lite")
for st, delay in (("listening", 1.5),):
    events.emit("state", state=st); time.sleep(delay)
events.emit("user", text="what's my disk space?"); events.emit("state", state="thinking"); time.sleep(1.2)
events.emit("state", state="acting"); events.emit("tool", name="run_shell", result="exit=0  773G free"); time.sleep(1.2)
events.emit("state", state="speaking")
for t in ("Hang on, checking.", "You've got 773 gigabytes free.", "Plenty of room."):
    events.emit("jeb", text=t); time.sleep(1.1)
events.emit("state", state="idle"); time.sleep(120)
