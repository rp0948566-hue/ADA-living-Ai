"""Shared background/scheduled task queue.

A tiny JSON-file-backed queue that lets Iris (running inside the Hermes MCP
tool process) hand off a task to be executed *later* — either "as soon as
possible, in the background" (when="now") or "at a specific time" (when="in
30 minutes", "5:30 PM", or an ISO timestamp) — without blocking the current
conversation turn.

The GUI process (iris_gui.py) owns the actual execution: a background thread
there polls this file, and when a task comes due, sends it through the same
Hermes chat pipeline as a normal message, then reports the result back into
the chat (and pings the user) when it's done. This module is intentionally
process-agnostic (just reads/writes one JSON file) since the MCP server and
the GUI are two separate Python processes.
"""
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta

QUEUE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iris_data", "scheduled_tasks.json")


def _load() -> list:
    if not os.path.exists(QUEUE_PATH):
        return []
    try:
        with open(QUEUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save(tasks: list):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    tmp = QUEUE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    os.replace(tmp, QUEUE_PATH)


def _parse_when(when: str) -> float:
    """Best-effort parse of a natural "when" string into a unix timestamp.

    Accepts: "now"/"" (immediately), "in N minutes/hours", "HH:MM" (today,
    or tomorrow if that time already passed), or an ISO 8601 timestamp.
    Falls back to "now" if it can't make sense of the input rather than
    erroring out the whole task.
    """
    w = (when or "").strip().lower()
    if not w or w == "now" or w == "asap":
        return time.time()

    m = re.match(r"in\s+(\d+(?:\.\d+)?)\s*(second|minute|hour|day)s?", w)
    if m:
        qty, unit = float(m.group(1)), m.group(2)
        mult = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}[unit]
        return time.time() + qty * mult

    m = re.match(r"^(\d{1,2}):(\d{2})\s*(am|pm)?$", w)
    if m:
        hour, minute, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target.timestamp()

    try:
        return datetime.fromisoformat(when).timestamp()
    except Exception:
        pass

    return time.time()


def queue_task(description: str, when: str = "now") -> dict:
    """Add a task to the queue. Returns the stored task record."""
    task = {
        "id": uuid.uuid4().hex[:10],
        "description": description,
        "when_raw": when,
        "run_at": _parse_when(when),
        "status": "pending",  # pending -> running -> done | failed | cancelled
        "created": time.time(),
        "result": "",
    }
    tasks = _load()
    tasks.append(task)
    _save(tasks)
    return task


def list_tasks() -> list:
    return _load()


def cancel_task(task_id: str) -> bool:
    tasks = _load()
    found = False
    for t in tasks:
        if t["id"] == task_id and t["status"] == "pending":
            t["status"] = "cancelled"
            found = True
    if found:
        _save(tasks)
    return found


def due_tasks() -> list:
    """Pending tasks whose run_at has passed — does NOT mark them running."""
    now = time.time()
    return [t for t in _load() if t["status"] == "pending" and t["run_at"] <= now]


def mark_running(task_id: str) -> bool:
    tasks = _load()
    found = False
    for t in tasks:
        if t["id"] == task_id and t["status"] == "pending":
            t["status"] = "running"
            found = True
    if found:
        _save(tasks)
    return found


def mark_done(task_id: str, result: str, ok: bool = True):
    tasks = _load()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "done" if ok else "failed"
            t["result"] = result
            t["completed"] = time.time()
    _save(tasks)
