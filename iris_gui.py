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

from PySide6.QtCore import Qt, QTimer, QPointF, QThread, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLineEdit, QPushButton,
    QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QTextEdit,
    QListWidget, QListWidgetItem, QFrame, QComboBox,
)

import iris_model_config
import iris_voice

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
                timeout=90,
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
        text = iris_voice.listen()
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
            text = iris_voice.listen(timeout=5, phrase_time_limit=8)
            if self._stop:
                return
            if text and not self._paused:
                self.heard.emit(text)
                time.sleep(0.3)  # beat for the main thread to pause us for a one-shot capture


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


class ChatBar(QWidget):
    """Conversation transcript + compact typing bar. Talks to Hermes
    directly over HTTP so the AI is usable without the voice pipeline.
    Persists every exchange to ChatHistoryStore for the sidebar."""

    chat_updated = Signal()  # tell the sidebar to refresh its list

    def __init__(self, history: ChatHistoryStore, parent=None):
        super().__init__(parent)
        self.history = history
        self.chat = None  # active chat dict from the history store
        self._worker = None
        self._listen_worker = None
        self._speak_worker = None

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

        box = QWidget()
        box.setObjectName("chatbox")
        box.setStyleSheet(
            "#chatbox { background:#1a1a1e; border:1px solid #2c2c32; border-radius:14px; }"
        )
        box.setFixedHeight(64)  # shrunk down from the original 110px
        row = QHBoxLayout(box)
        row.setContentsMargins(18, 0, 10, 0)
        row.setSpacing(8)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask Iris anything...")
        self.input.setStyleSheet(
            "QLineEdit { background:transparent; border:none; color:#E8E8EC;"
            " font-size:14px; }"
        )
        self.input.returnPressed.connect(self._send)
        row.addWidget(self.input, 1, Qt.AlignVCenter)

        self.send_btn = QPushButton("↑")
        self.send_btn.setFixedSize(30, 30)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet(
            "QPushButton { background:#3a3a42; color:white; border-radius:15px;"
            " font-size:14px; font-weight:bold; }"
            "QPushButton:hover { background:#4a4a54; }"
        )
        self.send_btn.clicked.connect(self._send)
        row.addWidget(self.send_btn, 0, Qt.AlignVCenter)

        outer.addWidget(box)

        # always-on listening — no button to click, just say "Iris ..." or
        # clap twice. Typing still works too.
        self.input.setPlaceholderText("Listening... just talk, or clap twice, or type here...")
        self._wake_thread = WakeListenerThread(self)
        self._wake_thread.heard.connect(self._on_wake_heard)
        self._wake_thread.start()

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

    def _send(self):
        text = self.input.text().strip()
        if not text:
            return
        self._dispatch(text, text)

    def _send_ambient(self, heard_text: str):
        """Continuously-overheard speech — no wake word required. Iris
        decides for herself whether it's directed at her and whether she
        can help; if not, she says nothing (see SOUL.md's NO_RESPONSE rule)."""
        if not heard_text:
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

    def _dispatch(self, display_text: str, payload_text: str):
        if self._worker is not None:
            return
        if self.chat is None:
            self.start_new_chat()

        self.input.clear()
        self.input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self._append_line("user", display_text)
        self.history.append(self.chat, "user", display_text)
        self.chat_updated.emit()
        self._thinking_line = "Iris is thinking..."
        self.transcript.append(f'<i style="color:#888">{self._thinking_line}</i>')

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

    def _on_reply(self, msg: str):
        if msg.strip().upper() == "NO_RESPONSE":
            # not directed at her / nothing she can help with — stay quiet
            self._remove_thinking_line()
            return
        self._replace_thinking(f'<b style="color:#D9B8FF">Iris:</b> {msg}')
        self.history.append(self.chat, "assistant", msg)
        self.chat_updated.emit()
        touch_ai_flag()  # let the orb react like Iris is "speaking"
        self._speak_worker = SpeakWorker(msg, self)
        self._speak_worker.start()

    def _on_failed(self, err: str):
        self._replace_thinking(f'<span style="color:#FF8080">⚠ Could not reach Iris: {err}</span>')

    def _cleanup(self):
        self.input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input.setFocus()
        self._worker = None

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
        self.input.setPlaceholderText("Listening...")
        self._listen_worker = ListenWorker(self)
        self._listen_worker.heard.connect(self._on_capture_heard)
        self._listen_worker.finished.connect(self._listen_cleanup)
        self._listen_worker.start()

    def _on_capture_heard(self, text: str):
        if text:
            self.input.setText(text)
            self._send()
        else:
            self.input.setPlaceholderText("Didn't catch that — try again or clap twice")

    def _listen_cleanup(self):
        self.input.setPlaceholderText("Listening... just talk, or clap twice, or type here...")
        self._listen_worker = None
        self._wake_thread.resume()


