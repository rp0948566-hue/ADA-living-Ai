"""Saves detailed write-ups (research, summaries, notes) Iris produces so
Vikash sir can come back to them later — e.g. "I'm stepping out for a bit,
research X and write it up" — instead of the result only living in a chat
reply that scrolls away.

Files land in iris_data/reports/ as markdown, named from the title + a
timestamp so nothing overwrites silently.
"""
import os
import re
import time

REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iris_data", "reports")


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug[:60] or "report"


def save_report(title: str, content: str) -> str:
    """Save a markdown report. Returns the absolute file path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"{stamp}_{_slugify(title)}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}\n")
    return path


def list_reports(limit: int = 20) -> list:
    """Most recent saved reports first: [(title, path, mtime), ...]."""
    if not os.path.isdir(REPORTS_DIR):
        return []
    files = [os.path.join(REPORTS_DIR, f) for f in os.listdir(REPORTS_DIR) if f.endswith(".md")]
    files.sort(key=os.path.getmtime, reverse=True)
    out = []
    for p in files[:limit]:
        try:
            with open(p, "r", encoding="utf-8") as f:
                first_line = f.readline().strip().lstrip("# ")
        except Exception:
            first_line = os.path.basename(p)
        out.append((first_line, p, os.path.getmtime(p)))
    return out
