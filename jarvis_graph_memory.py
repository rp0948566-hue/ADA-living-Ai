"""Graph-structured memory for Jarvis ("graphify").

A self-contained knowledge graph the AI manages itself: entities are nodes
(people, projects, preferences, apps, facts) and relationships are edges
("Vikash sir" --uses--> "VS Code", "Vikash sir" --prefers--> "Hindi").

Backed by SQLite (stdlib, no server needed), rendered to an interactive HTML
graph with pyvis (fully offline — resources inlined). The AI writes to this
automatically per its SOUL.md instructions; the user never has to curate it.
"""
import os
import sqlite3
import time
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.getcwd(), "jarvis_data", "graph_memory.db")
HTML_PATH = os.path.join(os.getcwd(), "jarvis_data", "memory_graph.html")

# node "kind" -> color, so the visual graph is organized/legible by category
KIND_COLORS = {
    "person": "#8FD3FF",
    "preference": "#D9B8FF",
    "project": "#FFB86B",
    "app": "#6BE3A0",
    "fact": "#F7F7F7",
    "place": "#FF8FB0",
    "device": "#B0B0FF",
    "other": "#C9C9CF",
}


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def _init():
    conn = _connect()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS nodes (
            name TEXT PRIMARY KEY,
            kind TEXT NOT NULL DEFAULT 'other',
            note TEXT,
            updated REAL NOT NULL
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS edges (
            src TEXT NOT NULL,
            rel TEXT NOT NULL,
            dst TEXT NOT NULL,
            updated REAL NOT NULL,
            UNIQUE(src, rel, dst)
        )"""
    )
    conn.commit()
    conn.close()


_init()


def add_entity(name: str, kind: str = "other", note: str = "") -> str:
    name = name.strip()
    if not name:
        return "empty name"
    kind = kind if kind in KIND_COLORS else "other"
    conn = _connect()
    # Never downgrade a specific kind back to 'other' on a generic touch;
    # never wipe an existing note with an empty one.
    conn.execute(
        "INSERT INTO nodes(name, kind, note, updated) VALUES(?,?,?,?) "
        "ON CONFLICT(name) DO UPDATE SET "
        "kind=CASE WHEN excluded.kind != 'other' THEN excluded.kind ELSE nodes.kind END, "
        "note=CASE WHEN excluded.note != '' THEN excluded.note ELSE nodes.note END, "
        "updated=excluded.updated",
        (name, kind, note, time.time()),
    )
    conn.commit()
    conn.close()
    return f"entity '{name}' ({kind})"


def add_relation(src: str, rel: str, dst: str) -> str:
    src, rel, dst = src.strip(), rel.strip(), dst.strip()
    if not (src and rel and dst):
        return "src/rel/dst required"
    # ensure both endpoints exist as nodes
    add_entity(src)
    add_entity(dst)
    conn = _connect()
    conn.execute(
        "INSERT OR REPLACE INTO edges(src, rel, dst, updated) VALUES(?,?,?,?)",
        (src, rel, dst, time.time()),
    )
    conn.commit()
    conn.close()
    return f"{src} --{rel}--> {dst}"


def recall(query: str = "", limit: int = 40) -> Dict:
    """Return matching nodes and their edges. Empty query -> most recent."""
    conn = _connect()
    c = conn.cursor()
    if query:
        like = f"%{query.lower()}%"
        c.execute(
            "SELECT name, kind, note FROM nodes WHERE lower(name) LIKE ? OR lower(note) LIKE ? "
            "ORDER BY updated DESC LIMIT ?",
            (like, like, limit),
        )
    else:
        c.execute("SELECT name, kind, note FROM nodes ORDER BY updated DESC LIMIT ?", (limit,))
    nodes = [{"name": r[0], "kind": r[1], "note": r[2]} for r in c.fetchall()]
    names = {n["name"] for n in nodes}
    edges = []
    if names:
        q = ",".join("?" * len(names))
        c.execute(
            f"SELECT src, rel, dst FROM edges WHERE src IN ({q}) OR dst IN ({q})",
            list(names) + list(names),
        )
        edges = [{"src": r[0], "rel": r[1], "dst": r[2]} for r in c.fetchall()]
    conn.close()
    return {"nodes": nodes, "edges": edges}


def all_data() -> Dict:
    conn = _connect()
    c = conn.cursor()
    c.execute("SELECT name, kind, note FROM nodes")
    nodes = [{"name": r[0], "kind": r[1], "note": r[2]} for r in c.fetchall()]
    c.execute("SELECT src, rel, dst FROM edges")
    edges = [{"src": r[0], "rel": r[1], "dst": r[2]} for r in c.fetchall()]
    conn.close()
    return {"nodes": nodes, "edges": edges}


def visualize(open_after: bool = True) -> str:
    """Render the whole graph to an interactive offline HTML file."""
    data = all_data()
    try:
        from pyvis.network import Network
    except Exception as e:
        return f"pyvis unavailable: {e}"

    net = Network(
        height="100%", width="100%", bgcolor="#171717", font_color="#E8E8EC",
        directed=True,
    )
    net.barnes_hut(gravity=-9000, spring_length=140)
    for n in data["nodes"]:
        color = KIND_COLORS.get(n["kind"], KIND_COLORS["other"])
        title = f"{n['kind']}" + (f": {n['note']}" if n["note"] else "")
        net.add_node(n["name"], label=n["name"], color=color, title=title)
    for e in data["edges"]:
        # endpoints are guaranteed as nodes by add_relation, but guard anyway
        net.add_node(e["src"], label=e["src"], color=KIND_COLORS["other"])
        net.add_node(e["dst"], label=e["dst"], color=KIND_COLORS["other"])
        net.add_edge(e["src"], e["dst"], label=e["rel"])

    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    try:
        # inline resources -> fully offline, self-contained HTML
        net.save_graph(HTML_PATH)
    except Exception as e:
        return f"render failed: {e}"

    if open_after:
        try:
            os.startfile(HTML_PATH)
        except Exception:
            pass
    return HTML_PATH


def stats() -> str:
    d = all_data()
    return f"{len(d['nodes'])} entities, {len(d['edges'])} relationships"
