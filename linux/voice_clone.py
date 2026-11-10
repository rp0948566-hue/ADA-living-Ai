"""Voice cloning on Linux (optional, heavy): a free ElevenLabs-style clone with Coqui XTTS v2. From a ~6-20s sample of a voice
it speaks any text in that voice, with emotion/tone. This is NOT installed by default: it pulls in PyTorch (~2 GB) and the XTTS
model (~1.8 GB), and on CPU each sentence takes many seconds. For fast everyday speech use Piper (voice.py); use cloning to make
specific clips.

Setup (the AI can run it; it's a big download, so Jev asks first):
  pip install --target ~/.local/share/jev/py coqui-tts torchaudio six soundfile
  (torchcodec is not needed: this module reads samples with soundfile)
  then this module downloads the XTTS model on first use (it accepts the model's non-commercial license via COQUI_TOS_AGREED=1).

Use:
  voice_clone.py add   <name> <sample.wav>     remember a voice sample
  voice_clone.py say    <name> "text" [out.wav]  speak text in that voice (plays it; writes out.wav if given)
  voice_clone.py list"""
import glob, json, os, subprocess, sys

HOME = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'jev')
CLONES = os.path.join(HOME, 'clones')   # <name>.wav samples + clones.json
PY = os.path.join(HOME, 'py')
if PY not in sys.path: sys.path.insert(0, PY)
MODEL = 'tts_models/multilingual/multi-dataset/xtts_v2'


def have_tts():
    try:
        import TTS  # noqa: F401
        return True
    except ImportError:
        return False


def sample_path(name):
    return os.path.join(CLONES, name + '.wav')


def add(name, wav):
    if not os.path.exists(wav): return f'No file: {wav}'
    os.makedirs(CLONES, mode=0o700, exist_ok=True)
    import shutil
    shutil.copy(wav, sample_path(name))
    return f'Saved voice sample "{name}". Use: voice_clone.py say {name} "hello".'


def speak(name, text, out=None, play=True):
    sample = sample_path(name)
    if not os.path.exists(sample): return f'No voice named "{name}". Add one: voice_clone.py add {name} <sample.wav>.'
    if not have_tts():
        return ('Voice cloning is not installed. It is a big download (~2 GB, PyTorch + the XTTS model) and slow without a free GPU. '
                'Install it with: pip install --target ~/.local/share/jev/py coqui-tts torchaudio six soundfile')
    os.environ['COQUI_TOS_AGREED'] = '1'   # XTTS is non-commercial; this records that the user accepted it by installing
    out = out or os.path.join(HOME, 'clone.wav')
    import torch, torchaudio, soundfile
    def load(path, *a, **k):   # torchaudio.load needs torchcodec + ffmpeg 4-7 (system has 8); soundfile reads wav/flac/ogg directly
        data, rate = soundfile.read(path, dtype='float32', always_2d=True)
        return torch.from_numpy(data.T.copy()), rate
    torchaudio.load = load
    from TTS.api import TTS
    try:   # the GPU is shared with llama-server: use it only if ~3 GB is free, else the CPU (slower, never crashes)
        import torch; gpu = torch.cuda.is_available() and torch.cuda.mem_get_info()[0] > 3 * 2**30
    except Exception: gpu = False
    tts = TTS(MODEL).to('cuda' if gpu else 'cpu')   # downloads the model on first run
    tts.tts_to_file(text=text, speaker_wav=sample, language='en', file_path=out)
    if play:
        import voice
        argv = voice.player(out)
        if argv: subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f'Spoke in "{name}"' + (f' and wrote {out}' if out else '')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['add'] and len(a) == 3: print(add(a[1], a[2]))
    elif a[:1] == ['say'] and len(a) >= 3: print(speak(a[1], a[2], a[3] if len(a) > 3 else None))
    elif a[:1] == ['list']:
        print('\n'.join(os.path.basename(f)[:-4] for f in sorted(glob.glob(os.path.join(CLONES, '*.wav')))) or 'no cloned voices yet')
    else: print(__doc__)
