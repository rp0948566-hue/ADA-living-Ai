"""Silent, token-free codebase index: SQLite FTS5 over file paths and text chunks, refreshed in the background.
Lets Jeb find files and code instantly (and tell the local model where things are) without spending LLM tokens.
Never indexes secrets: .env, keys, tokens, credentials."""
import os
import re
import sqlite3
import threading
import time
from pathlib import Path

DB = Path.home() / ".local" / "share" / "jeb" / "index.db"
ROOTS = [Path.home() / "Desktop", Path.home() / "Documents"]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".cache", "models", "vovy_extracted", "dist", "build",
             ".next", "target", ".idea", ".gradle", "site-packages", ".ollama", "Trash"}
SECRET = re.compile(r"(^\.env|\.pem$|\.key$|^id_(rsa|ed25519|ecdsa)|secret|credential|token|\.kdbx$|\.p12$|\.pfx$)", re.I)
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".html", ".css", ".sh", ".toml", ".yaml", ".yml", ".rs",
            ".go", ".java", ".c", ".h", ".cpp", ".cs", ".sql", ".service", ".ini", ".cfg", ".csv", ".ipynb"}
MAX_BYTES = 1_000_000
CHUNK = 40  # lines per searchable chunk
_lock = threading.Lock()
_map_cache = {"t": 0.0, "text": ""}


def _db(path: Path | None = None) -> sqlite3.Connection:
    path = path or DB
    path.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(path, timeout=30)
    c.execute("CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, mtime REAL, size INT)")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(path UNINDEXED, line UNINDEXED, text, tokenize='porter unicode61')")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS names USING fts5(path, tokenize='unicode61 remove_diacritics 2')")
    return c


def _walk(roots):
    for root in roots:
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in SKIP_DIRS and not d.startswith(".")]
            for n in fn:
                if SECRET.search(n):
                    continue
                yield Path(dp) / n


def refresh(roots=None, db_path: Path | None = None) -> dict:
    """Incrementally (re)index changed files and drop deleted ones. Returns counts."""
    with _lock:
        c = _db(db_path)
        known = {p: m for p, m in c.execute("SELECT path, mtime FROM files")}
        seen, added = set(), 0
        for p in _walk(roots or ROOTS):
            s = str(p)
            try:
                st = p.stat()
            except OSError:
                continue
            seen.add(s)
            if known.get(s) == st.st_mtime:
                continue
            c.execute("DELETE FROM files WHERE path=?", (s,)); c.execute("DELETE FROM chunks WHERE path=?", (s,)); c.execute("DELETE FROM names WHERE path=?", (s,))
            c.execute("INSERT INTO files VALUES(?,?,?)", (s, st.st_mtime, st.st_size))
            c.execute("INSERT INTO names VALUES(?)", (s,))
            if p.suffix.lower() in TEXT_EXT and st.st_size <= MAX_BYTES:
                try:
                    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
                except OSError:
                    continue
                for i in range(0, len(lines), CHUNK):
                    c.execute("INSERT INTO chunks VALUES(?,?,?)", (s, i + 1, "\n".join(lines[i:i + CHUNK])))
            added += 1
        gone = [p for p in known if p not in seen]
        for s in gone:
            c.execute("DELETE FROM files WHERE path=?", (s,)); c.execute("DELETE FROM chunks WHERE path=?", (s,)); c.execute("DELETE FROM names WHERE path=?", (s,))
        c.commit(); n = c.execute("SELECT count(*) FROM files").fetchone()[0]; c.close()
        return {"indexed_now": added, "removed": len(gone), "total": n}


def _q(query: str) -> str:
    words = re.findall(r"\w+", query)
    return " ".join(f'"{w}"' for w in words) if words else '""'


def search_code(query: str, folder: str = "") -> str:
    """Search the indexed code and notes on this laptop for words (instant, free). Returns path:line plus a snippet."""
    c = _db()
    like = (str(Path(folder).expanduser()) + "%") if folder else "%"
    rows = c.execute("SELECT path, line, snippet(chunks, 2, '[', ']', ' … ', 18) FROM chunks WHERE chunks MATCH ? AND path LIKE ? ORDER BY rank LIMIT 8",
                     (_q(query), like)).fetchall()
    names = c.execute("SELECT path FROM names WHERE names MATCH ? AND path LIKE ? ORDER BY rank LIMIT 5", (_q(query), like)).fetchall()
    c.close()
    out = [f"{p}:{ln}  {s.strip()}"[:260] for p, ln, s in rows]
    out += [f"(file name) {p}" for (p,) in names]
    return "\n".join(out) or f"no indexed match for '{query}'"


def project_map(max_chars: int = 600) -> str:
    """Short map of the user's projects: top-level folders with file counts and main languages. Cached for 5 minutes."""
    if time.time() - _map_cache["t"] < 300 and _map_cache["text"]:
        return _map_cache["text"]
    c = _db()
    rows = c.execute("SELECT path FROM files").fetchall(); c.close()
    proj: dict[str, dict] = {}
    for (p,) in rows:
        for r in ROOTS:
            if p.startswith(str(r) + os.sep):
                rel = Path(p).relative_to(r).parts
                key = str(r.name) + "/" + (rel[0] if len(rel) > 1 else "")
                if len(rel) > 2 and r.name == "Desktop":  # projects sit one level inside "my ai"
                    key = f"{r.name}/{rel[0]}/{rel[1]}"
                d = proj.setdefault(key.rstrip("/"), {"n": 0, "ext": {}})
                d["n"] += 1; e = Path(p).suffix.lower() or "other"; d["ext"][e] = d["ext"].get(e, 0) + 1
                break
    parts = []
    for k, d in sorted(proj.items(), key=lambda x: -x[1]["n"])[:10]:
        top = ",".join(e for e, _ in sorted(d["ext"].items(), key=lambda x: -x[1])[:2])
        parts.append(f"{k} ({d['n']} files, {top})")
    text = "; ".join(parts)[:max_chars]
    _map_cache.update(t=time.time(), text=text)
    return text


def read_file(path: str, start_line: int = 1, lines: int = 80) -> str:
    """Read part of a text file: `lines` lines starting at start_line."""
    p = Path(path).expanduser()
    if SECRET.search(p.name):
        return "refused: that file looks like it holds secrets"
    try:
        data = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return f"cannot read: {e}"
    a = max(1, start_line) - 1
    return f"{p} lines {a + 1}-{min(len(data), a + lines)} of {len(data)}\n" + "\n".join(data[a:a + lines])[:4000]


def start_background(interval: int = 600):
    """Index now and every `interval` seconds, quietly, at low priority."""
    def loop():
        try:
            os.nice(10)
        except OSError:
            pass
        while True:
            try:
                refresh()
            except Exception as e:  # never let the index take Jeb down
                print("indexer error:", e)
            time.sleep(interval)
    threading.Thread(target=loop, daemon=True, name="indexer").start()
