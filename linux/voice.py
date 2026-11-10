"""Jev's spoken voice on Linux, the counterpart of the Mac's AVSpeech read-aloud. Neural, offline, free: Piper.
`speak(text, tone)` synthesizes and plays; the `say` shim calls it. Falls back to spd-say/espeak-ng when Piper or the voice
model is missing, so speech never hard-fails.

Voice model: ~/.local/share/jev/voices/<name>.onnx (a deep natural male, en_US-ryan-medium, by default; the user's pick in
settings "voiceName" wins). Tone presets change pace/volume (Piper has no pitch knob; for the deep voice we resample and EQ in numpy; set
"voicePitch" in semitones, default -1.5: the calm Ultron-style voice). True voice cloning is voice_clone.py (optional, heavy)."""
import glob, json, os, re, shutil, subprocess, sys, threading, time, wave
import tier

HOME = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'jev')
VOICES = os.path.join(HOME, 'voices')
PY = os.path.join(HOME, 'py')
if PY not in sys.path: sys.path.insert(0, PY)

DEEP = -2.5   # semitones: low, cold, menacing
TONES = {'normal': (1.15, 1.0), 'calm': (1.15, 0.95), 'deep': (1.18, 1.0), 'fast': (0.85, 1.0), 'soft': (1.1, 0.8)}

# On a strong machine (tier.py both_warm) keep the ~1s Piper load out of every sentence; a weak machine loads
# fresh each time and lets it go right away, which is how this file always behaved before tiers existed.
_WARM = tier.profile()['both_warm']
_cache = {'path': None, 'voice': None, 'used': 0.0}
_lock = threading.Lock()


def _loaded(model):
    with _lock:
        _cache['used'] = time.time()
        if _cache['path'] != model:
            from piper import PiperVoice
            _cache['voice'], _cache['path'] = PiperVoice.load(model), model
        return _cache['voice']


def _reap():
    while True:
        time.sleep(30)
        with _lock:
            if _cache['voice'] is not None and time.time() - _cache['used'] > 90:
                _cache['voice'] = _cache['path'] = None


if not _WARM: threading.Thread(target=_reap, daemon=True).start()   # a strong machine (both_warm) just keeps it loaded, no reaper needed


def prefs():
    for p in (os.environ.get('JEV_DIR'), os.path.expanduser('~/.config/jev')):
        try:
            with open(os.path.join(p, 'settings.json')) as f: return json.load(f)
        except (TypeError, OSError, ValueError): continue
    return {}


def model_path(text=''):
    hindi = sorted(glob.glob(os.path.join(VOICES, 'hi_IN-*.onnx'))) if re.search('[\u0900-\u097f]', text) else []
    if hindi: return hindi[0]   # Hindi words need a Hindi voice; the English one reads Devanagari as noise
    p = prefs()
    name = p.get('voiceName')
    if name and os.path.exists(os.path.join(VOICES, name + '.onnx')): return os.path.join(VOICES, name + '.onnx')
    found = sorted(glob.glob(os.path.join(VOICES, '*.onnx')))
    return found[0] if found else None


def player(path):
    for argv in (['paplay', path], ['aplay', '-q', path], ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', path], ['pw-play', path]):
        if shutil.which(argv[0]): return argv
    return None


def fallback(text):
    if shutil.which('spd-say'): return subprocess.Popen(['spd-say', '-w', text])
    if shutil.which('espeak-ng'): return subprocess.Popen(['espeak-ng', text])
    sys.stderr.write('no speech engine\n'); return None


def synth(text, tone='normal', out=None, shift=0.0, gain=1.0, pace=1.0):
    """Make a wav; return its path, or None if Piper/model is unavailable."""
    model = model_path(text)
    if not model: return None
    try:
        from piper.config import SynthesisConfig
        v = _loaded(model)
    except ImportError:
        return None
    length, volume = TONES.get(tone, TONES['normal'])
    st = float(prefs().get('voicePitch', DEEP)) + shift   # semitones; negative = deeper. Default is the big, deep "AI" voice.
    ratio = 2 ** (-st / 12)   # >1: the clip is stretched, so it comes out deeper (and bigger); synthesize faster to keep the pace
    out = out or os.path.join(HOME, 'say.wav')
    with wave.open(out, 'wb') as w:
        v.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=length * pace / ratio, volume=volume))
    if st or gain != 1: deepen(out, ratio, gain)
    return out


