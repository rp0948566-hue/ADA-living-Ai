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
import iris_task_queue
import iris_reports
import Iris_image_generator
import iris_screen_activity
from features import browser_automation

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
    with iris_screen_activity.active():
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
    with iris_screen_activity.active():
        return await Iris_window_CTRL.close(window_title)


@mcp.tool()
async def folder_file_command(command: str) -> str:
    """Manage folders/files under D:/ using a natural-language command.

    Supports: "create folder <name>", "rename <old> to <new>", "delete <name>",
    "open folder <name>". Falls back to fuzzy file search + open otherwise.

    Args:
        command: The natural-language folder/file command.
    """
    with iris_screen_activity.active():
        return await Iris_window_CTRL.folder_file(command)


@mcp.tool()
async def play_file(name: str) -> str:
    """Find and open a file anywhere under D:/ by fuzzy name match (video, audio, doc, image, etc).

    Args:
        name: The file name (or close approximation) to search for and open.
    """
    with iris_screen_activity.active():
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
    with iris_screen_activity.active():
        return Iris_youtube_music.play_youtube_song_sync(song_name)


@mcp.tool()
def control_youtube(command: str) -> str:
    """Control YouTube playback in the active browser tab.

    Args:
        command: One of: pause, play, resume, next, mute, unmute, fullscreen, exit fullscreen.
    """
    with iris_screen_activity.active():
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
        with iris_screen_activity.active():
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


@mcp.tool()
def queue_task(description: str, when: str = "now") -> str:
    """Hand off a task to run later, decoupled from this conversation turn —
    either in the background right away, or at a specific time.

    Use this whenever Vikash sir says something like "I'm coming back in a
    bit, meanwhile do/research X", "automate this for me", or gives a fixed
    time ("remind me / do this at 5:30", "in 30 minutes"). The task runs
    through you exactly like a normal message (with all your tools
    available — research, save_report, run_command, etc.), and once it
    finishes he gets pinged with the result automatically. You don't need to
    stay "in the loop" for it yourself — just queue it and move on.

    Args:
        description: What to do, written the way you'd want to receive it
            as an instruction (be specific — this exact text is what you'll
            be asked to act on later, with no other context attached).
        when: "now" (default — runs in the background almost immediately),
            "in 30 minutes", "in 2 hours", "17:30" / "5:30 pm" (today, or
            tomorrow if that time already passed), or an ISO timestamp.
    """
    task = iris_task_queue.queue_task(description, when)
    return f"✅ Queued (id={task['id']}, runs at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task['run_at']))}): {description}"


@mcp.tool()
def list_scheduled_tasks() -> str:
    """List queued/background tasks and their status (pending/running/done/failed/cancelled)."""
    tasks = iris_task_queue.list_tasks()
    if not tasks:
        return "No scheduled/background tasks."
    lines = []
    for t in tasks[-30:]:
        ts = time.strftime("%m-%d %H:%M", time.localtime(t["run_at"]))
        lines.append(f"[{t['id']}] ({t['status']}) @ {ts} — {t['description']}")
    return "\n".join(lines)


@mcp.tool()
def cancel_scheduled_task(task_id: str) -> str:
    """Cancel a pending scheduled/background task by its id (see list_scheduled_tasks).

    Args:
        task_id: The short id shown in list_scheduled_tasks, e.g. "a1b2c3d4e5".
    """
    return "✅ Cancelled." if iris_task_queue.cancel_task(task_id) else "⚠ Not found or already running/done."


@mcp.tool()
def save_report(title: str, content: str) -> str:
    """Save a detailed write-up (research summary, notes, findings) as a
    markdown file Vikash sir can open later, and tell him where it landed.

    Use this after doing research or preparing anything "detailed" he asked
    for — write the full content yourself first (using scrape_web/run_command
    etc. as needed to gather it), then call this to persist it. Always
    mention the returned file path back to him in your reply.

    Args:
        title: Short report title (used to name the file too).
        content: The full markdown body of the report.
    """
    path = iris_reports.save_report(title, content)
    return f"✅ Saved report to: {path}"


@mcp.tool()
def list_reports() -> str:
    """List recently saved reports (see save_report), most recent first."""
    reports = iris_reports.list_reports()
    if not reports:
        return "No reports saved yet."
    return "\n".join(f"{title} — {path}" for title, path, _ in reports)


