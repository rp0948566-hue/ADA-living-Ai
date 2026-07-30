"""Toggle-able external MCP connectors (Blender, Figma, 21st.dev, Lovable)
that get merged into Hermes's mcp_servers config alongside iris-tools.

State lives in iris_data/mcp_connectors.json (just which ones are on/off).
The actual connection details for each connector are fixed/known-good
configs baked in here — the user only ever flips a switch in the GUI.

Config edits go through ruamel.yaml (round-trip mode) specifically so this
never clobbers iris-tools or anything else already in config.yaml, and never
destroys the file's comments — a plain text-replace/regex approach did both
the first time this was written.
"""
import json
import os

from ruamel.yaml import YAML

STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iris_data", "mcp_connectors.json")
HERMES_CONFIG_PATH = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"), "hermes", "config.yaml")

# Known-good connector configs. `ready` = can actually connect with zero
# extra setup beyond enabling it; others need something else running/set
# first (documented in `note`) — enabling them wires the config in either way,
# but Hermes just won't get tools from that server until the prerequisite
# is met (same graceful-degradation behavior as its other optional tools).
CONNECTORS = {
    "blender": {
        # blender-mcp pins no upper bound on `mcp`, so a bare `uvx blender-mcp`
        # resolves the newest `mcp` (2.0.0+, which dropped the old fastmcp API
        # blender-mcp's code imports) and crashes with
        # "ModuleNotFoundError: No module named 'mcp.server.fastmcp'".
        # Pinning mcp<2.0.0 here fixes it — verified working end-to-end
        # against a live Blender instance.
        "label": "Blender",
        "config": {"command": "uvx", "args": ["--with", "mcp<2.0.0", "blender-mcp"]},
        "ready": True,
        "note": "Needs the BlenderMCP addon (addon.py) installed and enabled "
                "in Blender, then click 'Connect to Claude' in Blender's "
                "sidebar (N-panel > BlenderMCP tab) each session.",
    },
    "figma": {
        "label": "Figma",
        "config": {"url": "http://127.0.0.1:3845/mcp"},
        "ready": False,
        "note": "Needs the Figma desktop app open with Preferences > "
                "Enable Dev Mode MCP Server turned on.",
    },
    "21st-dev": {
        "label": "21st.dev (Magic)",
        "config": {
            "command": "npx",
            "args": ["-y", "@21st-dev/magic@latest"],
            "env": {"TWENTY_FIRST_API_KEY": "${TWENTY_FIRST_API_KEY}"},
        },
        "ready": False,
        "note": "Needs TWENTY_FIRST_API_KEY set in .env (get one at 21st.dev).",
    },
    "lovable": {
        "label": "Lovable",
        "config": None,
        "ready": False,
        "note": "No public local/remote MCP endpoint for Lovable yet — "
                "toggling this on does nothing until Lovable ships one.",
    },
}


def _load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {name: True for name in CONNECTORS}  # default: all on
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
    except Exception:
        saved = {}
    return {name: saved.get(name, True) for name in CONNECTORS}


def _save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def list_connectors() -> list:
    """[(name, label, enabled, ready, note), ...]"""
    state = _load_state()
    return [
        (name, info["label"], state[name], info["ready"], info["note"])
        for name, info in CONNECTORS.items()
    ]


def set_enabled(name: str, enabled: bool):
    if name not in CONNECTORS:
        return
    state = _load_state()
    state[name] = enabled
    _save_state(state)
    apply_to_hermes_config()


def _yaml():
    y = YAML()
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def apply_to_hermes_config() -> bool:
    """Add/remove connector entries under mcp_servers in Hermes's
    config.yaml, touching ONLY the keys this module owns (blender, figma,
    21st-dev, lovable) — everything else already in that file (iris-tools,
    model settings, memory config, comments) is left exactly as-is."""
    if not os.path.exists(HERMES_CONFIG_PATH):
        return False

    y = _yaml()
    with open(HERMES_CONFIG_PATH, "r", encoding="utf-8") as f:
        data = y.load(f) or {}

    if "mcp_servers" not in data or data["mcp_servers"] is None:
        data["mcp_servers"] = {}
    mcp_servers = data["mcp_servers"]

    state = _load_state()
    for name, info in CONNECTORS.items():
        if state.get(name) and info["config"] is not None:
            mcp_servers[name] = info["config"]
        elif name in mcp_servers:
            del mcp_servers[name]

    with open(HERMES_CONFIG_PATH, "w", encoding="utf-8") as f:
        y.dump(data, f)
    return True
