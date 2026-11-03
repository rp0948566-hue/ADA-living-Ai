"""Computer-control tools for Jeb. Every function returns the real outcome as text (never a guess),
so the model can only report what actually happened."""
import asyncio
import datetime as dt
import os
import re
import shutil
import subprocess
import time
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

VAULT = Path.home() / "Documents" / "Jeb"
# Needs a spoken yes from the user first; the model must re-call with confirmed=True.
DANGEROUS = re.compile(r"\brm\s+(-\w*r|-\w*f)|\bmkfs|\bdd\s+.*of=/dev|\bshutdown\b|\breboot\b|\bpoweroff\b|:\(\)\s*\{|>\s*/dev/sd|\bchmod\s+-R\s+7|\bsudo\b|\bgit\s+push\b|\bgit\s+reset\s+--hard", re.I)


def _run(cmd, timeout=30, shell=False):
    try:
        r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        out = (r.stdout + r.stderr).strip()
        return f"exit={r.returncode}\n{out[-2500:]}" if out else f"exit={r.returncode} (no output)"
    except subprocess.TimeoutExpired:
        return f"timed out after {timeout}s"
    except Exception as e:
        return f"error: {e}"


def run_shell(command: str, confirmed: bool = False, timeout: int = 30) -> str:
    """Run a shell command in the user's home directory and return its exit code and output.
    Commands that delete, reboot, push or use sudo need the user's spoken confirmation first:
    ask them, then call again with confirmed=True."""
    if DANGEROUS.search(command) and not confirmed:
        return "NOT RUN: this could be destructive. Ask the user out loud to confirm, then call again with confirmed=True."
    return _run(command, timeout, shell=True)


def open_app(name: str) -> str:
    """Launch a desktop application by name (e.g. 'firefox', 'obsidian', 'steam')."""
    n = name.strip().lower()
    running = subprocess.run(["pgrep", "-ix", n], capture_output=True).returncode == 0
    prefix = f"{n} was already running; asked it to come forward. " if running else ""
    if shutil.which("gtk-launch"):
        r = subprocess.run(["gtk-launch", n], capture_output=True, text=True)
        if r.returncode == 0:
            return prefix + "launched via desktop entry"
    exe = shutil.which(n)
    if exe:
        subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return prefix + f"started {exe}"
    return f"could not find an application called '{name}'"


def open_url(url: str) -> str:
    """Open a web address in the default browser."""
    if not re.match(r"^https?://", url):
        return "refused: only http(s) URLs"
    subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return "opened in default browser"


def _yd(*args):
    if not shutil.which("ydotool"):
        return "ydotool is not installed"
    r = _run(["ydotool", *args], 10)
    if "exit=0" not in r:
        return "input failed (is ydotoold running and are you in the 'input' group after re-login?): " + r
    return "done"


def type_text(text: str) -> str:
    """Type text into whatever window has focus."""
    return _yd("type", "--key-delay", "8", "--", text)


def press_keys(keys: str) -> str:
    """Press a key combo using Linux key names, e.g. 'ctrl+l' or 'alt+tab' or 'enter'."""
    from evdev import ecodes
    codes = []
    for k in keys.lower().split("+"):
        code = getattr(ecodes, "KEY_" + {"ctrl": "LEFTCTRL", "alt": "LEFTALT", "shift": "LEFTSHIFT",
                                         "super": "LEFTMETA", "win": "LEFTMETA", "esc": "ESC"}.get(k.strip(), k.strip().upper()), None)
        if code is None:
            return f"unknown key '{k}'"
        codes.append(code)
    seq = [f"{c}:1" for c in codes] + [f"{c}:0" for c in reversed(codes)]
    return _yd("key", *seq)


def click_at(x: int, y: int, button: str = "left") -> str:
    """Move the mouse to absolute screen pixel (x, y) and click. button: left, right or double."""
    b = {"left": "0xC0", "right": "0xC1"}.get(button, "0xC0")
    r = _yd("mousemove", "--absolute", "-x", str(x), "-y", str(y))
    if r != "done":
        return r
    out = _yd("click", b)
    if button == "double" and out == "done":
        out = _yd("click", b)
    return out


