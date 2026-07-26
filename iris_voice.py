"""ElevenLabs TTS (with offline fallback) + mic STT + auto-translate for the Iris GUI.

Speaking: ElevenLabs "Jessica" (Playful, Bright, Warm) — a premade voice that
works on the free API plan, unlike the old Voice-Library pick which 402'd.
Streamed back as raw PCM and played via sounddevice (no temp files, no mp3
decoder), with a volume boost applied since the raw output was too quiet.
Falls back automatically to pyttsx3 (Windows SAPI, fully offline) whenever
ElevenLabs is unavailable — no key, no credit, no internet, rate-limited.
Either way, Iris always has *some* voice.

Listening: SpeechRecognition's microphone capture + the free Google Web
Speech recognizer (no API key required, just needs internet for the
recognition call itself — the mic capture and everything else stays local).
Whatever language Rudra actually spoke in gets auto-translated to English
before it's handed to the AI (see listen_and_translate / translate_to_english).
"""
import os
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


def translate_to_english(text: str) -> str:
    """Translate arbitrary-language text to English via Google's free
    (no-key) translate endpoint. Returns the original text unchanged if
    translation fails or it's already English."""
    if not text:
        return text
    try:
        resp = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": text},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        translated = "".join(seg[0] for seg in data[0] if seg[0])
        return translated.strip() or text
    except Exception:
        return text


def listen(timeout: float = 4.0, phrase_time_limit: float = 12.0) -> str:
    """Capture from the default mic and transcribe, in whatever language was
    spoken. Returns "" on failure (no mic, silence, unrecognized speech, no
    internet for recognition)."""
    if sr is None:
        return ""
    try:
        r = sr.Recognizer()
        r.pause_threshold = 0.5     # stop waiting 0.5s after speech ends (default 0.8) — starts processing sooner
        r.non_speaking_duration = 0.3
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)  # shorter calibration — less dead air every cycle
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except Exception:
        return ""  # no mic / nothing captured

    try:
        return r.recognize_google(audio, language="hi-IN")
    except sr.UnknownValueError:
        pass  # genuinely not recognized as Hindi speech — worth trying English
    except sr.RequestError:
        return ""  # network/quota hiccup — retrying in English would just mangle the Hindi

    try:
        return r.recognize_google(audio)
    except Exception:
        return ""


def listen_and_translate(timeout: float = 4.0, phrase_time_limit: float = 12.0) -> str:
    """listen() + auto-translate to English — whatever language Rudra spoke
    in, this is what gets sent to the AI backend."""
    heard = listen(timeout=timeout, phrase_time_limit=phrase_time_limit)
    return translate_to_english(heard)
