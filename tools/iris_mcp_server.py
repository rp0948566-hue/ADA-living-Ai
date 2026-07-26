"""MCP bridge exposing Iris's existing desktop-control code to Hermes Agent.

Runs as a stdio MCP server (spawned by Hermes per its ``mcp_servers`` config
in ``%LOCALAPPDATA%\\hermes\\config.yaml``). Each tool below is a thin
wrapper around the *existing* Iris_*.py implementations — no logic is
duplicated here, only exposed.

Deliberately NOT wrapped here (kept local to the LiveKit voice loop for
instant response): mouse/keyboard/volume control (keyboard_mouse_CTRL.py).

Deliberately NOT wrapped here (Hermes has built-in equivalents already):
web search, screenshots, system info, news.
"""
import asyncio
import json
import os
import subprocess
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP

import Iris_window_CTRL
import Iris_file_opner
import Iris_email
import Iris_youtube_music
import iris_get_whether
import iris_app_index
import iris_graph_memory
import iris_model_config
import iris_vision

mcp = FastMCP(
    "iris-tools",
    instructions=(
        "Controls Vikash sir's Windows desktop and connects it to the web. "
        "Launch/close ANY installed app (discovered dynamically — no hardcoded "
        "paths), run ANY terminal command, scrape web pages with Scrapling, "
        "open/manage files and folders, send email, play/control YouTube, "
        "check weather, and read the live camera view. Use these directly and "
        "confidently. Every terminal command is logged for pattern learning."
    ),
)

TERMINAL_LOG = os.path.join(PROJECT_ROOT, "iris_data", "terminal_history.jsonl")


@mcp.tool()
async def open_app(app_title: str) -> str:
    """Launch any installed application by name (e.g. "notepad", "chrome", "vs code", "claude").

    Apps are discovered dynamically from the Start Menu, registry, and known
    install locations — there is NO hardcoded path list, so anything actually
    installed can be launched. If the name isn't found, falls back to trying
    it as a raw command.

    Args:
        app_title: The app name to launch (fuzzy-matched against installed apps).
    """
    target, matched, score = iris_app_index.resolve_app(app_title)
    if target:
        try:
            os.startfile(target) if os.path.isabs(target) or os.path.exists(target) \
                else subprocess.Popen(target, shell=True)
            return f"🚀 Launched '{matched}' (match {score}%) → {target}"
        except Exception as e:
            return f"❌ Found '{matched}' but launch failed: {e}"
    # fall back to the original shell-based opener
    return await Iris_window_CTRL.open(app_title)


@mcp.tool()
def list_available_apps() -> str:
    """List every application Iris can currently launch on this machine.

    Use this to answer "which apps do you have / is X installed" — it reflects
    what is actually present, discovered live, not a fixed list.
    """
    apps = iris_app_index.list_apps()
    return f"{len(apps)} apps available:\n" + "\n".join(apps)


@mcp.tool()
async def close_window(window_title: str) -> str:
    """Close any open window whose title contains the given text.

    Args:
        window_title: Substring to match against open window titles.
    """
    return await Iris_window_CTRL.close(window_title)


@mcp.tool()
async def folder_file_command(command: str) -> str:
    """Manage folders/files under D:/ using a natural-language command.

    Supports: "create folder <name>", "rename <old> to <new>", "delete <name>",
    "open folder <name>". Falls back to fuzzy file search + open otherwise.

    Args:
        command: The natural-language folder/file command.
    """
    return await Iris_window_CTRL.folder_file(command)


@mcp.tool()
async def play_file(name: str) -> str:
    """Find and open a file anywhere under D:/ by fuzzy name match (video, audio, doc, image, etc).

    Args:
        name: The file name (or close approximation) to search for and open.
    """
    return await Iris_file_opner.Play_file(name)


@mcp.tool()
def send_email(recipient: str, subject: str, message: str) -> str:
    """Send an email via the configured Gmail account.

    Args:
        recipient: A contact name (e.g. "Rudra") or a raw email address.
        subject: Email subject line.
        message: Email body text.
    """
    result = Iris_email.send_email_direct(recipient, subject, message)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def play_youtube(song_name: str) -> str:
    """Play a song/video on YouTube by name.

    Args:
        song_name: What to search for and play on YouTube.
    """
    return Iris_youtube_music.play_youtube_song_sync(song_name)


@mcp.tool()
def control_youtube(command: str) -> str:
    """Control YouTube playback in the active browser tab.

    Args:
        command: One of: pause, play, resume, next, mute, unmute, fullscreen, exit fullscreen.
    """
    return Iris_youtube_music.youtube_control(command)


@mcp.tool()
async def get_weather(city: str = "") -> str:
    """Get the current weather for a city (defaults to the user's detected location).

    Args:
        city: City name, or empty to auto-detect from IP.
    """
    return await iris_get_whether.get_weather(city)