async def _portal_shot() -> str:
    from dbus_fast import Variant
    from dbus_fast.aio import MessageBus
    bus = await MessageBus().connect()
    intro = await bus.introspect("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop")
    iface = bus.get_proxy_object("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop", intro).get_interface("org.freedesktop.portal.Screenshot")
    fut = asyncio.get_event_loop().create_future()
    token = "jeb" + dt.datetime.now().strftime("%H%M%S%f")
    sender = bus.unique_name[1:].replace(".", "_")
    path = f"/org/freedesktop/portal/desktop/request/{sender}/{token}"

    def on_msg(m):
        if m.path == path and m.member == "Response" and not fut.done():
            fut.set_result(m.body)
        return False
    bus.add_message_handler(on_msg)
    from dbus_fast import Message
    await bus.call(Message(destination="org.freedesktop.DBus", path="/org/freedesktop/DBus",
                           interface="org.freedesktop.DBus", member="AddMatch", signature="s",
                           body=[f"type='signal',path='{path}',interface='org.freedesktop.portal.Request'"]))
    await iface.call_screenshot("", {"handle_token": Variant("s", token), "interactive": Variant("b", False)})
    code, results = await asyncio.wait_for(fut, 30)
    if code != 0:
        raise RuntimeError("screenshot denied or cancelled")
    return unquote(urlparse(results["uri"].value).path)


def take_screenshot() -> str:
    """Capture the screen to a PNG file and return its path (or an error)."""
    try:
        return asyncio.run(_portal_shot())
    except Exception as e:
        return f"screenshot failed: {e}"


def look_at_screen(question: str = "Describe what is on the screen.") -> str:
    """Take a screenshot and answer a question about what is visible on it."""
    p = take_screenshot()
    if not p.startswith("/"):
        return p
    from google import genai
    from google.genai import types
    c = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    img = Path(p).read_bytes()
    r = c.models.generate_content(model="gemini-2.5-flash", contents=[
        types.Part.from_bytes(data=img, mime_type="image/png"), question + " Be brief and factual. Only describe what you can see."])
    return r.text.strip()


def find_files(name_contains: str, folder: str = "~") -> str:
    """Find files or folders whose name contains some text, searching under a folder (default: home), up to 5 levels deep."""
    root = Path(folder).expanduser()
    q = name_contains.lower()
    hits = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".venv")]
        if dp[len(str(root)):].count(os.sep) >= 5:
            dn[:] = []
        for n in dn + fn:
            if q in n.lower():
                hits.append(str(Path(dp) / n))
                if len(hits) >= 15:
                    return "\n".join(hits)
    return "\n".join(hits) or f"nothing named like '{name_contains}' under {root}"


def remember(topic: str, fact: str) -> str:
    """Save a lasting fact about the user, a person or a project into Jeb's Obsidian memory."""
    safe = re.sub(r"[^\w \-]", "", topic).strip()[:60] or "Misc"
    f = VAULT / "Facts" / f"{safe}.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    if not f.exists():
        f.write_text(f"# {safe}\nSee [[Jeb]]\n\n")
    with f.open("a") as fh:
        fh.write(f"- {dt.date.today()}: {fact}\n")
    return f"saved to Facts/{safe}"


import functools
import sys

import events
import indexer


RESULTS: list[str] = []  # tool outcomes this turn, so a failed follow-up call can still report the truth


def _logged(fn, record=True):
    @functools.wraps(fn)
    def w(*a, **k):
        events.emit("state", state="acting")
        r = fn(*a, **k)
        events.emit("tool", name=fn.__name__, result=str(r)[:200])
        if record:  # background workers must not touch the foreground turn's honesty record
            RESULTS.append(f"{fn.__name__}: {str(r)[:120]}")
        print(f"[tool] {fn.__name__}{a}{k} -> {str(r)[:150]!r}", file=sys.stderr, flush=True)
        return r
    return w


