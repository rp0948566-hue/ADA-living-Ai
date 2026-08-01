"""ElevenLabs TTS (with offline fallback) + mic STT + auto-translate for the Iris GUI.

Speaking: ElevenLabs "Jessica" (Playful, Bright, Warm) — a premade voice that
works on the free API plan, unlike the old Voice-Library pick which 402'd.
Streamed back as raw PCM and played via sounddevice (no temp files, no mp3
decoder), with a volume boost applied since the raw output was too quiet.
Falls back automatically to pyttsx3 (Windows SAPI, fully offline) whenever
ElevenLabs is unavailable — no key, no credit, no internet, rate-limited.
Either way, Iris always has *some* voice.

Listening: SpeechRecognition's microphone capture (voice-activity detection,
same as before) feeding OpenAI Whisper (whisper/ — cloned locally, see
README.md removed / LICENSE kept per its MIT terms) running fully offline on
this machine. No Google Speech API, no internet dependency for recognition
itself. Whisper's task="translate" mode transcribes AND translates to
English in one pass, so whatever language Rudra spoke in — Hindi, English,
Hinglish — comes out as English text with no separate translation call.
"""
import os
import tempfile
import threading

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import whisper as _openai_whisper
except Exception:
    _openai_whisper = None

try:
    import numpy as np
    import sounddevice as sd
except Exception:
    np = None
    sd = None

import requests
from dotenv import load_dotenv

load_dotenv()  # load independently of import order in the caller

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")
ELEVENLABS_SAMPLE_RATE = 24000  # matches output_format=pcm_24000 below

VOLUME_GAIN = 1.6  # ElevenLabs PCM output came through quiet — boost it

_speak_lock = threading.Lock()


def _pick_voice_id(engine):
    try:
        for v in engine.getProperty("voices"):
            if "zira" in v.name.lower() or "female" in v.name.lower():
                return v.id
    except Exception:
        pass
    return None


def _speak_offline(text: str):
    if pyttsx3 is None:
        return
    engine = pyttsx3.init()
    voice_id = _pick_voice_id(engine)
    if voice_id:
        engine.setProperty("voice", voice_id)
    engine.setProperty("rate", 150)   # slower, more natural conversational pace
    engine.setProperty("volume", 1.0)  # max — SAPI default is already 1.0 but be explicit
    engine.say(text)
    engine.runAndWait()
    engine.stop()


def _speak_elevenlabs(text: str) -> bool:
    """Returns True on success, False on any failure (caller falls back)."""
    if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID or sd is None:
        return False
    try:
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
            params={"output_format": f"pcm_{ELEVENLABS_SAMPLE_RATE}"},
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "text": text,
                "model_id": ELEVENLABS_MODEL_ID,
                "voice_settings": {
                    "stability": 0.42,        # a bit more expressive/less flat
                    "similarity_boost": 0.8,
                    "style": 0.35,            # warmer, more "sweet" delivery
                    "use_speaker_boost": True,
                },
            },
            timeout=30,
        )
        if resp.status_code != 200 or not resp.content:
            return False
        audio = np.frombuffer(resp.content, dtype=np.int16).astype(np.float32)
        audio = np.clip(audio * VOLUME_GAIN, -32768, 32767).astype(np.int16)
        sd.play(audio, ELEVENLABS_SAMPLE_RATE)
        sd.wait()
        return True
    except Exception:
        return False


def speak(text: str):
    """Speak text out loud. Safe to call from a background thread. Tries
    ElevenLabs first, falls back to the offline SAPI voice on any failure."""
    if not text:
        return
    with _speak_lock:
        try:
            if _speak_elevenlabs(text):
                return
        except Exception:
            pass
        try:
            _speak_offline(text)
        except Exception:
            pass




WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

_whisper_model = None
_whisper_load_lock = threading.Lock()


def _get_whisper_model():
    """Lazy-loaded, loaded once and reused — loading takes a few seconds,
    transcribing after that is fast. First call after launch pays this cost."""
    global _whisper_model
    if _whisper_model is None and _openai_whisper is not None:
        with _whisper_load_lock:
            if _whisper_model is None:
                _whisper_model = _openai_whisper.load_model(WHISPER_MODEL_SIZE)
    return _whisper_model


def _capture_audio(timeout: float, phrase_time_limit: float):
    """Mic capture with voice-activity detection — returns a
    speech_recognition AudioData object, or None on failure/silence."""
    if sr is None:
        return None
    try:
        r = sr.Recognizer()
        # 0.5s was cutting people off mid-sentence on any normal thinking
        # pause — 1.0s gives a real pause room to breathe before ending the
        # phrase, without waiting so long it feels unresponsive.
        r.pause_threshold = 1.0
        r.non_speaking_duration = 0.5
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)  # shorter calibration — less dead air every cycle
            return r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception:
        return None  # no mic / nothing captured


def _whisper_transcribe(audio, task: str) -> str:
    """task: "transcribe" (original language) or "translate" (-> English)."""
    model = _get_whisper_model()
    if model is None or audio is None:
        return ""
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio.get_wav_data())
            wav_path = f.name
        result = model.transcribe(wav_path, task=task, fp16=False)
        return (result.get("text") or "").strip()
    except Exception:
        return ""
    finally:
        if wav_path:
            try:
                os.remove(wav_path)
            except Exception:
                pass


def listen(timeout: float = 4.0, phrase_time_limit: float = 12.0) -> str:
    """Capture from the default mic and transcribe, in whatever language was
    spoken. Returns "" on failure (no mic, silence, unrecognized speech)."""
    return _whisper_transcribe(_capture_audio(timeout, phrase_time_limit), task="transcribe")


def listen_and_translate(timeout: float = 4.0, phrase_time_limit: float = 12.0) -> str:
    """Capture + transcribe + translate to English, all in one Whisper pass
    — whatever language Rudra spoke in, this is what gets sent to the AI
    backend. No separate network call needed (unlike the old Google
    Translate step) since Whisper's translate mode does both at once."""
    return _whisper_transcribe(_capture_audio(timeout, phrase_time_limit), task="translate")