@mcp.tool()
def camera_view() -> str:
    """Read the most recent description of what the desktop's live camera currently sees.

    Camera must already be running (owned by the GUI) for this to be current;
    otherwise returns whatever status/error was last written.
    """
    path = os.path.join(PROJECT_ROOT, "iris_data", "camera_view.txt")
    if not os.path.exists(path):
        return "Camera abhi tak initialize nahi hua hai ya GUI running nahi hai."
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip() or "Camera se koi observation available nahi hai."


@mcp.tool()
def presence_check() -> str:
    """Check whether Rudra is currently sitting in front of the computer,
    and his rough posture (sitting / standing / leaning / moving).

    Backend-only vision context — the face/body tracking behind this never
    renders in the UI (only hand-tracking gestures do); this is purely for
    situational awareness (e.g. "should I greet him", "has he stepped away").
    Requires the GUI's vision engine to be running with camera + face
    recognition + body tracking enabled.
    """
    data = iris_vision.read_presence()
    face = data.get("face", {})
    body = data.get("body", {})
    if not face.get("present") and not body.get("present"):
        return "Rudra abhi camera ke saamne nahi dikh raha — shayad away hai."
    parts = ["Rudra is present in front of the camera."]
    if face.get("distance"):
        parts.append(f"Distance: {face['distance']}.")
    if body.get("posture"):
        parts.append(f"Posture: {body['posture']}.")
    return " ".join(parts)


@mcp.tool()
async def run_command(command: str, timeout: int = 120) -> str:
    """Run ANY command in the dedicated "IRIS - AI Command Terminal" window and return output.

    Every backend command Iris runs shows up live in ONE persistent,
    visibly-named terminal (auto-launched the first time it's needed) — so
    Vikash sir can watch everything the AI does in real time without a new
    window popping up per command. Output is still captured and returned
    here, and every command + output is logged to
    iris_data/terminal_history.jsonl for pattern learning. Runs in the
    project root.

    Args:
        command: The shell command to execute (PowerShell syntax).
        timeout: Max seconds to wait before giving up (default 120).
    """
    started = time.time()
    try:
        rc, text = await asyncio.to_thread(iris_model_config.run_in_ai_terminal, command, timeout)
        if text is None:
            _log_command(command, "", -1, "timeout")
            return f"⏱️ Command timed out after {timeout}s: {command}"
        _log_command(command, text, rc, "ok")
        head = text if len(text) < 6000 else text[:6000] + "\n...(truncated)"
        return f"[exit {rc}] ({time.time()-started:.1f}s)\n{head or '(no output)'}"
    except Exception as e:
        _log_command(command, str(e), -1, "error")
        return f"❌ Command failed: {e}"