@mcp.tool()
def read_screen() -> str:
    """See what's currently on Vikash sir's screen — takes a screenshot and
    extracts any visible text from it (OCR).

    Use this when he asks what's on his screen, to check the state of some
    app/window before acting, or as situational awareness before automating
    something. Requires Tesseract-OCR installed on the machine for the text
    extraction; the screenshot is saved either way.
    """
    try:
        from PIL import ImageGrab
    except Exception as e:
        return f"❌ Screenshot unavailable (PIL missing): {e}"
    folder = os.path.join(PROJECT_ROOT, "iris_data", "screen_snapshots")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, time.strftime("%Y%m%d_%H%M%S") + ".png")
    try:
        img = ImageGrab.grab()
        img.save(path)
    except Exception as e:
        return f"❌ Screenshot failed: {e}"
    try:
        import pytesseract
        text = pytesseract.image_to_string(img).strip()
        if text:
            return f"📸 Screenshot saved: {path}\n\nText visible on screen:\n{text[:4000]}"
        return f"📸 Screenshot saved: {path}\n\n(No readable text detected on screen.)"
    except Exception:
        return (
            f"📸 Screenshot saved: {path}\n\n"
            "⚠ OCR not available (install Tesseract-OCR + `pip install pytesseract` "
            "for text extraction) — screenshot itself was captured fine."
        )


@mcp.tool()
async def send_whatsapp_message(message: str, phone_number: str = "") -> str:
    """Send a WhatsApp message via WhatsApp Web, opened in Brave.

    Use this for "message me on WhatsApp", "send this to myself on WhatsApp",
    etc. Opens web.whatsapp.com in Brave with the chat + message prefilled,
    waits for it to load, then sends it. If no phone_number is given, uses
    WHATSAPP_SELF_NUMBER from .env (Vikash sir's own number) — set that up
    first if it isn't configured, since "myself" needs a number to resolve to.

    This drives the keyboard, so avoid touching the mouse/keyboard while it's
    running (roughly 12-15 seconds).

    Args:
        message: The message text to send.
        phone_number: Destination number with country code (e.g. "+919876543210").
            Defaults to WHATSAPP_SELF_NUMBER from .env if omitted.
    """
    import urllib.parse
    phone = (phone_number or os.getenv("WHATSAPP_SELF_NUMBER", "")).strip()
    if not phone:
        return (
            "❌ No phone number configured. Add WHATSAPP_SELF_NUMBER=+91XXXXXXXXXX "
            "(with country code) to the .env file, or pass phone_number explicitly."
        )
    url = f"https://web.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(message)}"

    def _do_send():
        target, _, _ = iris_app_index.resolve_app("brave")
        if target:
            subprocess.Popen([target, url] if os.path.isabs(target) else f'"{target}" "{url}"',
                              shell=not os.path.isabs(target))
        else:
            import webbrowser
            webbrowser.open(url)
        time.sleep(13)  # let WhatsApp Web load the chat + prefill the text box
        import pyautogui
        pyautogui.press("enter")

    try:
        with iris_screen_activity.active():
            await asyncio.to_thread(_do_send)
        return f"✅ WhatsApp message sent to {phone}: {message}"
    except Exception as e:
        return f"❌ Failed to send WhatsApp message: {e}"


WEBSITES_DIR = os.path.join(PROJECT_ROOT, "iris_data", "websites")


@mcp.tool()
async def research_website_design(topic: str, count: int = 10) -> str:
    """Gather real design inspiration for a website before building it.

    Opens Pinterest in Brave for browsing (logging in via Google first if
    needed — best-effort; if Google throws up a security challenge it stops
    and tells you rather than trying to push through it), AND scrapes
    Dribbble's search results for structured, linkable design references you
    can actually cite (title + real URL), since Pinterest's own page is pure
    images and can't be reliably parsed for links.

    Use this before building any website: present the shortlist to Vikash
    sir and ask him to pick one (or approve your favorite). If he doesn't
    give a clear answer, pick the strongest one yourself and proceed — don't
    block the whole build waiting on an approval that isn't coming.

    Args:
        topic: what the website is for/about (e.g. "coffee shop", "SaaS dashboard").
        count: how many design references to pull (default 10).
    """
    brave_path, _, _ = iris_app_index.resolve_app("brave")
    with iris_screen_activity.active():
        pinterest_status = await asyncio.to_thread(
            browser_automation.pinterest_login_flow, brave_path or "", topic
        )

    dribbble_lines = []
    try:
        from scrapling.fetchers import Fetcher
        q = topic.replace(" ", "+")

        def _fetch():
            return Fetcher.get(f"https://dribbble.com/search/shots?q={q}+website", stealthy_headers=True)

        page = await asyncio.to_thread(_fetch)
        seen = set()
        for a in page.css("a"):
            href = a.attrib.get("href", "")
            if "/shots/" not in href:
                continue
            label = a.get_all_text(strip=True)
            if not label or href in seen:
                continue
            seen.add(href)
            full_url = href if href.startswith("http") else f"https://dribbble.com{href}"
            dribbble_lines.append(f"{label} — {full_url}")
            if len(dribbble_lines) >= count:
                break
    except Exception as e:
        dribbble_lines = [f"(Dribbble scrape failed: {e})"]

    result = [f"Pinterest: {pinterest_status}", "", f"Top design references for '{topic}':"]
    result += dribbble_lines or ["(no results found)"]
    return "\n".join(result)