class Sidebar(QFrame):
    """Left panel — new-chat button + list of previous conversations."""

    new_chat_clicked = Signal()
    chat_selected = Signal(str)

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

        model_label = QLabel("BRAIN MODEL")
        model_label.setStyleSheet("color:#6b6b72; font-size:10px; font-weight:600; letter-spacing:1px;")
        lay.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(
            "QComboBox { background:#1f1f24; color:#E8E8EC; border:1px solid #2c2c32;"
            " border-radius:8px; padding:6px 8px; font-size:12px; }"
            "QComboBox QAbstractItemView { background:#1f1f24; color:#E8E8EC;"
            " selection-background-color:#3a3a42; }"
        )
        self._populate_models()
        self.model_combo.activated.connect(self._on_model_picked)
        lay.addWidget(self.model_combo)

        self.model_status = QLabel("")
        self.model_status.setWordWrap(True)
        self.model_status.setStyleSheet("color:#7fd48a; font-size:10px;")
        lay.addWidget(self.model_status)

        new_btn = QPushButton("+  New chat")
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet(
            "QPushButton { background:#1f1f24; color:#E8E8EC; border:1px solid #2c2c32;"
            " border-radius:10px; padding:8px; text-align:left; font-size:13px; }"
            "QPushButton:hover { background:#27272d; }"
        )
        new_btn.clicked.connect(self.new_chat_clicked.emit)
        lay.addWidget(new_btn)

        hist_label = QLabel("PREVIOUS CHATS")
        hist_label.setStyleSheet("color:#6b6b72; font-size:10px; font-weight:600; letter-spacing:1px;")
        lay.addWidget(hist_label)

        self.list = QListWidget()
        self.list.setStyleSheet(
            "QListWidget { background:transparent; border:none; color:#C9C9CF; font-size:12px; }"
            "QListWidget::item { padding:8px 6px; border-radius:8px; }"
            "QListWidget::item:selected { background:#24242b; color:#fff; }"
            "QListWidget::item:hover { background:#1c1c21; }"
        )
        self.list.itemClicked.connect(self._on_item_clicked)
        lay.addWidget(self.list, 1)

    def _on_item_clicked(self, item: QListWidgetItem):
        self.chat_selected.emit(item.data(Qt.UserRole))

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

        # pre-select whatever is actually active right now
        target = ("local", current_default) if current_is_local else ("cloud", current_default)
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == target:
                self.model_combo.setCurrentIndex(i)
                break
        self.model_combo.blockSignals(False)

    def _on_model_picked(self, index: int):
        kind, model_name = self.model_combo.itemData(index)
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
        self.list.clear()
        for c in chats:
            item = QListWidgetItem(c["title"] or "New chat")
            item.setData(Qt.UserRole, c["id"])
            self.list.addItem(item)


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
        root_lay.addWidget(self.sidebar)

        self.canvas = QWidget(root)
        root_lay.addWidget(self.canvas, 1)

        self.orb = ParticleOrb(self.canvas)
        self.chatbar = ChatBar(self.history, self.canvas)
        self.chatbar.chat_updated.connect(self._refresh_sidebar)
        self.orb.activate_requested.connect(self.chatbar.trigger_listen)  # clap twice -> listen

        self._refresh_sidebar()
        self._place_widgets()

        # auto-detect if any AI mode is already running; if not, turn the
        # last-selected one on automatically — and stand up the AI Command
        # Terminal — without blocking the UI thread.
        self._autostart = AutoStartWorker(self)
        self._autostart.done.connect(lambda msg: print(f"[iris] {msg}"))
        self._autostart.start()

    def _new_chat(self):
        self.chatbar.start_new_chat()

    def _select_chat(self, chat_id: str):
        self.chatbar.load_chat(chat_id)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_widgets()

    def closeEvent(self, event):
        self.chatbar._wake_thread.stop()
        self.orb.closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = NovaHUD()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
