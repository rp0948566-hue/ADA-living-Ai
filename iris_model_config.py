"""Ollama auto-detect + Hermes model-provider switching for Iris.

Lets Iris (both the AI itself, via MCP tools, and Vikash sir, via the GUI
dropdown) discover locally installed Ollama models and flip Hermes between
"local" (Ollama — free, private, no API key) and "cloud" (OpenRouter/etc)
by editing %LOCALAPPDATA%\\hermes\\config.yaml directly, without touching
anything else already in that file.

Also owns the two persistent, visibly-named terminal windows Iris runs in:
  - "IRIS - AI Command Terminal"  → every run_command call executes here
  - "IRIS - Local AI Mode (...)"  → hosts the Hermes gateway / local brain

Switching modes kills whichever gateway is running (old mode "turns off",
closing its terminal) and opens a fresh one for the newly selected model.
"""
import json
import os
import re
import subprocess
import time
import urllib.request

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
HERMES_HEALTH_URL = "http://127.0.0.1:8642/health"

_CONFIG_PATH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "config.yaml")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
HERMES_DIR = os.path.join(PROJECT_ROOT, "hermes-agent", "hermes-agent")
HERMES_EXE = os.path.join(HERMES_DIR, ".venv", "Scripts", "hermes.exe")
TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")
DATA_DIR = os.path.join(PROJECT_ROOT, "iris_data")
CMD_QUEUE_DIR = os.path.join(DATA_DIR, "cmd_queue")

_MODEL_BLOCK_RE = re.compile(r"^model:[ \t]*\n((?:[ \t]+.+\n?)+)", re.MULTILINE)


# ---------------------------------------------------------------- model config

def list_ollama_models() -> list:
    """Auto-detect models installed locally via `ollama list`."""
    try:
        out = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=10,
        )
        lines = [l for l in out.stdout.splitlines()[1:] if l.strip()]
        return [l.split()[0] for l in lines]
    except Exception:
        return []


def get_current_model() -> dict:
    """Parse whatever `model:` block is currently active in config.yaml."""
    info = {"default": None, "provider": None, "base_url": None, "path": _CONFIG_PATH}
    if not os.path.exists(_CONFIG_PATH):
        return info
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    m = _MODEL_BLOCK_RE.search(text)
    if not m:
        return info
    block = m.group(1)
    for key in ("default", "provider", "base_url"):
        km = re.search(rf'^\s*{key}:\s*"?([^"\n]+?)"?\s*$', block, re.MULTILINE)
        if km:
            info[key] = km.group(1).strip()
    return info


def _write_model_block(new_block: str):
    text = ""
    if os.path.exists(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        os.makedirs(os.path.dirname(_CONFIG_PATH), exist_ok=True)
    if _MODEL_BLOCK_RE.search(text):
        text = _MODEL_BLOCK_RE.sub(new_block, text, count=1)
    else:
        text = new_block + "\n" + text
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(text)


def set_local_model(model_name: str) -> str:
    """Point Hermes at a local Ollama model — free, private, no API key."""
    _write_model_block(
        f'model:\n'
        f'  default: "{model_name}"\n'
        f'  provider: "ollama"\n'
        f'  base_url: "{OLLAMA_BASE_URL}"\n'
    )
    return f"Hermes ab local model '{model_name}' use karega (Ollama @ {OLLAMA_BASE_URL})."


def set_cloud_model(model_name: str, provider: str = "openrouter") -> str:
    """Point Hermes back at a cloud provider (OpenRouter, etc)."""
    _write_model_block(
        f'model:\n'
        f'  default: "{model_name}"\n'
        f'  provider: "{provider}"\n'
    )
    return f"Hermes ab cloud model '{model_name}' use karega (via {provider})."


# ---------------------------------------------------------------- process helpers

def _is_pid_alive(pid: int) -> bool:
    if not pid:
        return False
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True, timeout=5,
        )
        return str(pid) in out.stdout
    except Exception:
        return False