def deepen(path, ratio, gain=1.0):
    """The cold AI voice: low and calm, with a metallic edge and a short cold room. Clear words come first. Resample for the pitch,
    shape it so words stay clear, then add the machine layer (comb ring, faint ring-mod, tiny reverb). Pure numpy, no sox needed."""
    import numpy as np
    with wave.open(path, 'rb') as w: sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels(); raw = w.readframes(n)
    x = np.frombuffer(raw, dtype='<i2').astype(np.float32).reshape(-1, ch).mean(axis=1) / 32768
    if not len(x): return
    if ratio != 1: x = np.interp(np.arange(0, len(x) - 1, 1 / ratio), np.arange(len(x)), x)
    x = np.concatenate([x, np.zeros(int(sr * 0.5), np.float32)])   # room for the tail
    f = np.fft.rfftfreq(len(x), 1 / sr)
    db = (5.5 / (1 + (f / 190) ** 3)                                               # weight: deep and dangerous
          + 5.0 * np.exp(-0.5 * ((np.log2(np.maximum(f, 1) / 3000)) / 0.7) ** 2)   # presence: every word clear
          - 2.0 * np.exp(-0.5 * ((np.log2(np.maximum(f, 1) / 400)) / 0.6) ** 2)    # mud cut
          - 8.0 * np.clip((f - 8000) / 3500, 0, 1))
    x = np.fft.irfft(np.fft.rfft(x) * 10 ** (db / 20), len(x)).astype(np.float32)
    d1, d2 = int(sr * 0.0045), int(sr * 0.0105)                                    # comb: the thin metal ring
    m = x.copy(); m[d1:] += 0.36 * x[:-d1]; m[d2:] += 0.2 * x[:-d2]
    t = np.arange(len(x)) / sr
    x = 0.82 * m + 0.18 * m * np.sin(2 * np.pi * 70 * t)                              # faint ring-mod: machine edge
    rng = np.random.default_rng(7); n_ir = int(sr * 0.45)
    ir = rng.standard_normal(n_ir).astype(np.float32) * np.exp(-np.arange(n_ir) / (sr * 0.09)); ir[0] = 0
    wet = np.fft.irfft(np.fft.rfft(x, len(x) + n_ir) * np.fft.rfft(ir, len(x) + n_ir))[:len(x)]
    x = x + 0.14 * wet / max(1e-6, float(np.abs(wet).max())) * float(np.abs(x).max())
    x = np.tanh(1.6 * x) / np.tanh(1.6)
    x *= min(0.98, 0.89 * gain) / max(1e-6, float(np.abs(x).max()))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype('<i2').tobytes())


# {tag}: what the AI asks of its own voice, per piece of speech -> (pace multiplier, loudness, extra semitones)
TAGS = {'calm': (1.12, 0.9, -0.5), 'soft': (1.15, 0.6, -0.5), 'deep': (1.1, 1.0, -2.0), 'menace': (1.28, 0.95, -2.5),
        'loud': (0.95, 1.1, 0.0), 'fast': (0.82, 1.0, 0.0), 'slow': (1.3, 1.0, -0.5)}


def parse(piece):
    """'{menace} I know.' -> ('I know.', pace, gain, shift). Several tags combine; unknown tags are dropped."""
    import re
    pace, gain, shift = 1.0, 1.0, 0.0
    for t in re.findall(r'\{(\w+)\}', piece):
        p, g, sh = TAGS.get(t, (1.0, 1.0, 0.0)); pace *= p; gain *= g; shift += sh
    return re.sub(r'\{\w+\}', '', piece).strip(), pace, min(gain, 1.2), max(-5, min(2, shift))


class Speaker:
    """Speaks pieces as they arrive: one thread makes the audio of the next piece while another plays the current one, so there is no gap
    and the first words start as soon as the first piece exists."""
    def __init__(self):
        import queue, threading
        self.todo, self.ready, self.proc, self.gen = queue.Queue(), queue.Queue(), None, 0
        self.busy = 0; self.lock = threading.Lock()
        threading.Thread(target=self._make, daemon=True).start(); threading.Thread(target=self._play, daemon=True).start()

    def say(self, piece, tone='normal'):
        text, pace, gain, shift = parse(piece)
        if text:
            with self.lock: self.busy += 1
            self.todo.put((self.gen, text, tone, pace, gain, shift))

    def _make(self):
        n = 0
        while True:
            gen, text, tone, pace, gain, shift = self.todo.get()
            if gen != self.gen: self._done(); continue
            n += 1; path = os.path.join(HOME, f'say-stream-{n % 16}.wav')
            try: wav = synth(text, tone, path, shift=shift, gain=gain, pace=pace)
            except Exception: wav = None
            self.ready.put((gen, wav, text))

    def _play(self):
        while True:
            gen, wav, text = self.ready.get()
            try:
                if gen == self.gen:
                    argv = player(wav) if wav else None
                    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if argv else fallback(text)
                    self.proc = p
                    if p: p.wait()
            finally: self._done()

    def _done(self):
        with self.lock: self.busy -= 1

    def speaking(self): return self.busy > 0

    def stop(self):
        self.gen += 1
        if self.proc and self.proc.poll() is None: self.proc.terminate()


def speak(text, tone='normal'):
    """Synthesize and play, blocking until done (so the box can hide after). Returns the Popen, or None."""
    text = text.strip()
    if not text: return None
    wav = synth(text, tone)
    if not wav: return fallback(text)
    argv = player(wav)
    if not argv: return fallback(text)
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    tone = 'normal'
    args = sys.argv[1:]
    if args[:1] == ['-v']:   # say -v <voice|?> compatibility
        if args[1:2] == ['?']:
            for f in sorted(glob.glob(os.path.join(VOICES, '*.onnx'))): print(os.path.basename(f)[:-5])
            sys.exit(0)
        args = args[2:]
    if args[:1] == ['--tone'] and len(args) > 1: tone = args[1]; args = args[2:]
    text = ' '.join(args) or sys.stdin.read()
    p = speak(text, tone)
    if p: p.wait()