@mcp.tool()
def generate_design_image(prompt: str, project_path: str, relative_path: str) -> str:
    """Generate an image (via Stability AI) for use in a website being built,
    and save it directly into that project's folder.

    Args:
        prompt: Description of the image to generate.
        project_path: Absolute path of the website project (from scaffold_website).
        relative_path: Where to save it inside the project, e.g. "src/assets/hero.png".
    """
    full = os.path.abspath(os.path.join(project_path, relative_path))
    if not full.startswith(os.path.abspath(WEBSITES_DIR)):
        return "❌ Refused: path escapes the websites sandbox."
    return Iris_image_generator.generate_image_sync(prompt, full)


@mcp.tool()
async def scaffold_website(project_name: str, stack: str = "vite-react-tailwind") -> str:
    """Scaffold a new website project (Vite + React + Tailwind by default) —
    prefer this over a plain static HTML file for anything "AAA level"; it
    gives you real components, hot-reload, and a proper build.

    Args:
        project_name: Folder/project name (no spaces — use hyphens).
        stack: Currently only "vite-react-tailwind" is wired up.
    """
    os.makedirs(WEBSITES_DIR, exist_ok=True)
    project_path = os.path.join(WEBSITES_DIR, project_name)
    if os.path.exists(project_path):
        return f"⚠ Project already exists: {project_path}"

    steps = [
        f'cd "{WEBSITES_DIR}"',
        f'npm create vite@latest {project_name} -- --template react',
        f'cd "{project_path}"',
        'npm install',
        'npm install -D tailwindcss postcss autoprefixer',
        'npx tailwindcss init -p',
    ]
    log = []
    with iris_screen_activity.active():
        for cmd in steps:
            rc, out = await asyncio.to_thread(iris_model_config.run_in_ai_terminal, cmd, 180)
            log.append(f"$ {cmd}\n{(out or '(no output / timed out)')[:600]}")
    ok = os.path.exists(project_path)
    header = f"{'✅' if ok else '❌'} Scaffolded at {project_path}" if ok else "❌ Scaffold failed — see log below"
    return header + "\n\n" + "\n\n".join(log)


@mcp.tool()
def write_project_file(project_path: str, relative_path: str, content: str) -> str:
    """Write (or overwrite) a file inside a scaffolded website project.

    Use this for every React component, page, style sheet, and config file
    the site needs — write real, complete code, not placeholders.

    Args:
        project_path: Absolute project path (from scaffold_website).
        relative_path: File path inside the project, e.g. "src/App.jsx".
        content: Full file content.
    """
    full = os.path.abspath(os.path.join(project_path, relative_path))
    if not full.startswith(os.path.abspath(WEBSITES_DIR)):
        return "❌ Refused: path escapes the websites sandbox."
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ Wrote {full}"


@mcp.tool()
async def run_dev_server(project_path: str) -> str:
    """Start `npm run dev` for a scaffolded website project in its own
    persistent window (not the shared AI Command Terminal, since a dev
    server runs forever and would block the command queue).

    Args:
        project_path: Absolute project path (from scaffold_website).
    """
    if not os.path.isdir(project_path):
        return f"❌ No such project folder: {project_path}"
    start_cmd = (
        f'Start-Process powershell -ArgumentList \'-NoExit\',\'-Command\',\'cd "{project_path}"; npm run dev\''
    )
    with iris_screen_activity.active():
        rc, out = await asyncio.to_thread(iris_model_config.run_in_ai_terminal, start_cmd, 30)
    return (
        f"🚀 Dev server starting for {project_path} in its own window "
        "(Vite defaults to http://localhost:5173 — check that window for the exact URL, "
        "port may differ if 5173 was busy)."
    )


if __name__ == "__main__":
    mcp.run()
