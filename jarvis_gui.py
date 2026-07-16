# jarvis_gui.py
# J.A.R.V.I.S HUD — rebuilding step by step.
# Step 1: blank canvas, background #171717.
# Step 2: particle-sphere orb (dotted wavy energy ball) anchored bottom-right.
#         - idle       : purple core / orange rim, slow organic waves
#         - user speaks: deep blue / bright cyan, ripples follow mic loudness
#         - AI speaks  : violet / white-gold, fast rhythmic pulsing
#           (AI mode triggers when jarvis_data/ai_speaking.flag is touched;
#            agent.py's TTS hook can touch that file while speaking.)

import math
import os
import sys
import time

import numpy as np

from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

try:
    import sounddevice as sd
except Exception:
    sd = None

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_FLAG = os.path.join(PROJECT_DIR, "jarvis_data", "ai_speaking.flag")

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
        self._stream = None
        if sd is not None:
            try:
                def _cb(indata, frames, t, status):
                    rms = float(np.sqrt(np.mean(indata ** 2)))
                    self._mic = max(rms, self._mic * 0.82)
                    # sharp transient well above ambient baseline = clap/snap
                    if rms > max(0.10, self._rms_slow * 5.0):
                        self._clap_time = time.time()
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


class NovaHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S HUD")
        self.resize(1200, 720)
        self.setStyleSheet("background-color: #171717;")

        canvas = QWidget()
        self.setCentralWidget(canvas)
        self.orb = ParticleOrb(canvas)
        self._place_orb()

    def _place_orb(self):
        s = int(max(180, min(320, min(self.width(), self.height()) * 0.30)))
        margin = 18
        self.orb.setGeometry(
            self.width() - s - margin, self.height() - s - margin, s, s
        )

    def resizeEvent(self, event):
        self._place_orb()
        super().resizeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = NovaHUD()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
