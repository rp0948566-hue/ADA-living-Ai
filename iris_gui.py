# iris_gui.py
# I.R.I.S HUD — rebuilding step by step.
# Step 1: blank canvas, background #171717.
# Step 2: particle-sphere orb (dotted wavy energy ball) anchored bottom-right.
#         - idle       : purple core / orange rim, slow organic waves
#         - user speaks: deep blue / bright cyan, ripples follow mic loudness
#         - AI speaks  : violet / white-gold, fast rhythmic pulsing
#           (AI mode triggers when iris_data/ai_speaking.flag is touched;
#            agent.py's TTS hook can touch that file while speaking.)

import json
import math
import os
import sys
import time
import uuid

import numpy as np
import requests

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QThread, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QTextCursor, QImage, QPixmap, QPainterPath, QLinearGradient
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton,
    QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QTextEdit,
    QFrame, QComboBox, QCheckBox,
)

import iris_model_config
import iris_voice
import iris_vision
import iris_task_queue
import iris_screen_activity
import iris_mcp_connectors

try:
    import sounddevice as sd
except Exception:
    sd = None

from dotenv import load_dotenv
load_dotenv()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_FLAG = os.path.join(PROJECT_DIR, "iris_data", "ai_speaking.flag")

# Hermes brain — same local API server agent.py talks to.
HERMES_API_BASE_URL = os.getenv("HERMES_API_BASE_URL", "http://127.0.0.1:8642/v1")
HERMES_API_KEY = os.getenv("API_SERVER_KEY", "")
HERMES_SESSION_KEY = os.getenv("HERMES_SESSION_KEY", "vikash-jarvis-desktop")


def touch_ai_flag():
    try:
        os.makedirs(os.path.dirname(AI_FLAG), exist_ok=True)
        with open(AI_FLAG, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def notify_task_complete(window):
    """A background/scheduled task finished with nobody necessarily watching
    — beep + flash the taskbar entry so it actually gets noticed, on top of
    the normal chat bubble + spoken reply."""
    try:
        import winsound
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass
    try:
        if window is not None:
            QApplication.alert(window, 4000)
    except Exception:
        pass


HISTORY_PATH = os.path.join(PROJECT_DIR, "iris_data", "gui_chat_history.json")


class ChatHistoryStore:
    """Local GUI-side chat history (separate from Hermes's own long-term
    memory) — lets the sidebar list and reopen previous conversations."""

    def __init__(self, path=HISTORY_PATH):
        self.path = path
        self.chats = self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.chats, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def new_chat(self):
        chat = {"id": str(uuid.uuid4()), "title": "New chat", "messages": []}
        self.chats.insert(0, chat)
        self._save()
        return chat

    def append(self, chat, role, text):
        chat["messages"].append({"role": role, "text": text})
        if role == "user" and chat["title"] == "New chat":
            chat["title"] = text[:42] + ("…" if len(text) > 42 else "")
        # keep this chat newest-first
        if chat in self.chats:
            self.chats.remove(chat)
        self.chats.insert(0, chat)
        self._save()

    def get(self, chat_id):
        for c in self.chats:
            if c["id"] == chat_id:
                return c
        return None

    def delete(self, chat_id):
        chat = self.get(chat_id)
        if chat is not None:
            self.chats.remove(chat)
            self._save()
        return chat is not None


class HermesWorker(QThread):
    """Sends one message to Hermes's local API server and reports back the
    reply on the Qt thread via a signal (chat completions call is blocking,
    so it must not run on the UI thread)."""

    reply_ready = Signal(str)
    failed = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self):
        try:
            resp = requests.post(
                f"{HERMES_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {HERMES_API_KEY}",
                    "X-Hermes-Session-Key": HERMES_SESSION_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "model": "hermes-agent",
                    "messages": [{"role": "user", "content": self.text}],
                },
                # Local small models (e.g. qwen3.5:4b via Ollama) can take a
                # long time per turn, especially with several tool calls
                # chained together — 90s was cutting those off mid-run.
                timeout=300,
            )
            data = resp.json()
            msg = data["choices"][0]["message"]["content"]
            self.reply_ready.emit(msg)
        except Exception as e:
            self.failed.emit(str(e))

class SpeakWorker(QThread):
    """Speaks a reply out loud (offline, pyttsx3) without blocking the UI."""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self):
        iris_voice.speak(self.text)


class ListenWorker(QThread):
    """Captures one utterance from the mic and transcribes it, off the UI thread."""

    heard = Signal(str)

    def run(self):
        text = iris_voice.listen_and_translate()
        self.heard.emit(text)


class WakeListenerThread(QThread):
    """Always-on background listener — no button, no wake word needed.
    Keeps capturing short utterances and reports anything heard back to the
    UI thread, which forwards it to Iris; she decides for herself whether
    it's directed at her and worth acting on."""

    heard = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False
        self._paused = False

    def stop(self):
        self._stop = True

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def run(self):
        while not self._stop:
            if self._paused:
                time.sleep(0.2)
                continue
            # short timeout: when nobody's talking, give up fast and loop
            # right back around instead of sitting there waiting.
            # phrase_time_limit was 8s, cutting off longer sentences mid-word
            text = iris_voice.listen_and_translate(timeout=1.5, phrase_time_limit=20)
            if self._stop:
                return
            if text and not self._paused:
                self.heard.emit(text)  # dispatched immediately, no artificial delay


class AutoStartWorker(QThread):
    """Runs iris_model_config.auto_start_if_needed() off the UI thread on
    launch: auto-detects whether any AI mode is already running and, if
    not, turns the last-configured one on — plus makes sure the AI Command
    Terminal exists."""

    done = Signal(str)

    def run(self):
        try:
            msg = iris_model_config.auto_start_if_needed()
        except Exception as e:
            msg = f"auto-start failed: {e}"
        self.done.emit(msg)


