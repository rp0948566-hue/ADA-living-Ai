"""MCP bridge exposing Jarvis's existing desktop-control code to Hermes Agent.

Runs as a stdio MCP server (spawned by Hermes per its ``mcp_servers`` config
in ``%LOCALAPPDATA%\\hermes\\config.yaml``). Each tool below is a thin
wrapper around the *existing* Jarvis_*.py implementations — no logic is
duplicated here, only exposed.

Deliberately NOT wrapped here (kept local to the LiveKit voice loop for
instant response): mouse/keyboard/volume control (keyboard_mouse_CTRL.py).

Deliberately NOT wrapped here (Hermes has built-in equivalents already):
web search, screenshots, system info, news.
"""
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP

import Jarvis_window_CTRL
import Jarvis_file_opner
import Jarvis_email
import Jarvis_youtube_music
import jarvis_get_whether

mcp = FastMCP(
    "jarvis-tools",
    instructions=(
        "Controls Vikash sir's Windows desktop: launching/closing apps, "
        "opening/creating/renaming/deleting files and folders, sending "
        "email, playing/controlling YouTube, checking weather, and reading "
        "the live camera-view description. Use these directly and "
        "confidently when asked to perform an action on the desktop."
    ),
)


@mcp.tool()
async def open_app(app_title: str) -> str:
    """Launch an application or open a URL/path by name (e.g. "notepad", "chrome", "vs code").

    Args:
        app_title: The app name or command to launch.
    """
    return await Jarvis_window_CTRL.open(app_title)


@mcp.tool()
async def close_window(window_title: str) -> str:
    """Close any open window whose title contains the given text.

    Args:
        window_title: Substring to match against open window titles.
    """
    return await Jarvis_window_CTRL.close(window_title)


@mcp.tool()
async def folder_file_command(command: str) -> str:
    """Manage folders/files under D:/ using a natural-language command.

    Supports: "create folder <name>", "rename <old> to <new>", "delete <name>",
    "open folder <name>". Falls back to fuzzy file search + open otherwise.

    Args:
        command: The natural-language folder/file command.
    """
    return await Jarvis_window_CTRL.folder_file(command)


@mcp.tool()
async def play_file(name: str) -> str:
    """Find and open a file anywhere under D:/ by fuzzy name match (video, audio, doc, image, etc).

    Args:
        name: The file name (or close approximation) to search for and open.
    """
    return await Jarvis_file_opner.Play_file(name)


@mcp.tool()
def send_email(recipient: str, subject: str, message: str) -> str:
    """Send an email via the configured Gmail account.

    Args:
        recipient: A contact name (e.g. "Rudra") or a raw email address.
        subject: Email subject line.
        message: Email body text.
    """
    result = Jarvis_email.send_email_direct(recipient, subject, message)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def play_youtube(song_name: str) -> str:
    """Play a song/video on YouTube by name.

    Args:
        song_name: What to search for and play on YouTube.
    """
    return Jarvis_youtube_music.play_youtube_song_sync(song_name)


@mcp.tool()
def control_youtube(command: str) -> str:
    """Control YouTube playback in the active browser tab.

    Args:
        command: One of: pause, play, resume, next, mute, unmute, fullscreen, exit fullscreen.
    """
    return Jarvis_youtube_music.youtube_control(command)


@mcp.tool()
async def get_weather(city: str = "") -> str:
    """Get the current weather for a city (defaults to the user's detected location).

    Args:
        city: City name, or empty to auto-detect from IP.
    """
    return await jarvis_get_whether.get_weather(city)


@mcp.tool()
def camera_view() -> str:
    """Read the most recent description of what the desktop's live camera currently sees.

    Camera must already be running (owned by the GUI) for this to be current;
    otherwise returns whatever status/error was last written.
    """
    path = os.path.join(PROJECT_ROOT, "jarvis_data", "camera_view.txt")
    if not os.path.exists(path):
        return "Camera abhi tak initialize nahi hua hai ya GUI running nahi hai."
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip() or "Camera se koi observation available nahi hai."


if __name__ == "__main__":
    mcp.run()
