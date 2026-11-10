"""Which voice-model file a tier needs, and whether it's on disk yet. No download logic here: listen.py and
voice.py already know how to fetch their own models (faster-whisper / Piper do it on first use); this module
just names the file each tier wants and reports size/presence so host.py can show one status line while it
happens. Nothing here talks to the network -- it only looks at local files."""
import os

HOME = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'jev')
VOICES = os.path.join(HOME, 'voices')

# approximate download sizes, for the status line only -- not used to verify anything
WHISPER_MB = {'tiny': 75, 'base': 142, 'small': 462, 'large-v3-turbo': 1600}
PIPER_MB = {'low': 20, 'medium': 61, 'high': 109}

PIPER_VOICES = {   # size tier -> a voice file that exists at that quality; medium ships in the installer today
    'low': 'en_US-ryan-low',
    'medium': 'en_US-ryan-medium',
    'high': 'en_US-ryan-high',
}


def piper_model_name(size):
    return PIPER_VOICES.get(size, PIPER_VOICES['medium'])


def piper_ready(size):
    return os.path.exists(os.path.join(VOICES, piper_model_name(size) + '.onnx'))


def whisper_cache_dir():
    return os.path.join(os.path.expanduser('~/.cache/huggingface/hub'))


def whisper_ready(size):
    """faster-whisper names its HF snapshot folder after the model; a rough existence check is enough here --
    the real load (listen.py) is the source of truth and will download on first use if this says no."""
    try:
        return any('faster-whisper-' + size in d for d in os.listdir(whisper_cache_dir()))
    except OSError:
        return False


def pending_download_mb(whisper_size, piper_size):
    """What's left to fetch for this tier, for the "Setting up voice (N MB)" status line."""
    mb = 0
    if not whisper_ready(whisper_size):
        mb += WHISPER_MB.get(whisper_size, 0)
    if not piper_ready(piper_size):
        mb += PIPER_MB.get(piper_size, 0)
    return mb


def vocab_prompt(text, limit=220):
    """Settings "My words" -> Whisper's initial_prompt, so names and terms are heard as written. Empty -> None."""
    words = [w.strip() for w in str(text or '').replace('\n', ',').split(',') if w.strip()]
    out = ''
    for w in words:
        if len(out) + len(w) + 2 > limit: break
        out += (', ' if out else '') + w
    return out or None