class ColibriReadyWatcher(QThread):
    """Polls for the colibri (GLM-5.2) model download finishing and, the
    moment it does, switches Hermes to it automatically — no restart, no
    manual dropdown click needed. Only fires once (the transition from
    not-present to present), and only while nothing else has already been
    switched to colibri."""

    became_ready = Signal(str)  # carries the switch_to_colibri_mode() result

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        was_present = iris_model_config.colibri_model_status()["present"]
        while not self._stop:
            for _ in range(60):  # ~60s poll, but stop promptly on shutdown
                if self._stop:
                    return
                time.sleep(1)
            now_present = iris_model_config.colibri_model_status()["present"]
            if now_present and not was_present:
                try:
                    msg = iris_model_config.switch_to_colibri_mode()
                except Exception as e:
                    msg = f"⚠ Auto-switch to colibri failed: {e}"
                self.became_ready.emit(msg)
                return  # job done — one-shot
            was_present = now_present


class TaskSchedulerThread(QThread):
    """Polls iris_task_queue for background/scheduled tasks that have come
    due (queued via the queue_task MCP tool — e.g. "research this while I'm
    away" or "do this at 5:30") and hands each one to the UI thread to run
    through the normal Hermes chat pipeline."""

    task_due = Signal(str, str)  # task_id, description

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        while not self._stop:
            try:
                for t in iris_task_queue.due_tasks():
                    if iris_task_queue.mark_running(t["id"]):
                        self.task_due.emit(t["id"], t["description"])
            except Exception:
                pass
            for _ in range(20):  # ~20s poll, but stop promptly on shutdown
                if self._stop:
                    return
                time.sleep(1)


# (core color, rim color) per mode
PALETTES = {
    "idle": ((95, 60, 200), (255, 128, 40)),     # purple -> orange (reference image)
    "user": ((25, 80, 210), (120, 235, 255)),    # deep blue -> cyan
    "ai":   ((170, 60, 255), (255, 235, 170)),   # violet -> white-gold
}
SPEED = {"idle": 1.0, "user": 1.9, "ai": 2.7}


class ParticleOrb(QWidget):
    """Dotted particle sphere with flowing wave displacement, like a living
    ball of energy. Rows of dots (lat/long grid) so the surface reads as
    flowing dotted lines, matching the reference image."""

    activate_requested = Signal()  # 2+ claps in quick succession -> "start listening"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # --- lat/long dot grid on a unit sphere (rows of dots) ---
        pts, seeds = [], []
        rng = np.random.default_rng(7)
        n_lat = 38
        for i in range(1, n_lat):
            theta = math.pi * i / n_lat                # polar angle
            n_lon = max(6, int(68 * math.sin(theta)))  # dots on this ring
            for j in range(n_lon):
                phi = 2 * math.pi * j / n_lon
                pts.append((theta, phi))
                seeds.append(rng.uniform(0, 2 * math.pi))
        ang = np.array(pts)
        self.theta = ang[:, 0]
        self.phi = ang[:, 1]
        self.seed = np.array(seeds)
        st = np.sin(self.theta)
        self.base = np.stack(
            [st * np.cos(self.phi), np.cos(self.theta), st * np.sin(self.phi)],
            axis=1,
        )

        # --- animation state ---
        self.t0 = time.time()
        self.anim_t = 0.0          # advances at mode-dependent speed
        self.last_tick = self.t0
        self.energy = 0.18
        self.burst = 0.0
        self.mode = "idle"
        core, rim = PALETTES["idle"]
        self.cur_core = np.array(core, dtype=float)
        self.cur_rim = np.array(rim, dtype=float)

        # --- microphone level + clap/transient detection (best effort) ---
        self._mic = 0.0
        self._rms_slow = 0.01   # slow-moving baseline of ambient loudness
        self._clap_time = 0.0   # when the last clap/snap was detected
        self._clap_times = []   # rolling window for 2+ claps = "activate" gesture
        self.vision_settings = None  # shared dict from VisionEngine — privacy toggle for clap wake
        self._stream = None
        if sd is not None:
            try:
                def _cb(indata, frames, t, status):
                    rms = float(np.sqrt(np.mean(indata ** 2)))
                    self._mic = max(rms, self._mic * 0.82)
                    # sharp transient well above ambient baseline = clap/snap
                    if rms > max(0.10, self._rms_slow * 5.0):
                        now = time.time()
                        self._clap_time = now
                        self._clap_times = [t2 for t2 in self._clap_times if now - t2 < 1.5] + [now]
                        if len(self._clap_times) >= 2:
                            self._clap_times = []
                            if self.vision_settings is None or self.vision_settings.get("clap_detection", True):
                                self.activate_requested.emit()
                    self._rms_slow = 0.95 * self._rms_slow + 0.05 * rms
                self._stream = sd.InputStream(
                    samplerate=16000, channels=1, blocksize=1024, callback=_cb
                )
                self._stream.start()
            except Exception:
                self._stream = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)  # ~30 fps

    # ------------------------------------------------------------------
    def _detect_mode(self):
        # AI speaking wins if the flag file was touched in the last 1.5 s
        try:
            if time.time() - os.path.getmtime(AI_FLAG) < 1.5:
                return "ai", 0.0
        except OSError:
            pass
        level = min(1.0, self._mic / 0.06)  # normalize speech loudness
        if level > 0.22:
            return "user", level
        return "idle", level

    def _tick(self):
        now = time.time()
        dt = min(0.1, now - self.last_tick)
        self.last_tick = now

        mode, level = self._detect_mode()
        self.mode = mode

        # energy target per mode
        if mode == "user":
            target = 0.30 + 0.70 * level
        elif mode == "ai":
            t = now - self.t0
            target = 0.45 + 0.45 * abs(math.sin(t * 3.1) * math.sin(t * 1.7))
        else:
            target = 0.18

        # clap burst: instant reaction, decays over ~0.7 s
        burst = max(0.0, 1.0 - (now - self._clap_time) / 0.7)
        self.burst = burst
        target = min(1.4, target + burst * 1.0)

        self.energy += (target - self.energy) * (0.5 if burst > 0.5 else 0.15)

        # smooth palette shift toward the mode palette
        core, rim = PALETTES[mode]
        self.cur_core += (np.array(core, dtype=float) - self.cur_core) * 0.10
        self.cur_rim += (np.array(rim, dtype=float) - self.cur_rim) * 0.10

        # animation clock runs faster in energetic modes
        self.anim_t += dt * SPEED[mode]
        self.update()

    # ------------------------------------------------------------------
    def paintEvent(self, event):
        w, h = self.width(), self.height()
        if w < 10 or h < 10:
            return
        t = self.anim_t
        e = self.energy

        # layered travelling waves -> organic wavy displacement
        disp = (
            0.50 * np.sin(3.0 * self.phi + 2.0 * self.theta + t * 0.9 + self.seed)
            + 0.30 * np.sin(5.0 * self.theta - t * 0.7 + self.seed * 0.5)
            + 0.20 * np.sin(7.0 * self.phi + t * 1.3)
        )
        radius = 1.0 + (0.06 + 0.30 * e) * disp

        pos = self.base * radius[:, None]

        # slow spin around Y with a gentle X wobble
        ay = t * 0.25
        ax = 0.35 + 0.10 * math.sin(t * 0.30)
        cy_, sy_ = math.cos(ay), math.sin(ay)
        cx_, sx_ = math.cos(ax), math.sin(ax)
        x = pos[:, 0] * cy_ + pos[:, 2] * sy_
        z1 = -pos[:, 0] * sy_ + pos[:, 2] * cy_
        y = pos[:, 1] * cx_ - z1 * sx_
        z = pos[:, 1] * sx_ + z1 * cx_

        # orthographic projection into the widget
        cx, cy = w / 2.0, h / 2.0
        scale = min(w, h) * 0.335
        sxp = cx + x * scale
        syp = cy + y * scale

        # color mixing: displacement crest -> rim color, depth -> brightness
        mix = np.clip((disp + 1.0) / 2.0, 0.0, 1.0)
        bright = 0.30 + 0.70 * (z + 1.4) / 2.4

        # clap flash: momentarily blaze the whole palette toward white
        flash = getattr(self, "burst", 0.0)
        if flash > 0.0:
            bright = np.minimum(1.0, bright + 0.55 * flash)

        # quantized palette LUT (16 mix x 6 brightness) to avoid 2k QColors
        mix_q = np.minimum((mix * 15).astype(int), 15)
        bri_q = np.minimum((bright * 5).astype(int), 5)
        lut = {}
        for mq in range(16):
            f = mq / 15.0
            r0, g0, b0 = self.cur_core + (self.cur_rim - self.cur_core) * f
            for bq in range(6):
                bf = 0.35 + 0.65 * bq / 5.0
                lut[(mq, bq)] = QColor(
                    int(min(255, r0 * bf)),
                    int(min(255, g0 * bf)),
                    int(min(255, b0 * bf)),
                    int(120 + 135 * bq / 5.0),
                )

        order = np.argsort(z)  # painter's algorithm: back to front
        dot = max(1.2, min(w, h) / 190.0)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        for i in order:
            p.setBrush(lut[(int(mix_q[i]), int(bri_q[i]))])
            s = dot * (0.6 + 0.5 * bright[i])
            p.drawEllipse(QPointF(sxp[i], syp[i]), s, s)

        # clap shockwave: expanding ring that fades as it grows
        if flash > 0.0:
            ring_r = scale * (1.05 + 1.1 * (1.0 - flash))
            pen = QPen(QColor(255, 255, 255, int(180 * flash)), 2.0 + 2.0 * flash)
            p.setPen(pen)
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(QPointF(cx, cy), ring_r, ring_r)

    def closeEvent(self, event):
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
        event.accept()


