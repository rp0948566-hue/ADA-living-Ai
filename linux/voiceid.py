"""Owner-voice lock: a basic voiceprint made with numpy only, so no model download.
It keeps out other voices in the room (a child, a guest, the TV); it is NOT a security lock: a recording of
the owner, or a similar voice, can pass. Typing always works, so the owner is never locked out.
shortcut: spectral-shape print with one fixed threshold, not calibrated on many real voices; upgrade to a
speaker-embedding model (e.g. ECAPA) if this must resist a determined person."""
import os
import numpy as np

RATE = 16000
PRINT = os.path.join(os.environ.get('JEV_DIR') or os.path.expanduser('~/.config/jev'), 'voiceprint.npy')
THRESHOLD = .93
DENIED = 'That did not sound like the owner. Type instead, or turn Owner voice off in Settings.'


def _mel(bands=32, size=400):
    """Triangular mel filters, 100 Hz to 7 kHz, for a `size`-sample frame."""
    mel = lambda f: 2595 * np.log10(1 + f / 700); inv = lambda m: 700 * (10 ** (m / 2595) - 1)
    edges = inv(np.linspace(mel(100), mel(7000), bands + 2)); freqs = np.fft.rfftfreq(size, 1 / RATE)
    return np.array([np.clip(np.minimum((freqs - lo) / (mid - lo), (hi - freqs) / (hi - mid)), 0, None) for lo, mid, hi in zip(edges, edges[1:], edges[2:])])


MEL = _mel()


def embed(audio):
    """Voiceprint of float mono 16 kHz audio: mean and spread of the loudness-normalised log-mel spectrum over voiced frames. None when under 1 s is voiced."""
    audio = np.asarray(audio, np.float32)
    if len(audio) < 400: return None
    frames = np.lib.stride_tricks.sliding_window_view(audio, 400)[::160] * np.hanning(400)
    power = np.abs(np.fft.rfft(frames, axis=1)) ** 2
    energy = power.sum(axis=1)
    voiced = power[energy > max(np.median(energy), 1e-7)]
    if len(voiced) < 50: return None   # 50 voiced frames of the louder half = about 1 s of speech
    logmel = np.log(voiced @ MEL.T + 1e-10)
    logmel -= logmel.mean(axis=1, keepdims=True)   # loudness and mic distance drop out
    v = np.concatenate([logmel.mean(axis=0), logmel.std(axis=0)])
    return v / (np.linalg.norm(v) or 1)


def allowed(audio, on, path=PRINT):
    """True when this request may run. Off: forget the print. On with no print yet: the first clear voice becomes the owner."""
    if not on:
        try: os.remove(path)
        except OSError: pass
        return True
    v = embed(audio)
    try: owner = np.load(path)
    except (OSError, ValueError): owner = None
    if owner is None:
        if v is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), 'wb') as f: np.save(f, v)
        return True
    return v is not None and float(v @ owner) >= THRESHOLD   # too short to judge = not let in; typing still works
