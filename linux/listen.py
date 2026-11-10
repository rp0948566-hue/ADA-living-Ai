#!/usr/bin/env python3
"""Jev for Linux: speech in, the counterpart of Jev.swift's Whisper path (whisperTick / whisperFinal).
One long-lived process so the model loads once. stdin: start | stop | cancel. stdout JSON lines:
{"ready":true} {"level":0..1} {"words":"live text"} {"final":"text"} {"error":"why"}.
Run with PYTHONPATH=~/.local/share/jev/py (faster-whisper lives there; the system Python is externally managed)."""
import json, os, re, select, subprocess, sys, threading, time
import numpy as np
import models, tier, voiceid

RATE = 16000
PROFILE = tier.profile()   # picked from this machine's cores/RAM/GPU, or JEV_TIER override (see tier.py)
MODEL = os.environ.get('JEV_WHISPER', PROFILE['whisper'])
DEVICE = os.environ.get('JEV_WHISPER_DEVICE', PROFILE['whisper_device'])
LANG = os.environ.get('JEV_WHISPER_LANG') or None   # None = detect, like whisperLanguage "auto"
IDLE_UNLOAD = 0 if PROFILE['both_warm'] else 90   # 0 = never unload (strong machines keep it warm); weak machines free the RAM after 90s quiet


def out(**k): print(json.dumps(k), flush=True)


def _prefs():
    for d in (os.environ.get('JEV_DIR'), os.path.expanduser('~/.config/jev')):
        try:
            with open(os.path.join(d, 'settings.json')) as f: return json.load(f)
        except (TypeError, OSError, ValueError): continue
    return {}


STOPS = {'stop', 'quiet', 'enough', 'silence', 'shush', 'pause', 'cancel', 'wait'}


def stop_hit(text):
    """Barge-in: only a short utterance that is a stop word counts, so Jev's own voice through the speakers (long sentences) never trips it."""
    words = re.findall(r"[a-z']+", text.lower())
    return 0 < len(words) <= 4 and (bool(STOPS & set(words)) or words[:2] in (['shut', 'up'], ['be', 'quiet']) or 'jev' in words and len(words) <= 3 and bool(STOPS & set(words)))


OPEN_END = {'and', 'but', 'or', 'so', 'because', 'then', 'if', 'that', 'the', 'a', 'an', 'to', 'of', 'with', 'for', 'in', 'on', 'at', 'from', 'my', 'um', 'uh', 'er', 'like', 'is', 'are', 'was'}


def quiet_needed(words):
    """Seconds of silence that end the turn, from the live words so far: a thought left hanging ("...and", a comma) gets longer
    so a thinking pause does not cut the user off; a finished sentence sends sooner."""
    t = words.strip().lower()
    if not t: return .8
    if t.endswith((',', '...', '…', '-')) or re.findall(r"[a-z']+", t)[-1:] and re.findall(r"[a-z']+", t)[-1] in OPEN_END and not t.endswith(('.', '?', '!')): return 1.8
    return .6 if t.endswith(('.', '?', '!')) else .8


