"""Dynamic app discovery for Jarvis.

Instead of a hardcoded APP_MAPPINGS table, this scans the machine at runtime
for installed applications, so Jarvis can launch anything that's actually
present without anyone editing a path list first. Sources scanned:

  - Start Menu shortcuts (.lnk) — the most reliable "what's installed" list
  - App Paths registry key (HKLM/HKCU ...\\App Paths)
  - PATH executables
  - Known Claude / Claude Code / VS Code / browser locations

Results are fuzzy-matched so "claude", "vs code", "chrome" etc. resolve to
the real launch target. A short in-memory + on-disk cache avoids rescanning
on every call.
"""
import glob
import json
import os
import time

try:
    from fuzzywuzzy import process as _fuzz
except Exception:
    _fuzz = None

try:
    import winreg
except Exception:
    winreg = None

_CACHE_PATH = os.path.join(os.getcwd(), "jarvis_data", "app_index.json")
_CACHE_TTL = 3600  # rescan at most once an hour
_mem_cache = {"ts": 0, "apps": {}}


def _start_menu_dirs():
    dirs = []
    for env in ("ProgramData", "APPDATA"):
        base = os.environ.get(env)
        if base:
            dirs.append(os.path.join(base, "Microsoft", "Windows", "Start Menu", "Programs"))
    return [d for d in dirs if os.path.isdir(d)]


def _scan_start_menu():
    """Return {display_name_lower: shortcut_path} for every Start Menu .lnk."""
    apps = {}
    for d in _start_menu_dirs():
        for lnk in glob.glob(os.path.join(d, "**", "*.lnk"), recursive=True):
            name = os.path.splitext(os.path.basename(lnk))[0].lower()
            apps.setdefault(name, lnk)
    return apps


def _scan_app_paths():
    """Read the Windows 'App Paths' registry — canonical launch targets."""
    apps = {}
    if winreg is None:
        return apps
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            key = winreg.OpenKey(
                root, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"
            )
        except OSError:
            continue
        try:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                except OSError:
                    break
                i += 1
                try:
                    sk = winreg.OpenKey(key, sub)
                    path, _ = winreg.QueryValueEx(sk, None)
                    name = os.path.splitext(sub)[0].lower()
                    if path:
                        apps.setdefault(name, path.strip('"'))
                except OSError:
                    pass
        finally:
            winreg.CloseKey(key)
    return apps


def _scan_known():
    """Explicitly probe common AI/dev/browser targets that matter most."""
    apps = {}
    local = os.environ.get("LOCALAPPDATA", "")
    pf = os.environ.get("ProgramFiles", r"C:\Program Files")
    pfx = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    candidates = {
        "claude": [os.path.join(local, "AnthropicClaude", "claude.exe"),
                   os.path.join(local, "Programs", "claude", "Claude.exe")],
        "claude desktop": [os.path.join(local, "AnthropicClaude", "claude.exe")],
        "cursor": [os.path.join(local, "Programs", "cursor", "Cursor.exe")],
        "vs code": [os.path.join(local, "Programs", "Microsoft VS Code", "Code.exe")],
        "code": [os.path.join(local, "Programs", "Microsoft VS Code", "Code.exe")],
        "chrome": [os.path.join(pf, "Google", "Chrome", "Application", "chrome.exe"),
                   os.path.join(pfx, "Google", "Chrome", "Application", "chrome.exe")],
        "edge": [os.path.join(pfx, "Microsoft", "Edge", "Application", "msedge.exe")],
        "notepad": ["notepad"],
        "calculator": ["calc"],
    }
    for name, paths in candidates.items():
        for pth in paths:
            if pth in ("notepad", "calc") or os.path.exists(pth):
                apps.setdefault(name, pth)
                break
    return apps


def build_index(force=False):
    """Return {name: launch_target}. Cached to disk + memory for _CACHE_TTL."""
    now = time.time()
    if not force and _mem_cache["apps"] and now - _mem_cache["ts"] < _CACHE_TTL:
        return _mem_cache["apps"]
    if not force and os.path.exists(_CACHE_PATH):
        try:
            if now - os.path.getmtime(_CACHE_PATH) < _CACHE_TTL:
                with open(_CACHE_PATH, "r", encoding="utf-8") as f:
                    apps = json.load(f)
                _mem_cache.update(ts=now, apps=apps)
                return apps
        except Exception:
            pass

    apps = {}
    apps.update(_scan_start_menu())
    apps.update(_scan_app_paths())
    apps.update(_scan_known())  # known targets win over generic shortcuts

    _mem_cache.update(ts=now, apps=apps)
    try:
        os.makedirs(os.path.dirname(_CACHE_PATH), exist_ok=True)
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return apps


def resolve_app(query: str):
    """Fuzzy-resolve a spoken app name to a launch target.

    Returns (target, matched_name, score) or (None, None, 0) if nothing is a
    confident match.
    """
    apps = build_index()
    q = query.lower().strip()
    if q in apps:
        return apps[q], q, 100
    if _fuzz and apps:
        match, score = _fuzz.extractOne(q, list(apps.keys()))
        if score >= 70:
            return apps[match], match, score
    return None, None, 0


def list_apps():
    """Return a sorted list of discovered app names (for 'what can you open')."""
    return sorted(build_index().keys())