def is_ollama_up() -> bool:
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_URL, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def is_hermes_up() -> bool:
    try:
        with urllib.request.urlopen(HERMES_HEALTH_URL, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def kill_hermes_gateway():
    """Turn the currently running mode OFF (closes its terminal window too,
    since that window's only job was hosting this process)."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "hermes.exe"], capture_output=True)
    except Exception:
        pass


# ---------------------------------------------------------------- AI Command Terminal

_AI_TERM_PID_FILE = os.path.join(DATA_DIR, "ai_cmd_terminal.pid")


def ensure_ai_command_terminal() -> str:
    """Make sure the persistent "IRIS - AI Command Terminal" window is
    running. Every run_command call is routed into this single window
    instead of popping a fresh console per command."""
    os.makedirs(CMD_QUEUE_DIR, exist_ok=True)
    pid = None
    if os.path.exists(_AI_TERM_PID_FILE):
        try:
            pid = int(open(_AI_TERM_PID_FILE).read().strip())
        except Exception:
            pid = None
    if pid and _is_pid_alive(pid):
        return f"AI Command Terminal already running (pid {pid})."

    script = os.path.join(TOOLS_DIR, "ai_cmd_watcher.ps1")
    proc = subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script],
        cwd=PROJECT_ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    with open(_AI_TERM_PID_FILE, "w") as f:
        f.write(str(proc.pid))
    return f"AI Command Terminal launched (pid {proc.pid})."


def run_in_ai_terminal(command: str, timeout: int = 120) -> tuple:
    """Drop a job into the AI Command Terminal's queue and wait for its
    result. Returns (returncode, output)."""
    ensure_ai_command_terminal()
    os.makedirs(CMD_QUEUE_DIR, exist_ok=True)
    job_id = f"{int(time.time()*1000)}_{os.getpid()}"
    job_path = os.path.join(CMD_QUEUE_DIR, f"{job_id}.job")
    result_path = os.path.join(CMD_QUEUE_DIR, f"{job_id}.result")
    with open(job_path, "w", encoding="utf-8") as f:
        f.write(command)

    waited = 0.0
    step = 0.25
    while waited < timeout:
        if os.path.exists(result_path):
            time.sleep(0.05)  # let the writer finish flushing
            try:
                with open(result_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            finally:
                try:
                    os.remove(result_path)
                except Exception:
                    pass
            first_nl = content.find("\n")
            if first_nl == -1:
                return 0, content
            rc_text, output = content[:first_nl], content[first_nl + 1:]
            try:
                rc = int(rc_text.strip())
            except ValueError:
                rc = 0
            return rc, output
        time.sleep(step)
        waited += step

    try:
        os.remove(job_path)
    except Exception:
        pass
    return -1, None  # None output signals timeout to the caller


# ---------------------------------------------------------------- Local AI Mode terminal

_LOCAL_TERM_PID_FILE = os.path.join(DATA_DIR, "local_ai_terminal.pid")


def ensure_local_ai_mode(model_name: str = None, force_restart: bool = False) -> str:
    """Auto-detect whether Hermes (any mode) is already running; if not —
    or if force_restart is set for a mode switch — turn the old mode OFF
    and start the new one in its own titled terminal."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if not force_restart and is_hermes_up():
        return "Local AI mode already running — reusing it."

    kill_hermes_gateway()  # old mode off (also closes its console window)

    if not model_name:
        model_name = get_current_model().get("default") or "unknown"

    script = os.path.join(TOOLS_DIR, "local_ai_watcher.ps1")
    proc = subprocess.Popen(
        [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script,
            "-ModelName", model_name, "-HermesExe", HERMES_EXE, "-HermesDir", HERMES_DIR,
        ],
        cwd=PROJECT_ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    with open(_LOCAL_TERM_PID_FILE, "w") as f:
        f.write(str(proc.pid))
    return f"Local AI mode '{model_name}' starting in its own terminal (pid {proc.pid})."


def switch_local_model(model_name: str) -> str:
    """Full mode switch: write config, turn the old mode off, turn the new
    mode on — in its own terminal, banner and all."""
    msg1 = set_local_model(model_name)
    msg2 = ensure_local_ai_mode(model_name, force_restart=True)
    return f"{msg1} {msg2}"


def switch_cloud_model(model_name: str, provider: str = "openrouter") -> str:
    msg1 = set_cloud_model(model_name, provider)
    msg2 = ensure_local_ai_mode(model_name, force_restart=True)
    return f"{msg1} {msg2}"


# ---------------------------------------------------------------- Colibri (GLM-5.2 744B MoE)

COLIBRI_ENGINE_DIR = os.path.join(PROJECT_ROOT, "colibri_engine")
COLIBRI_MODEL_PATH = r"C:\colibri_models\glm52_i4"
COLIBRI_PORT = 8765
COLIBRI_BASE_URL = f"http://localhost:{COLIBRI_PORT}/v1"
_COLIBRI_TERM_PID_FILE = os.path.join(DATA_DIR, "colibri_terminal.pid")


def colibri_model_status() -> dict:
    """Whether the (huge, ~429GB) colibri model download is present and
    looks complete enough to actually serve — config.json + tokenizer.json
    existing is a reasonable proxy since those are written near the end of
    a snapshot download."""
    present = (
        os.path.isdir(COLIBRI_MODEL_PATH)
        and os.path.exists(os.path.join(COLIBRI_MODEL_PATH, "config.json"))
        and os.path.exists(os.path.join(COLIBRI_MODEL_PATH, "tokenizer.json"))
    )
    return {"present": present, "path": COLIBRI_MODEL_PATH}


def is_colibri_serving_up() -> bool:
    try:
        with urllib.request.urlopen(f"http://localhost:{COLIBRI_PORT}/v1/models", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_colibri_serving(force_restart: bool = False) -> str:
    """Make sure `coli web` (API + live dashboard on one port) is running
    in its own titled terminal — visit http://localhost:8765/ for the
    dashboard once it's up."""
    if not colibri_model_status()["present"]:
        return (
            f"⚠ Colibri model not found/incomplete at {COLIBRI_MODEL_PATH} — "
            "download it first (see hf download instructions), then try again."
        )
    if not force_restart and is_colibri_serving_up():
        return "Colibri mode already running — reusing it."

    try:
        subprocess.run(["taskkill", "/F", "/IM", "colibri.exe"], capture_output=True)
    except Exception:
        pass

    python_exe = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    script = os.path.join(TOOLS_DIR, "colibri_watcher.ps1")
    proc = subprocess.Popen(
        [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script,
            "-PythonExe", python_exe, "-ColibriDir", COLIBRI_ENGINE_DIR,
            "-ModelPath", COLIBRI_MODEL_PATH, "-Port", str(COLIBRI_PORT),
        ],
        cwd=PROJECT_ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    with open(_COLIBRI_TERM_PID_FILE, "w") as f:
        f.write(str(proc.pid))
    return (
        f"🐦 Colibri starting in its own terminal (pid {proc.pid}) — "
        f"dashboard at http://localhost:{COLIBRI_PORT}/ once it's up. "
        "GLM-5.2 744B MoE, streaming from disk. First reply can take a long "
        "time on this hardware (measured ~0.05-0.1 tok/s class)."
    )


def switch_to_colibri_mode() -> str:
    """Full mode switch to colibri — same pattern as switch_local_model, but
    the actual inference server is `coli serve`, not Ollama, so Hermes just
    gets pointed at coli's OpenAI-compatible endpoint like any local model."""
    status = colibri_model_status()
    if not status["present"]:
        return f"⚠ Colibri model not found/incomplete at {status['path']} — can't switch yet."
    msg1 = ensure_colibri_serving(force_restart=True)
    _write_model_block(
        f'model:\n'
        f'  default: "glm-5.2-colibri"\n'
        f'  provider: "ollama"\n'
        f'  base_url: "{COLIBRI_BASE_URL}"\n'
    )
    msg2 = ensure_local_ai_mode("glm-5.2-colibri", force_restart=True)
    return f"{msg1} {msg2}"


def restart_gateway_in_new_terminal(title_suffix: str = "") -> str:
    """Back-compat alias — kept because tools/iris_mcp_server.py and older
    callers referenced this name; now routed through ensure_local_ai_mode."""
    current = get_current_model()
    model_name = title_suffix.split(":")[-1].strip() or current.get("default")
    return ensure_local_ai_mode(model_name, force_restart=True)


def auto_start_if_needed() -> str:
    """Called on GUI startup: auto-detect if any AI mode is already running;
    if not, automatically turn the last-configured one on. Also makes sure
    the AI Command Terminal exists."""
    msgs = [ensure_ai_command_terminal()]
    current = get_current_model()
    model_name = current.get("default")

    if current.get("base_url") == COLIBRI_BASE_URL:
        # last-configured mode was colibri — its inference server is a
        # separate process from the hermes gateway, so both need checking.
        if not colibri_model_status()["present"]:
            msgs.append(
                f"⚠ Last mode was colibri but the model isn't at "
                f"{COLIBRI_MODEL_PATH} — falling back, switch modes manually once it's downloaded."
            )
        else:
            msgs.append(ensure_colibri_serving(force_restart=False))

    if is_hermes_up():
        msgs.append("Brain already online — reusing it.")
    else:
        msgs.append(ensure_local_ai_mode(model_name, force_restart=False))
    return "\n".join(msgs)