def wake(text_of, name='Jev', stop=False):
    """Wake-word mode (Mac wakeTick): listen for short utterances, say {"wake": text} when one holds the name, until cancel/start."""
    name = (name.strip() or 'Jev').lower()
    hit = stop_hit if stop else (lambda t: re.search(r'(?<![\w])' + re.escape(name) + r'(?![\w])', t.lower()) is not None)
    rec = subprocess.Popen(['pw-record', '--rate', str(RATE), '--channels', '1', '--format', 's16', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    buf, quiet = [], 0   # an utterance = voiced audio, closed by 0.6 s of silence (or 5 s), then transcribed once
    try:
        while True:
            r, _, _ = select.select([rec.stdout, sys.stdin], [], [], .2)
            if sys.stdin in r:
                c = sys.stdin.readline().strip()
                if not c.startswith(('wake', 'interrupt')): return c   # cancel / start / EOF leave wake mode; the caller handles a 'start' that arrived first
            if rec.stdout not in r: continue
            chunk = os.read(rec.stdout.fileno(), 1 << 20)
            if not chunk: return
            a = np.frombuffer(chunk[:len(chunk) // 2 * 2], np.int16).astype(np.float32) / 32768
            voiced = float(np.sqrt(np.mean(a * a))) * 12 > .1
            if voiced: buf.append(a); quiet = 0
            elif buf: buf.append(a); quiet += len(a)
            if buf and (quiet > .6 * RATE or sum(map(len, buf)) > 5 * RATE):
                audio, buf, quiet = np.concatenate(buf), [], 0
                if len(audio) > .25 * RATE and hit(text_of(audio)): out(**({'stop': True} if stop else {'wake': name})); return
    finally:
        rec.terminate(); rec.wait()


class Loader:
    """Loads the Whisper model on first use and, on a weak machine (IDLE_UNLOAD>0), frees it again after
    a quiet stretch -- the RAM matters more there than the reload time. A strong machine (IDLE_UNLOAD==0,
    tier.py's both_warm) just loads once and keeps it, exactly like before this file supported tiers."""
    def __init__(self):
        self.model, self.last_used, self.lock = None, 0.0, threading.Lock()
        if IDLE_UNLOAD: threading.Thread(target=self._reaper, daemon=True).start()

    def _reaper(self):
        while True:
            time.sleep(10)
            with self.lock:
                if self.model is not None and time.time() - self.last_used > IDLE_UNLOAD:
                    self.model = None   # drop the reference; faster-whisper/ctranslate2 frees the RAM on GC

    def get(self):
        with self.lock:
            self.last_used = time.time()
            if self.model is None:
                from faster_whisper import WhisperModel
                self.model = WhisperModel(MODEL, device=DEVICE, compute_type='int8' if DEVICE == 'cpu' else 'float16',
                                          cpu_threads=max(2, (os.cpu_count() or 4) // 2))
            return self.model


def main():
    loader = Loader()
    pending_mb = models.pending_download_mb(MODEL, PROFILE['piper'])
    allow = os.environ.get('JEV_ALLOW_DOWNLOAD', '1') != '0'   # settings.json "allowDownload": false -> host.py sets this to 0
    if pending_mb and not allow:
        out(error=f'This voice needs a {pending_mb} MB download, which is turned off in Settings.'); return
    os.environ['HF_HUB_OFFLINE'] = '0' if allow else '1'   # allowDownload off: never let faster-whisper fetch anything, not even a missing model
    if pending_mb: out(downloading=pending_mb)   # disclosed on the box's own status line, never silent (see tier.py / the Linux brief)
    try:
        loader.get()   # fail fast if the model can't load at all, same as before; this is also where the download (if any) happens
    except Exception as e:   # missing package or model download failed: the box says so, like "Whisper isn't set up yet"
        out(error=f'Speech isn’t set up yet: {e}'); return
    if IDLE_UNLOAD: loader.model = None   # loaded just to check it works; a weak machine goes back to lazy from here
    out(ready=True)

    def text_of(audio):
        model = loader.get()
        segs, _ = model.transcribe(audio, language=LANG, beam_size=1, vad_filter=True, condition_on_previous_text=False, initial_prompt=models.vocab_prompt(_prefs().get('vocabulary')))
        return ' '.join(s.text.strip() for s in segs).strip()

    pending = ''
    while True:
        cmd = pending or sys.stdin.readline(); pending = ''   # readline, not iteration: select() below must see what is still unread
        if not cmd: return
        if _prefs().get('micOff'):   # the hard mute: no recorder is ever opened while it is on
            if cmd.strip() == 'start': out(denied='The microphone is off. Turn it on in Settings, or type.')
            continue
        if cmd.strip().startswith('interrupt'):
            pending = wake(text_of, stop=True) or ''; pending = pending + '\n' if pending == 'start' else ''; continue
        if cmd.strip().startswith('wake'):
            pending = wake(text_of, cmd.strip()[4:]) or ''; pending = pending + '\n' if pending == 'start' else ''; continue
        if cmd.strip() != 'start': continue
        rec = subprocess.Popen(['pw-record', '--rate', str(RATE), '--channels', '1', '--format', 's16', '-'],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        # times are audio samples, not wall time: transcribing pauses this loop, and the backlog must not look like speech going on
        buf, total, voiced_at, last_tick, words, ended, rms = [], 0, -1, 0.0, '', None, []
        while ended is None:
            r, _, _ = select.select([rec.stdout, sys.stdin], [], [], .1)
            if sys.stdin in r:
                c = sys.stdin.readline().strip()
                if c in ('stop', 'cancel', ''): ended = c or 'cancel'; break
            if rec.stdout in r:
                chunk = os.read(rec.stdout.fileno(), 1 << 20)   # everything waiting
                if not chunk: out(error='No microphone is available. Connect one and try again.'); ended = 'cancel'; break
                a = np.frombuffer(chunk[:len(chunk) // 2 * 2], np.int16).astype(np.float32) / 32768
                buf.append(a)
                for i in range(0, len(a), 1600):   # 0.1 s blocks
                    block = a[i:i + 1600]
                    r_ = float(np.sqrt(np.mean(block * block))); rms.append(r_)
                    # voiced = clearly above this room's noise floor (10th percentile so far), so steady fan/hiss noise never keeps it listening
                    if r_ * 12 > max(.1, 2.5 * np.percentile(rms, 10) * 12): voiced_at = total + i + len(block)
                total += len(a)
                tail = a[-1600:]
                out(level=round(float(min(1, np.sqrt(np.mean(tail * tail)) * 12)), 3))
            if voiced_at >= 0 and time.time() - last_tick > 1.2 and buf:   # live words, like whisperTick
                words = text_of(np.concatenate(buf)) or words
                last_tick = time.time()
                out(words=words)
            if voiced_at >= 0 and total - voiced_at > quiet_needed(words) * RATE: ended = 'stop'   # quiet after speech sends it; how long depends on whether the sentence sounds finished (the final pass below transcribes if no live words yet)
            elif voiced_at < 0 and total > 8 * RATE: ended = 'cancel'   # nothing heard in 8 s
            elif total > 60 * RATE: ended = 'stop'   # the 60 s recording limit
        rec.terminate(); rec.wait()
        if ended == 'stop' and buf and not voiceid.allowed(np.concatenate(buf), _prefs().get('ownerVoice')): out(denied=voiceid.DENIED)
        elif ended == 'stop' and buf:
            out(final=text_of(np.concatenate(buf)) or words)
        else:
            out(final='')


if __name__ == '__main__':
    main()
