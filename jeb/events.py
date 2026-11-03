"""Tiny local event bus + server for the GUI. Localhost only, no dependencies, nothing leaves the machine.
GET /        -> gui/index.html
GET /events  -> server-sent events (JSON per line)"""
import json
import urllib.request
from urllib.parse import parse_qs, urlparse
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 7777
_subs: list[queue.Queue] = []
_state = {"state": "idle", "model": "", "log": []}
_lock = threading.Lock()


def subscribers() -> int:
    with _lock:
        return len(_subs)


def emit(kind: str, **data):
    ev = {"t": time.time(), "kind": kind, **data}
    with _lock:
        if kind == "state":
            _state["state"] = data["state"]
        elif kind == "model":
            _state["model"] = data["name"]
        elif kind in ("user", "jeb", "tool"):
            _state["log"] = (_state["log"] + [ev])[-30:]
        subs = list(_subs)
    for q in subs:
        q.put(ev)


UA = {"User-Agent": "JebAI/1.0 (personal local assistant, not public)"}
_cache: dict = {}


def _fetch(key: str, url: str, ttl: float, timeout: int = 20):
    """GET json with a ttl cache; a failed refresh serves the stale copy so the GUI keeps flying."""
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            data = json.loads(r.read())
        _cache[key] = (now, data)
        return data
    except Exception:
        return hit[1] if hit else None


def flights_global():
    """OpenSky anonymous allows ~100 global pulls/day, so one pull per 15 min; the GUI dead-reckons between pulls."""
    d = _fetch("global", "https://opensky-network.org/api/states/all", 900, 30)
    if not d:
        return {"t": 0, "f": []}
    f = [[s[0], (s[1] or "").strip(), s[6], s[5], s[7] or s[13] or 0, s[9] or 0, s[10] or 0, s[11] or 0, s[8]]
         for s in d.get("states", []) if s[5] is not None and s[6] is not None and not s[8]]
    return {"t": d.get("time", 0), "f": f}


def flights_near(lat: float, lon: float):
    d = _fetch(f"n{round(lat,1)},{round(lon,1)}", f"https://api.adsb.lol/v2/point/{lat:.4f}/{lon:.4f}/250", 5, 10)
    return {"t": time.time(), "ac": (d or {}).get("ac", [])}


def photo(reg: str):
    d = _fetch("p" + reg, "https://api.planespotters.net/pub/photos/reg/" + urllib.request.quote(reg), 86400, 10)
    ph = (d or {}).get("photos") or []
    return {"src": ph[0]["thumbnail_large"]["src"], "by": ph[0].get("photographer", "")} if ph else {}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/flights":
            self._json(flights_global())
        elif u.path == "/near":
            try:
                self._json(flights_near(float(q["lat"][0]), float(q["lon"][0])))
            except (KeyError, ValueError):
                self.send_error(400)
        elif u.path == "/photo":
            self._json(photo(q.get("reg", [""])[0][:12]))
        elif self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            q: queue.Queue = queue.Queue()
            with _lock:
                _subs.append(q)
                snap = dict(_state)
            try:
                self.wfile.write(f"data: {json.dumps({'kind': 'snapshot', **snap})}\n\n".encode()); self.wfile.flush()
                while True:
                    try:
                        ev = q.get(timeout=15)
                        self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode())
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with _lock:
                    _subs.remove(q)
        elif self.path in ("/", "/index.html"):
            body = (Path(__file__).parent / "gui" / "index.html").read_bytes()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            self.send_error(404)


def serve():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
