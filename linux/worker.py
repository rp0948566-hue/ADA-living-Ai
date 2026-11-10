"""One ask: spawns `jev.py --wait` exactly like Jev.swift's spawn()/run(), feeds it the request, and yields its output lines.
Protocol (Jev.swift ~3991-4130): env JEV_UI/FRONT/SCREEN/COMMIT; write "go" to the commit file once the words are final;
send one JSON line {"front","task",...} on stdin; read prefixed lines on stdout."""
import json, os, subprocess, sys, tempfile, threading, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAIN = os.path.join(ROOT, 'jev.py')


class Worker:
    def __init__(self, on_line, on_exit, front='', screen='', env=None):
        self.commit = os.path.join(tempfile.gettempdir(), 'jev-commit-' + uuid.uuid4().hex)
        e = dict(os.environ, JEV_UI='1', JEV_FRONT=front, JEV_SCREEN=screen, JEV_COMMIT=self.commit,
                 JEV_SELECTION='', JEV_CARET='', JEV_FOCUS_GUARD='1', JEV_APP=os.path.join(ROOT, 'linux', 'native'))
        e.update(env or {})
        self.p = subprocess.Popen(['/bin/sh', BRAIN, '--wait'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=e, text=True, bufsize=1)
        self.on_line, self.on_exit, self.front = on_line, on_exit, front
        threading.Thread(target=self._read, daemon=True).start()

    def run(self, task, **extra):
        with open(self.commit, 'w') as f: f.write('go')
        try:
            self.p.stdin.write(json.dumps({'front': self.front, 'task': task, **extra}) + '\n'); self.p.stdin.close()
        except OSError: self.cancel()

    def _read(self):
        for line in self.p.stdout: self.on_line(line.rstrip('\n'))
        code = self.p.wait()
        try: os.remove(self.commit)
        except OSError: pass
        self.on_exit(code)

    def cancel(self):
        try: os.killpg(self.p.pid, 15)
        except OSError: pass
