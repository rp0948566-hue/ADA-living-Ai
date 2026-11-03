"""Background task worker: Jeb's voice stays free while a separate agent loop does multi-step jobs.
start_task() returns at once; the finished (or failed) result is queued in DONE for the daemon to speak."""
import itertools
import queue
import threading
import time

from google import genai
from google.genai import types

import controller
import events

TASKS: dict[int, dict] = {}
DONE: queue.Queue = queue.Queue()
_ids = itertools.count(1)
MODELS = ("gemini-2.5-flash", "gemini-3.1-flash-lite", "gemini-flash-lite-latest")
INSTRUCTION = """You are Jeb's background worker on the user's Linux laptop. Finish the task using your tools, then reply in one to three short spoken sentences in Jeb's voice: plain, no markdown, no lists, never say "sir".
Report only what tool results actually show. If a step failed or you could not finish, say exactly what failed. Never claim success you did not see. If the task needs the user's decision or a destructive action, stop and say what you need to ask."""


def _run(tid: int, goal: str, client):
    t = TASKS[tid]
    cfg = types.GenerateContentConfig(
        system_instruction=INSTRUCTION, tools=controller.WORKER_TOOLS, max_output_tokens=500,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(maximum_remote_calls=12))
    err = "no model reachable"
    for model in MODELS:
        try:
            r = client.models.generate_content(model=model, contents=goal, config=cfg)
            t.update(status="done", result=(r.text or "").strip() or "The task ended without a report.", model=model)
            break
        except Exception as e:
            err = str(e)[:160]
    else:
        t.update(status="failed", result=f"The task failed: {err}")
    t["ended"] = time.time()
    events.emit("task", id=tid, status=t["status"], text=t["result"])
    DONE.put((tid, t["status"], t["result"]))


_client = None


def init(api_key: str):
    global _client
    _client = genai.Client(api_key=api_key)


def start_task(goal: str) -> str:
    """Start a longer multi-step job in the background (installs, builds, research, file work) and return immediately.
    The result is spoken to the user when it finishes. Use it when the job needs more than one or two quick tool calls."""
    if _client is None:
        return "worker not initialised"
    tid = next(_ids)
    TASKS[tid] = {"goal": goal, "status": "running", "result": "", "started": time.time()}
    events.emit("task", id=tid, status="running", text=goal)
    threading.Thread(target=_run, args=(tid, goal, _client), daemon=True).start()
    return f"started task {tid} in the background"


def task_status() -> str:
    """List background tasks with their real status and results."""
    if not TASKS:
        return "no tasks"
    return "\n".join(f"#{i} [{t['status']}] {t['goal'][:60]} -> {t['result'][:100]}" for i, t in TASKS.items())