class ScreenAuraOverlay(QWidget):
    """A soft, animated glow around every edge of the screen — shows
    whenever Iris is actually controlling the mouse/keyboard/browser (running
    commands, opening apps, browsing, building a website) so it's obvious
    at a glance that she's "in control" right now, the way a recording-light
    or an aurora in the night sky reads as alive and unmistakable. Fades
    out the moment she's done, and never shows at all for anything
    explicitly run in the background (see iris_screen_activity.py)."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.Tool | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        virt = QRectF()
        for s in QApplication.screens():
            virt = virt.united(QRectF(s.geometry()))
        self.setGeometry(virt.toRect())

        self._t = 0.0
        self._opacity = 0.0
        self._thickness = 70

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)  # ~30fps
        self.hide()

    def _tick(self):
        active = (
            os.path.exists(iris_screen_activity.ACTIVE_FLAG)
            and (time.time() - os.path.getmtime(iris_screen_activity.ACTIVE_FLAG) < 2.0)
        )
        self._t += 0.02
        target = 1.0 if active else 0.0
        prev = self._opacity
        self._opacity += (target - self._opacity) * 0.12
        if self._opacity > 0.01:
            if not self.isVisible():
                self.show()
            self.update()
        elif prev > 0.01:
            self.update()  # one last paint at ~0 to clear the frame
            self.hide()

    def paintEvent(self, event):
        if self._opacity <= 0.01:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = self.width(), self.height()
        th = self._thickness
        hue = (self._t * 18) % 360
        a = int(150 * self._opacity)

        def c(offset):
            col = QColor.fromHsv(int((hue + offset) % 360), 210, 255)
            col.setAlpha(a)
            return col

        clear = QColor(0, 0, 0, 0)

        top = QLinearGradient(0, 0, 0, th)
        top.setColorAt(0.0, c(0))
        top.setColorAt(1.0, clear)
        p.fillRect(QRectF(0, 0, w, th), top)

        bottom = QLinearGradient(0, h, 0, h - th)
        bottom.setColorAt(0.0, c(180))
        bottom.setColorAt(1.0, clear)
        p.fillRect(QRectF(0, h - th, w, th), bottom)

        left = QLinearGradient(0, 0, th, 0)
        left.setColorAt(0.0, c(90))
        left.setColorAt(1.0, clear)
        p.fillRect(QRectF(0, 0, th, h), left)

        right = QLinearGradient(w, 0, w - th, 0)
        right.setColorAt(0.0, c(270))
        right.setColorAt(1.0, clear)
        p.fillRect(QRectF(w - th, 0, th, h), right)

    def stop(self):
        self._timer.stop()


class ChatBar(QWidget):
    """Conversation transcript + a live status line — voice-only now, no
    typing bar. Talks to Hermes directly over HTTP. Persists every exchange
    to ChatHistoryStore for the sidebar."""

    chat_updated = Signal()  # tell the sidebar to refresh its list

    def __init__(self, history: ChatHistoryStore, orb: "ParticleOrb" = None, parent=None):
        super().__init__(parent)
        self.history = history
        self.orb = orb  # read its live mic level for the "hearing you" indicator
        self.chat = None  # active chat dict from the history store
        self._worker = None
        self._listen_worker = None
        self._speak_worker = None
        self._pending = None  # (display_text, payload_text, task_id) queued while a reply is in flight
        self._active_task_id = None  # set while running a queued background/scheduled task
        self._busy = False  # true whenever a reply is in flight — status line shows that, not mic level
        self._status_override = None  # (text, expires_at) — a transient message that beats the live mic status

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setFrameShape(QFrame.NoFrame)
        self.transcript.setStyleSheet(
            "QTextEdit { background:transparent; color:#CFCFCF; font-size:13px; }"
        )
        self.transcript.setMaximumHeight(160)
        outer.addWidget(self.transcript)

        # Live status line — replaces the old typing bar entirely. Always
        # shows exactly what's happening right now: listening, hearing you
        # speak, thinking, or why something got ignored.
        self.status_label = QLabel("👂 Listening... just talk, or clap twice")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(48)
        self.status_label.setStyleSheet(
            "QLabel { background:#1a1a1e; border:1px solid #2c2c32; border-radius:14px;"
            " color:#9a9aa2; font-size:13px; }"
        )
        outer.addWidget(self.status_label)

        # always-on listening — no button, no wake word, just talk or clap twice.
        self._wake_thread = WakeListenerThread(self)
        self._wake_thread.heard.connect(self._on_wake_heard)
        self._wake_thread.start()

        # background/scheduled tasks queued via the queue_task MCP tool
        # ("research this while I'm out", "do this at 5:30") — polled and
        # fired independently of anything being said out loud.
        self._task_scheduler = TaskSchedulerThread(self)
        self._task_scheduler.task_due.connect(self._on_task_due)
        self._task_scheduler.start()

        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._update_status_label)
        self._status_timer.start(150)

    _MIC_SPEAKING_THRESHOLD = 0.015

    def _flash_status(self, text: str, seconds: float = 2.5):
        """Show a message that overrides the live mic/thinking status for a
        short while — used so a filtered/ignored utterance is visible for a
        moment instead of looking like nothing happened at all."""
        self._status_override = (text, time.time() + seconds)
        self.status_label.setText(text)

    def _update_status_label(self):
        if self._status_override is not None:
            text, expires_at = self._status_override
            if time.time() < expires_at:
                return  # still showing the override
            self._status_override = None
        if self._busy:
            return  # _dispatch/_on_reply/_on_failed own the label while busy
        mic_level = getattr(self.orb, "_mic", 0.0) if self.orb is not None else 0.0
        if mic_level > self._MIC_SPEAKING_THRESHOLD:
            self.status_label.setText("🎤 Hearing you...")
        else:
            self.status_label.setText("👂 Listening... just talk, or clap twice")

    def start_new_chat(self):
        self.chat = self.history.new_chat()
        self.transcript.clear()
        self.chat_updated.emit()

    def load_chat(self, chat_id: str):
        chat = self.history.get(chat_id)
        if not chat:
            return
        self.chat = chat
        self.transcript.clear()
        for m in chat["messages"]:
            self._append_line(m["role"], m["text"])

    def _append_line(self, role: str, text: str):
        who = "You" if role == "user" else "Iris"
        color = "#8FD3FF" if role == "user" else "#D9B8FF"
        self.transcript.append(f'<b style="color:{color}">{who}:</b> {text}')

    def _send_ambient(self, heard_text: str):
        """Continuously-overheard speech — no wake word required. Iris
        decides for herself whether it's directed at her and whether she
        can help; if not, she says nothing (see SOUL.md's NO_RESPONSE rule).

        Before that decision even reaches the (often small/local) LLM, cheap
        stuff gets filtered out here: one-off short mutters or filler words
        picked up from ambient room noise never get dispatched at all, unless
        her name is actually said. This is what keeps her from replying to
        every little thing said in the room — the model-level NO_RESPONSE
        check is a second line of defense, not the only one."""
        if not heard_text:
            return
        if not self._looks_directed(heard_text):
            # Not silent-silent: flash why, so "heard but nothing happened"
            # doesn't look like a hang — this is the difference between
            # "ignored as noise" and "dispatched but Iris never replied".
            self._flash_status(f'🤫 Heard "{heard_text}" — too short, ignored')
            return
        payload = (
            "[This was picked up from continuous background listening — it "
            "may or may not be directed at you, and may just be ambient talk. "
            "Decide: is this actually meant for you, and can you help? If yes, "
            "go ahead and do it, then tell me what you did. If it's not "
            "directed at you or you can't help, reply with exactly the single "
            "word NO_RESPONSE and nothing else.] " + heard_text
        )
        self._dispatch(heard_text, payload)

    def _on_task_due(self, task_id: str, description: str):
        """A background/scheduled task (see queue_task MCP tool) has come
        due. Run it through the normal Hermes pipeline like any message, but
        remember its task_id so completion can be reported back into the
        queue file and flagged more insistently (this happens with nobody
        necessarily watching, so a quiet chat bubble isn't enough)."""
        payload = (
            "[This is a background/scheduled task you queued earlier via "
            "queue_task — it is not something Vikash sir just said, act on "
            "it now using whatever tools you need, then summarize what you "
            "did. Do NOT call queue_task again for this same task — it is "
            "already running right now, queueing it again would just loop "
            "forever. Only use queue_task here if this task's own result "
            "requires a genuinely separate new future action.] " + description
        )
        # Explicitly backgrounded — suppress the on-screen "Iris is active"
        # glow for the duration of this turn (see iris_screen_activity.py).
        try:
            with open(iris_screen_activity.BACKGROUND_FLAG, "w") as f:
                f.write(str(time.time()))
        except Exception:
            pass
        self._dispatch(f"[Background task] {description}", payload, task_id=task_id)

    _AMBIENT_MIN_WORDS = 4  # short mutters below this get dropped unless her name is in them

    def _looks_directed(self, text: str) -> bool:
        """Quick local pass to weed out ambient noise before it ever reaches
        the AI. Anything that says her name is always forwarded, no matter
        how short. Everything else needs to be a real sentence, not a
        one-or-two-word fragment (a cough transcribed as "the", a distant
        "okay", a TV/other-person snippet) — those are the bulk of the false
        triggers when there's no wake word."""
        t = text.strip().lower()
        if not t:
            return False
        if "iris" in t:
            return True
        return len(t.split()) >= self._AMBIENT_MIN_WORDS

    def _dispatch(self, display_text: str, payload_text: str, task_id: str = None):
        if self._worker is not None:
            # Iris is still replying to the last thing — never drop what was
            # just said, queue it and it fires the moment she's free.
            self._pending = (display_text, payload_text, task_id)
            self._flash_status("Iris is still replying — sending this right after...", seconds=5)
            return
        if self.chat is None:
            self.start_new_chat()

        self._busy = True
        self.status_label.setText("🤔 Iris is thinking...")
        self._append_line("user", display_text)
        self.history.append(self.chat, "user", display_text)
        self.chat_updated.emit()
        self._thinking_line = "Iris is thinking..."
        self.transcript.append(f'<i style="color:#888">{self._thinking_line}</i>')

        self._active_task_id = task_id
        self._worker = HermesWorker(payload_text, self)
        self._worker.reply_ready.connect(self._on_reply)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._cleanup)
        self._worker.start()

    def _remove_thinking_line(self):
        cursor = self.transcript.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()

    def _replace_thinking(self, html: str):
        # drop the trailing "thinking..." placeholder line, then append reply
        self._remove_thinking_line()
        self.transcript.append(html)

    def _clear_background_flag(self):
        try:
            if os.path.exists(iris_screen_activity.BACKGROUND_FLAG):
                os.remove(iris_screen_activity.BACKGROUND_FLAG)
        except Exception:
            pass

    def _on_reply(self, msg: str):
        if msg.strip().upper() == "NO_RESPONSE":
            # not directed at her / nothing she can help with — stay quiet
            self._remove_thinking_line()
            self._flash_status("🤫 Not directed at Iris — stayed quiet", seconds=2)
            if self._active_task_id:
                iris_task_queue.mark_done(self._active_task_id, "(NO_RESPONSE)", ok=True)
                self._clear_background_flag()
            return
        self._replace_thinking(f'<b style="color:#D9B8FF">Iris:</b> {msg}')
        self.history.append(self.chat, "assistant", msg)
        self.chat_updated.emit()
        touch_ai_flag()  # let the orb react like Iris is "speaking"
        self._speak_worker = SpeakWorker(msg, self)
        self._speak_worker.start()
        self._flash_status("💬 Iris replied", seconds=1.5)
        if self._active_task_id:
            iris_task_queue.mark_done(self._active_task_id, msg, ok=True)
            self._clear_background_flag()
            notify_task_complete(self.window())

    def _on_failed(self, err: str):
        self._replace_thinking(f'<span style="color:#FF8080">⚠ Could not reach Iris: {err}</span>')
        self._flash_status(f"⚠ Could not reach Iris: {err}", seconds=4)
        if self._active_task_id:
            iris_task_queue.mark_done(self._active_task_id, err, ok=False)
            self._clear_background_flag()
            notify_task_complete(self.window())

    def _cleanup(self):
        self._busy = False
        self._worker = None
        self._active_task_id = None
        self._wake_thread.resume()  # only resume ambient listening once this full turn is done
        if self._pending is not None:
            display_text, payload_text, task_id = self._pending
            self._pending = None
            self._dispatch(display_text, payload_text, task_id=task_id)

    def _on_wake_heard(self, text: str):
        """Fired continuously by WakeListenerThread with anything picked up.
        No wake word required anymore — everything heard goes to Iris, and
        she herself decides whether it's directed at her / worth acting on."""
        self._send_ambient(text)

    def trigger_listen(self):
        """One-shot capture, used for the clap-twice gesture and for a bare
        wake-word with no command attached."""
        if self._listen_worker is not None:
            return
        self._wake_thread.pause()  # don't fight the one-shot capture for the mic
        self._flash_status("🎤 Listening...", seconds=15)
        self._listen_worker = ListenWorker(self)
        self._listen_worker.heard.connect(self._on_capture_heard)
        self._listen_worker.finished.connect(self._listen_cleanup)
        self._listen_worker.start()

    def _on_capture_heard(self, text: str):
        if text:
            self._dispatch(text, text)  # _cleanup (fired once the reply finishes) resumes ambient listening
        else:
            self._flash_status("Didn't catch that — try again or clap twice", seconds=3)
            self._wake_thread.resume()  # nothing dispatched — safe to resume right away

    def _listen_cleanup(self):
        self._listen_worker = None


class Sidebar(QFrame):
    """Left panel — new-chat button + list of previous conversations."""

    new_chat_clicked = Signal()
    chat_selected = Signal(str)
    chat_delete_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(240)
        self.setStyleSheet(
            "background:#131315; border-right:1px solid #232327;"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 18, 14, 14)
        lay.setSpacing(12)

        title = QLabel("I.R.I.S")
        title.setStyleSheet("color:#E8E8EC; font-size:16px; font-weight:700; letter-spacing:1px;")
        lay.addWidget(title)

        self.mcp_toggle_btn = QPushButton("🔌  MCP")
        self.mcp_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.mcp_toggle_btn.setStyleSheet(
            "QPushButton { background:#1f1f24; color:#C9C9CF; border:1px solid #2c2c32;"
            " border-radius:8px; padding:6px; text-align:left; font-size:12px; }"
            "QPushButton:hover { background:#27272d; }"
        )
        self.mcp_toggle_btn.clicked.connect(self._toggle_mcp_panel)
        lay.addWidget(self.mcp_toggle_btn)

        # --- Chats section (default view) ---
        self.chats_section = QWidget()
        chats_lay = QVBoxLayout(self.chats_section)
        chats_lay.setContentsMargins(0, 0, 0, 0)
        chats_lay.setSpacing(12)

        model_label = QLabel("BRAIN MODEL")
        model_label.setStyleSheet("color:#6b6b72; font-size:10px; font-weight:600; letter-spacing:1px;")
        chats_lay.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(
            "QComboBox { background:#1f1f24; color:#E8E8EC; border:1px solid #2c2c32;"
            " border-radius:8px; padding:6px 8px; font-size:12px; }"
            "QComboBox QAbstractItemView { background:#1f1f24; color:#E8E8EC;"
            " selection-background-color:#3a3a42; }"
        )
        self._populate_models()
        self.model_combo.activated.connect(self._on_model_picked)
        chats_lay.addWidget(self.model_combo)

        self.model_status = QLabel("")
        self.model_status.setWordWrap(True)
        self.model_status.setStyleSheet("color:#7fd48a; font-size:10px;")
        chats_lay.addWidget(self.model_status)

        new_btn = QPushButton("+  New chat")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(
            "QPushButton { background:#1f1f24; color:#E8E8EC; border:1px solid #2c2c32;"
            " border-radius:10px; padding:8px; text-align:left; font-size:13px; }"
            "QPushButton:hover { background:#27272d; }"
        )
        new_btn.clicked.connect(self.new_chat_clicked.emit)
        chats_lay.addWidget(new_btn)
        chats_lay.addStretch(1)

        lay.addWidget(self.chats_section, 1)

        # --- MCP connectors section (hidden until the MCP button is clicked) ---
        self.mcp_section = QWidget()
        self.mcp_section.setVisible(False)
        mcp_lay = QVBoxLayout(self.mcp_section)
        mcp_lay.setContentsMargins(0, 0, 0, 0)
        mcp_lay.setSpacing(10)

        mcp_title = QLabel("MCP CONNECTORS")
        mcp_title.setStyleSheet("color:#6b6b72; font-size:10px; font-weight:600; letter-spacing:1px;")
        mcp_lay.addWidget(mcp_title)

        self._mcp_checkboxes = {}
        for name, label, enabled, ready, note in iris_mcp_connectors.list_connectors():
            row = QWidget()
            row_lay = QVBoxLayout(row)
            row_lay.setContentsMargins(0, 0, 0, 0)
            row_lay.setSpacing(2)

            top_row = QHBoxLayout()
            cb = QCheckBox(label)
            cb.setChecked(enabled)
            cb.setStyleSheet("QCheckBox { color:#E8E8EC; font-size:13px; }")
            cb.stateChanged.connect(lambda state, n=name: self._on_connector_toggled(n, state))
            self._mcp_checkboxes[name] = cb
            top_row.addWidget(cb, 1)
            row_lay.addLayout(top_row)

            note_label = QLabel(note)
            note_label.setWordWrap(True)
            note_label.setStyleSheet("color:#6b6b72; font-size:10px; padding-left:22px;")
            row_lay.addWidget(note_label)

            mcp_lay.addWidget(row)

        self.mcp_status = QLabel("")
        self.mcp_status.setWordWrap(True)
        self.mcp_status.setStyleSheet("color:#7fd48a; font-size:10px;")
        mcp_lay.addWidget(self.mcp_status)
        mcp_lay.addStretch(1)

        lay.addWidget(self.mcp_section, 1)

        # Auto-switch to colibri the moment its (huge) model download
        # finishes — no waiting for a restart or manual dropdown click.
        self._colibri_watcher = ColibriReadyWatcher(self)
        self._colibri_watcher.became_ready.connect(self._on_colibri_ready)
        self._colibri_watcher.start()

    def _on_colibri_ready(self, msg: str):
        self.model_status.setText(f"🐦 Colibri model finished downloading — {msg}")
        self._populate_models()

    def _toggle_mcp_panel(self):
        showing_mcp = not self.mcp_section.isVisible()
        self.mcp_section.setVisible(showing_mcp)
        self.chats_section.setVisible(not showing_mcp)
        self.mcp_toggle_btn.setText("←  Chats" if showing_mcp else "🔌  MCP")

    def _on_connector_toggled(self, name: str, state: int):
        enabled = bool(state)  # 0 = unchecked, non-zero = checked (non-tristate box)
        iris_mcp_connectors.set_enabled(name, enabled)
        self.mcp_status.setText(
            f"✅ {'Enabled' if enabled else 'Disabled'} — restart the gateway "
            "(switch model or relaunch) to apply."
        )

    def _populate_models(self):
        """Auto-detect installed Ollama models + mark whichever Hermes is
        currently pointed at (local or cloud) as the selected entry."""
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        local_models = iris_model_config.list_ollama_models()
        current = iris_model_config.get_current_model()
        current_default = current.get("default")
        current_is_local = current.get("provider") in ("ollama", "custom", "vllm", "llamacpp")

        for m in local_models:
            self.model_combo.addItem(f"🖥 {m} (local)", ("local", m))
        cloud_label = f"☁ {current_default} (cloud)" if not current_is_local and current_default else "☁ cloud (current)"
        self.model_combo.addItem(cloud_label, ("cloud", current_default or ""))

        colibri_ready = iris_model_config.colibri_model_status()["present"]
        colibri_label = "🐦 GLM-5.2 colibri (ready)" if colibri_ready else "🐦 GLM-5.2 colibri (still downloading...)"
        self.model_combo.addItem(colibri_label, ("colibri", "glm-5.2-colibri"))

        # pre-select whatever is actually active right now
        if current.get("base_url") == iris_model_config.COLIBRI_BASE_URL:
            target = ("colibri", "glm-5.2-colibri")
        else:
            target = ("local", current_default) if current_is_local else ("cloud", current_default)
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == target:
                self.model_combo.setCurrentIndex(i)
                break
        self.model_combo.blockSignals(False)

    def _on_model_picked(self, index: int):
        kind, model_name = self.model_combo.itemData(index)
        if kind == "colibri":
            if not iris_model_config.colibri_model_status()["present"]:
                self.model_status.setText(
                    f"⚠ Model not finished downloading yet — {iris_model_config.COLIBRI_MODEL_PATH}"
                )
                return
            self.model_combo.setEnabled(False)
            self.model_status.setText(
                "Switching to colibri (GLM-5.2 744B)... very slow on this hardware, first reply may take minutes."
            )
            try:
                msg = iris_model_config.switch_to_colibri_mode()
                self.model_status.setText(f"✅ {msg}")
            except Exception as e:
                self.model_status.setText(f"⚠ Colibri switch failed: {e}")
            finally:
                self.model_combo.setEnabled(True)
            return
        if kind != "local" or not model_name:
            return  # only local switches are driven from this dropdown
        self.model_combo.setEnabled(False)
        self.model_status.setText(f"Switching to local model '{model_name}'... (old mode turning off)")
        try:
            msg = iris_model_config.switch_local_model(model_name)
            self.model_status.setText(f"✅ {msg}")
        except Exception as e:
            self.model_status.setText(f"⚠ Model switch failed: {e}")
        finally:
            self.model_combo.setEnabled(True)

    def refresh(self, chats):
        pass  # previous-chats list removed from the sidebar


class CameraWidget(QWidget):
    """Small circular camera preview, top-right of the HUD. Shows only hand
    tracking (gesture) — face/body tracking run in the backend but never
    render here, by design. Click to expand into VisionPanel."""

    clicked = Signal()

    SIZE = 76

    def __init__(self, engine: "iris_vision.VisionEngine", parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(Qt.PointingHandCursor)
        self._pixmap = None
        self._t0 = time.time()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(90)  # ~11fps — plenty for a small preview

    def _tick(self):
        jpeg = self.engine.get_last_jpeg() if self.engine.available else None
        if jpeg:
            img = QImage.fromData(jpeg, "JPG")
            if not img.isNull():
                self._pixmap = QPixmap.fromImage(img)
        self.update()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        s = self.SIZE
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        clip = QPainterPath()
        clip.addEllipse(2, 2, s - 4, s - 4)
        p.setClipPath(clip)

        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(s, s, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (scaled.width() - s) // 2
            y = (scaled.height() - s) // 2
            p.drawPixmap(-x, -y, scaled)
        else:
            p.fillRect(0, 0, s, s, QColor(26, 26, 30, 235))
            p.setPen(QColor(120, 120, 128))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(QRectF(0, 0, s, s), Qt.AlignCenter, "cam\noff" if not self.engine.available else "…")

        p.setClipping(False)

        # ring border
        camera_on = self.engine.settings.get("camera_enabled", True) and self.engine.available
        ring_color = QColor(120, 230, 150) if camera_on else QColor(90, 90, 96)
        p.setPen(QPen(ring_color, 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(1, 1, s - 2, s - 2))

        # privacy/status dot, bottom-right — soft pulse while camera is live
        if camera_on:
            pulse = 0.55 + 0.45 * abs(math.sin((time.time() - self._t0) * 2.2))
            dot_color = QColor(255, 90, 90, int(160 + 95 * pulse))
        else:
            dot_color = QColor(110, 110, 116)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(dot_color))
        p.drawEllipse(QPointF(s - 12, s - 12), 6, 6)
        p.setPen(QPen(QColor(23, 23, 23), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(s - 12, s - 12), 6, 6)


class VisionPanel(QFrame):
    """Expanded vision workspace — larger preview, current hand gesture,
    and privacy toggles. Opens when the CameraWidget is clicked."""

    closed = Signal()

    def __init__(self, engine: "iris_vision.VisionEngine", parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setFixedWidth(280)
        self.setStyleSheet(
            "QFrame { background: rgba(24,24,28,235); border: 1px solid rgba(255,255,255,30);"
            " border-radius: 16px; }"
            "QLabel { background: transparent; color: #E8E8EC; }"
            "QCheckBox { background: transparent; color: #C9C9CF; font-size: 12px; }"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Vision")
        title.setStyleSheet("font-size:13px; font-weight:700; letter-spacing:0.5px;")
        header.addWidget(title, 1)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { background:transparent; color:#8a8a90; border:none; }"
            "QPushButton:hover { color:#fff; }"
        )
        close_btn.clicked.connect(self.closed.emit)
        header.addWidget(close_btn)
        lay.addLayout(header)

        self.preview = QLabel()
        self.preview.setFixedSize(252, 189)
        self.preview.setStyleSheet("background:#101012; border-radius:12px;")
        self.preview.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.preview)

        self.gesture_label = QLabel("Hand: none")
        self.gesture_label.setStyleSheet("color:#8FD3FF; font-size:12px; font-weight:600;")
        lay.addWidget(self.gesture_label)

        settings_label = QLabel("PRIVACY")
        settings_label.setStyleSheet("color:#6b6b72; font-size:10px; font-weight:600; letter-spacing:1px;")
        lay.addWidget(settings_label)

        self._checkboxes = {}
        for key, label in [
            ("camera_enabled", "Camera"),
            ("face_recognition", "Face Recognition"),
            ("body_tracking", "Body Tracking"),
            ("hand_tracking", "Hand Tracking"),
            ("gesture_recognition", "Gesture Recognition"),
            ("clap_detection", "Clap Detection (wake)"),
        ]:
            cb = QCheckBox(label)
            cb.setChecked(bool(self.engine.settings.get(key, True)))
            cb.toggled.connect(lambda checked, k=key: self.engine.set_setting(k, checked))
            lay.addWidget(cb)
            self._checkboxes[key] = cb

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(100)

    def _tick(self):
        jpeg = self.engine.get_last_jpeg() if self.engine.available else None
        if jpeg:
            img = QImage.fromData(jpeg, "JPG")
            if not img.isNull():
                pm = QPixmap.fromImage(img).scaled(
                    self.preview.width(), self.preview.height(),
                    Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation,
                )
                self.preview.setPixmap(pm)
        elif not self.engine.settings.get("camera_enabled", True):
            self.preview.setText("Camera off")
            self.preview.setStyleSheet(self.preview.styleSheet() + " color:#8a8a90;")

        hand = self.engine.get_hand_state()
        gesture = hand.get("gesture", "none") if hand.get("present") else "none"
        self.gesture_label.setText(f"Hand: {gesture.replace('_', ' ')}")


class NovaHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("I.R.I.S HUD")
        self.resize(1280, 760)
        self.setStyleSheet("background-color: #171717;")

        self.history = ChatHistoryStore()

        root = QWidget()
        self.setCentralWidget(root)
        root_lay = QHBoxLayout(root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        self.sidebar = Sidebar(root)
        self.sidebar.new_chat_clicked.connect(self._new_chat)
        self.sidebar.chat_selected.connect(self._select_chat)
        self.sidebar.chat_delete_requested.connect(self._delete_chat)
        root_lay.addWidget(self.sidebar)

        self.canvas = QWidget(root)
        root_lay.addWidget(self.canvas, 1)

        self.orb = ParticleOrb(self.canvas)
        self.chatbar = ChatBar(self.history, self.orb, self.canvas)
        self.chatbar.chat_updated.connect(self._refresh_sidebar)
        self.orb.activate_requested.connect(self.chatbar.trigger_listen)  # clap twice -> listen

        # Screen-edge glow — lights up around the whole screen whenever Iris
        # is actively driving the mouse/keyboard/browser, so it's obvious
        # she's "in control" right now instead of it happening invisibly.
        self.aura = ScreenAuraOverlay()

        # Background vision engine — face/body tracking stay backend-only;
        # only hand tracking ever renders in the UI, per design.
        self.vision_engine = iris_vision.VisionEngine(target_fps=8)
        self.orb.vision_settings = self.vision_engine.settings  # shared dict — clap toggle check
        self.vision_engine.start()

        self.camera_widget = CameraWidget(self.vision_engine, self.canvas)
        self.camera_widget.clicked.connect(self._toggle_vision_panel)
        self.vision_panel = None

        self._refresh_sidebar()
        self._place_widgets()

        # auto-detect if any AI mode is already running; if not, turn the
        # last-selected one on automatically — and stand up the AI Command
        # Terminal — without blocking the UI thread.
        self._autostart = AutoStartWorker(self)
        self._autostart.done.connect(lambda msg: print(f"[iris] {msg}"))
        self._autostart.start()

    def _toggle_vision_panel(self):
        if self.vision_panel is not None:
            self.vision_panel.deleteLater()
            self.vision_panel = None
            return
        self.vision_panel = VisionPanel(self.vision_engine, self.canvas)
        self.vision_panel.closed.connect(self._toggle_vision_panel)
        self.vision_panel.show()
        self._place_widgets()
        self.vision_panel.raise_()

    def _new_chat(self):
        self.chatbar.start_new_chat()

    def _select_chat(self, chat_id: str):
        self.chatbar.load_chat(chat_id)

    def _delete_chat(self, chat_id: str):
        was_open = self.chatbar.chat is not None and self.chatbar.chat["id"] == chat_id
        self.history.delete(chat_id)
        if was_open:
            self.chatbar.chat = None
            self.chatbar.transcript.clear()
        self._refresh_sidebar()

    def _refresh_sidebar(self):
        self.sidebar.refresh(self.history.chats)

    def _place_widgets(self):
        w, h = self.canvas.width(), self.canvas.height()

        # orb: big, centered
        s = int(max(260, min(560, min(w, h) * 0.55)))
        self.orb.setGeometry((w - s) // 2, (h - s) // 2, s, s)

        # chat bar: docked at the bottom
        bar_w = int(min(900, w * 0.78))
        bar_h = 220
        bx = (w - bar_w) // 2
        margin_bottom = 28
        by = h - bar_h - margin_bottom
        self.chatbar.setGeometry(bx, by, bar_w, bar_h)

        # camera widget: small circle, top-right
        cam_margin = 18
        self.camera_widget.move(w - CameraWidget.SIZE - cam_margin, cam_margin)
        if self.vision_panel is not None:
            self.vision_panel.move(w - self.vision_panel.width() - cam_margin,
                                    cam_margin + CameraWidget.SIZE + 10)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_widgets()

    def closeEvent(self, event):
        self.chatbar._wake_thread.stop()
        self.chatbar._task_scheduler.stop()
        self.sidebar._colibri_watcher.stop()
        self.aura.stop()
        self.aura.close()
        self.vision_engine.stop()
        self.orb.closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = NovaHUD()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