def _log_command(command: str, output: str, rc: int, status: str):
    """Append a command record to the history log for pattern learning."""
    try:
        os.makedirs(os.path.dirname(TERMINAL_LOG), exist_ok=True)
        rec = {
            "ts": time.time(),
            "command": command,
            "returncode": rc,
            "status": status,
            "output_preview": (output or "")[:500],
        }
        with open(TERMINAL_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


@mcp.tool()
def command_history(limit: int = 30) -> str:
    """Read recent terminal command history — what Iris has run before.

    Use this to spot patterns (commands Vikash sir runs often) so repetitive
    actions can be anticipated and offered proactively.

    Args:
        limit: How many recent commands to return (default 30).
    """
    if not os.path.exists(TERMINAL_LOG):
        return "No command history yet."
    try:
        with open(TERMINAL_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        recs = [json.loads(l) for l in lines if l.strip()]
        out = []
        for r in recs:
            ts = time.strftime("%m-%d %H:%M", time.localtime(r.get("ts", 0)))
            out.append(f"[{ts}] ({r.get('status')}) {r.get('command')}")
        return "\n".join(out) if out else "No command history yet."
    except Exception as e:
        return f"Could not read history: {e}"


@mcp.tool()
def scrape_web(url: str, css_selector: str = "", max_chars: int = 5000) -> str:
    """Scrape a web page with Scrapling (D4Vinci/Scrapling) — fast, stealthy fetch.

    Returns the page's visible text, or the text of elements matching a CSS
    selector if one is given (e.g. "h1", ".price", "article p"). Use this to
    read/extract content from any website for research.

    Args:
        url: The page URL to scrape.
        css_selector: Optional CSS selector to extract specific elements.
        max_chars: Cap on returned text length (default 5000).
    """
    try:
        from scrapling.fetchers import Fetcher
    except Exception as e:
        return f"❌ Scrapling not available: {e}"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        if page.status >= 400:
            return f"⚠ HTTP {page.status} fetching {url}"
        if css_selector:
            nodes = page.css(css_selector)
            parts = []
            for n in nodes:
                try:
                    parts.append(n.get_all_text(strip=True))
                except Exception:
                    parts.append(str(n))
            text = "\n".join(p for p in parts if p)
        else:
            text = page.get_all_text(strip=True)
        text = text or "(no matching content)"
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...(truncated)"
        return f"[{page.status}] {url}\n\n{text}"
    except Exception as e:
        return f"❌ Scrape failed: {e}"


@mcp.tool()
def scrape_links(url: str, max_links: int = 40) -> str:
    """Extract all hyperlinks (text + href) from a web page via Scrapling.

    Useful for navigating/researching a site — find what pages exist before
    scraping them in detail.

    Args:
        url: The page URL to pull links from.
        max_links: Max links to return (default 40).
    """
    try:
        from scrapling.fetchers import Fetcher
    except Exception as e:
        return f"❌ Scrapling not available: {e}"
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        anchors = page.css("a")
        out = []
        for a in anchors[:max_links]:
            href = a.attrib.get("href", "")
            label = a.get_all_text(strip=True)
            if href:
                out.append(f"{label or '(no text)'} → {href}")
        return "\n".join(out) if out else "No links found."
    except Exception as e:
        return f"❌ Link scrape failed: {e}"


@mcp.tool()
def graph_remember(entities: str = "", relations: str = "") -> str:
    """Save knowledge to Iris's graph memory (auto-organized brain).

    Store facts about Vikash sir and his world as a knowledge graph so they
    persist and stay connected. Call this yourself whenever you learn
    something worth keeping — you don't need to be asked.

    Args:
        entities: newline-separated "name | kind | note" (kind one of:
            person, preference, project, app, fact, place, device, other).
            Example: "Vikash sir | person | primary owner\nHindi | preference |"
        relations: newline-separated "source | relationship | target".
            Example: "Vikash sir | prefers | Hindi\nVikash sir | uses | VS Code"
    """
    out = []
    for line in (entities or "").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if parts and parts[0]:
            name = parts[0]
            kind = parts[1] if len(parts) > 1 and parts[1] else "other"
            note = parts[2] if len(parts) > 2 else ""
            out.append(iris_graph_memory.add_entity(name, kind, note))
    for line in (relations or "").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3 and all(parts[:3]):
            out.append(iris_graph_memory.add_relation(parts[0], parts[1], parts[2]))
    if not out:
        return "nothing saved (provide entities and/or relations)"
    return "Saved to graph memory:\n" + "\n".join(out) + f"\n({iris_graph_memory.stats()})"


@mcp.tool()
def graph_recall(query: str = "") -> str:
    """Recall from Iris's graph memory — entities and how they connect.

    Args:
        query: text to search entity names/notes. Empty = most recent memories.
    """
    data = iris_graph_memory.recall(query)
    if not data["nodes"] and not data["edges"]:
        return "No matching memories yet."
    lines = ["Entities:"]
    for n in data["nodes"]:
        note = f" — {n['note']}" if n["note"] else ""
        lines.append(f"  • {n['name']} ({n['kind']}){note}")
    if data["edges"]:
        lines.append("Relationships:")
        for e in data["edges"]:
            lines.append(f"  • {e['src']} --{e['rel']}--> {e['dst']}")
    return "\n".join(lines)


@mcp.tool()
def graph_visualize() -> str:
    """Render Iris's whole graph memory as an interactive visual graph and open it.

    Produces an offline HTML view (color-coded by entity kind) so Vikash sir
    can literally see how everything Iris knows is organized and connected.
    """
    path = iris_graph_memory.visualize(open_after=True)
    return f"Opened memory graph ({iris_graph_memory.stats()}): {path}"


@mcp.tool()
def list_local_models() -> str:
    """List Ollama models installed on this machine (auto-detected via `ollama list`).

    Use this before switching to a local model so you only offer models that
    actually exist on this machine.
    """
    models = iris_model_config.list_ollama_models()
    current = iris_model_config.get_current_model()
    if not models:
        return "No local Ollama models detected (is `ollama serve` running?)."
    lines = [f"{'→ ' if m == current.get('default') else '  '}{m}" for m in models]
    return f"Installed local models (current marked →):\n" + "\n".join(lines)


@mcp.tool()
def switch_to_local_model(model_name: str, restart_gateway: bool = True) -> str:
    """Switch Hermes to run fully locally on a given Ollama model — free, private, no API key.

    Writes the change to Hermes's config.yaml and (by default) turns the old
    mode off and starts the new one in its own titled terminal window
    ("IRIS - Local AI Mode (...)") so it takes effect immediately.

    Args:
        model_name: An installed Ollama model tag, e.g. "qwen2.5-coder:14b" (see list_local_models).
        restart_gateway: Whether to also switch the running gateway now (default True).
    """
    if restart_gateway:
        return iris_model_config.switch_local_model(model_name)
    return iris_model_config.set_local_model(model_name)


@mcp.tool()
def switch_to_cloud_model(model_name: str, provider: str = "openrouter", restart_gateway: bool = True) -> str:
    """Switch Hermes back to a cloud provider model (e.g. OpenRouter, Gemini).

    Args:
        model_name: The cloud model id, e.g. "tencent/hy3:free" or "anthropic/claude-sonnet-4".
        provider: The provider key as configured in Hermes (default "openrouter").
        restart_gateway: Whether to also switch the running gateway now (default True).
    """
    if restart_gateway:
        return iris_model_config.switch_cloud_model(model_name, provider)
    return iris_model_config.set_cloud_model(model_name, provider)


if __name__ == "__main__":
    mcp.run()