def system_status() -> str:
    """One fast call for laptop usage: CPU, memory (RAM), disk, GPU, battery, temperature. Use this for any 'how is my laptop doing' question; never several shell commands."""
    out = []
    try:
        a = [int(x) for x in open("/proc/stat").readline().split()[1:]]
        import time as _t; _t.sleep(0.2)
        b = [int(x) for x in open("/proc/stat").readline().split()[1:]]
        d = [y - x for x, y in zip(a, b)]
        out.append(f"CPU {100 * (1 - (d[3] + d[4]) / max(1, sum(d))):.0f}% busy, {os.cpu_count()} cores")
    except Exception:
        pass
    try:
        m = {k: int(v.split()[0]) for k, v in (l.split(":") for l in open("/proc/meminfo"))}
        out.append(f"RAM {(m['MemTotal'] - m['MemAvailable']) / 1048576:.1f} of {m['MemTotal'] / 1048576:.1f} GB used")
    except Exception:
        pass
    u = shutil.disk_usage(os.path.expanduser("~"))
    out.append(f"disk {u.free / 1e9:.0f} GB free of {u.total / 1e9:.0f} GB")
    try:
        g = subprocess.run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        g = ""
    if "," in g:
        n, ut, mu, mt, tp = [x.strip() for x in g.splitlines()[0].split(",")][:5]
        out.append(f"GPU {n} {ut}% busy, video memory {int(mu) / 1024:.1f} of {int(mt) / 1024:.1f} GB, {tp} degrees")
    for bat in Path("/sys/class/power_supply").glob("BAT*"):
        try:
            out.append(f"battery {(bat / 'capacity').read_text().strip()}% {(bat / 'status').read_text().strip().lower()}")
        except OSError:
            pass
    return "; ".join(out)


def show_map(place: str = "") -> str:
    """Open Jeb's live world map window (real satellite imagery, live flights). Optional place name to fly to, e.g. 'Paris' or 'Heathrow airport'."""
    if events.subscribers() < 2:  # the daemon's own GUI page counts as one; the desktop app is the other
        return "the map app is not running, so nothing was opened"
    events.emit("map", action="show", query=place.strip())
    return f"map opened{' at ' + place if place else ''}"


def hide_map() -> str:
    """Close Jeb's world map window."""
    events.emit("map", action="hide", query="")
    return "map hidden"


def narrate_airspace() -> str:
    """Pull the live worldwide air traffic snapshot and return hard facts for a cinematic briefing (counts, countries, fastest, highest). Narrate only these facts."""
    d = events._fetch("global", "https://opensky-network.org/api/states/all", 900, 30)
    if not d or not d.get("states"):
        return "live air traffic feed unavailable right now"
    air = [s for s in d["states"] if not s[8] and s[5] is not None and s[6] is not None]
    from collections import Counter
    top = Counter(s[2] for s in air).most_common(3)
    fast = max((s for s in air if s[9] and s[9] < 350), key=lambda s: s[9])
    high = max((s for s in air if s[7] and s[7] < 15500), key=lambda s: s[7])
    age = max(0, int(time.time() - d.get("time", time.time())))
    return (f"snapshot {age}s old from OpenSky. {len(air)} aircraft airborne worldwide. "
            f"Busiest registrations: {', '.join(f'{c} {n}' for c, n in top)}. "
            f"Fastest: {fast[1].strip() or fast[0]} at {fast[9] * 3.6:.0f} km/h over {fast[2]}. "
            f"Highest: {high[1].strip() or high[0]} at {high[7]:.0f} m. "
            f"{sum(1 for s in air if (s[7] or 0) > 10000)} are above 10 km.")


BASE = (show_map, hide_map, narrate_airspace, system_status, run_shell, open_app, open_url, find_files, indexer.search_code, indexer.read_file, type_text, press_keys, click_at, look_at_screen, remember)
TOOLS = [_logged(f) for f in BASE]
WORKER_TOOLS = [_logged(f, record=False) for f in BASE]


import worker  # noqa: E402  (after TOOLS: worker imports controller.WORKER_TOOLS)
TOOLS += [_logged(worker.start_task), _logged(worker.task_status)]
