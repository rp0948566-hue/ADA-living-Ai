"""Tiny local web UI (stdlib only), localhost-bound. Works on every OS with any browser."""
import json, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import agent

PAGE = b"""<!doctype html><meta charset=utf-8><title>Jev-X</title>
<body style="font:15px system-ui;max-width:720px;margin:2rem auto;padding:0 1rem"><h2>Jev-X</h2>
<form onsubmit="go(event)"><input id=t autofocus style="width:80%;padding:.5rem" placeholder="What should I do?"><button>Go</button></form>
<pre id=o style="white-space:pre-wrap"></pre><script>
async function go(e){e.preventDefault();const t=document.getElementById('t').value,o=document.getElementById('o');
o.textContent='working...';const r=await fetch('/ask',{method:'POST',body:JSON.stringify({task:t})});const j=await r.json();
o.textContent=j.log.join('\\n')+'\\n\\n'+j.answer}</script>"""
_lock = threading.Lock()   # one task at a time: it drives the one real mouse and keyboard


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, body, ctype):
        self.send_response(code); self.send_header('content-type', ctype); self.send_header('content-length', str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        self._send(200, PAGE, 'text/html') if self.path == '/' else self._send(404, b'', 'text/plain')

    def do_POST(self):
        if self.path != '/ask': return self._send(404, b'', 'text/plain')
        try: task = json.loads(self.rfile.read(int(self.headers.get('content-length', 0)))).get('task', '')
        except ValueError: return self._send(400, b'{}', 'application/json')
        log = []
        with _lock:
            try: answer = agent.run(task, on_event=log.append)[0]
            except RuntimeError as e: answer = f'error: {e}'
        self._send(200, json.dumps({'log': log, 'answer': answer}).encode(), 'application/json')


def serve(port=7777):
    srv = ThreadingHTTPServer(('127.0.0.1', port), H)   # 127.0.0.1 only: this UI can run shell commands
    print(f'Jev-X UI: http://127.0.0.1:{port}')
    threading.Timer(0.5, lambda: webbrowser.open(f'http://127.0.0.1:{port}')).start()
    srv.serve_forever()
