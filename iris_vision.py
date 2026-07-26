"""IRIS's background computer-vision engine.

Runs body/pose (face-derived from pose keypoints) + hand-gesture tracking
off the camera in a background thread, using MediaPipe's Tasks API
(GestureRecognizer + PoseLandmarker — model bundles cached under
iris_data/vision_models/, auto-downloaded on first run).

Body/face tracking is backend-only — contextual awareness (is Rudra
present, roughly how he's postured) written to a small JSON file for the
MCP layer / SOUL context to read. Only HAND TRACKING (gesture + landmarks)
is surfaced to the GUI widget, per design: the camera widget shows hand
gestures, not a face/body dashboard.

Reuses features.camera_manager.CameraManager (the existing singleton
camera owner) rather than opening the device a second time.
"""
import json
import math
import os
import threading
import time
import urllib.request

from features.camera_manager import CameraManager
from features.storage import data_path

try:
    import cv2
except Exception:
    cv2 = None

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
except Exception:
    mp = None
    mp_python = None
    mp_vision = None

PRESENCE_FILE = data_path("vision_presence.json")  # backend-only: face/body context
SETTINGS_FILE = data_path("vision_settings.json")  # privacy toggles, persisted
MODELS_DIR = data_path("vision_models")

MODEL_URLS = {
    "gesture_recognizer.task": (
        "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/"
        "gesture_recognizer/float16/latest/gesture_recognizer.task"
    ),
    "pose_landmarker_lite.task": (
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
        "pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
    ),
}

DEFAULT_SETTINGS = {
    "camera_enabled": True,
    "face_recognition": True,   # derived from pose keypoints, backend-only
    "body_tracking": True,
    "hand_tracking": True,
    "gesture_recognition": True,
    "clap_detection": True,     # informational — clap detection itself lives in ParticleOrb
}

_GESTURE_MAP = {
    "Open_Palm": "open_hand",
    "Closed_Fist": "closed_fist",
    "Pointing_Up": "pointing",
    "Thumb_Up": "thumbs_up",
    "Thumb_Down": "thumbs_down",
    "Victory": "peace_sign",
    "ILoveYou": "i_love_you",
    "None": "none",
}


def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update({k: v for k, v in saved.items() if k in DEFAULT_SETTINGS})
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass


def _ensure_models() -> bool:
    """Download the (small, one-time) model bundles if not already cached."""
    try:
        os.makedirs(MODELS_DIR, exist_ok=True)
        for name, url in MODEL_URLS.items():
            path = os.path.join(MODELS_DIR, name)
            if os.path.exists(path) and os.path.getsize(path) > 100_000:
                continue
            urllib.request.urlretrieve(url, path)
        return True
    except Exception:
        return False


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


class VisionEngine:
    """Owns the MediaPipe models and a background processing thread.
    Thread-safe getters for the GUI (hand tracking) and backend consumers
    (presence/posture, written to PRESENCE_FILE)."""

    def __init__(self, target_fps: float = 8.0):
        self._interval = 1.0 / max(1.0, target_fps)
        self._lock = threading.Lock()
        self._thread = None
        self._stop = False
        self.settings = load_settings()

        self._hand_state = {"present": False, "gesture": "none", "landmarks": []}
        self._last_frame_jpeg = None  # small preview for the widget
        self._available = mp is not None and cv2 is not None

        self._gesture_recognizer = None
        self._pose_landmarker = None
        self._prev_pose_landmarks = None

    @property
    def available(self) -> bool:
        return self._available

    def start(self):
        if not self._available or self._thread is not None:
            return
        if not self.settings.get("camera_enabled", True):
            return
        if not _ensure_models():
            return
        ok, _msg = CameraManager().start(owner="vision_engine")
        if not ok:
            return

        gr_path = os.path.join(MODELS_DIR, "gesture_recognizer.task")
        self._gesture_recognizer = mp_vision.GestureRecognizer.create_from_options(
            mp_vision.GestureRecognizerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=gr_path),
                num_hands=2, running_mode=mp_vision.RunningMode.IMAGE,
            )
        )
        pl_path = os.path.join(MODELS_DIR, "pose_landmarker_lite.task")
        self._pose_landmarker = mp_vision.PoseLandmarker.create_from_options(
            mp_vision.PoseLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=pl_path),
                running_mode=mp_vision.RunningMode.IMAGE,
            )
        )

        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        CameraManager().stop(owner="vision_engine")

    def set_setting(self, key: str, value: bool):
        if key not in DEFAULT_SETTINGS:
            return
        self.settings[key] = value
        save_settings(self.settings)
        if key == "camera_enabled":
            if value:
                self.start()
            else:
                self.stop()

    def get_hand_state(self) -> dict:
        with self._lock:
            return dict(self._hand_state)

    def get_last_jpeg(self):
        with self._lock:
            return self._last_frame_jpeg

    # ------------------------------------------------------------------
    def _run(self):
        last_tick = 0.0
        while not self._stop:
            now = time.time()
            if now - last_tick < self._interval:
                time.sleep(0.01)
                continue
            last_tick = now

            ok, frame = CameraManager().get_latest_frame()
            if not ok or frame is None:
                continue

            frame = cv2.flip(frame, 1)  # mirror, natural for a preview widget
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            pose_ctx = self._process_pose(mp_image) if self.settings.get("body_tracking") else None
            hand_ctx = self._process_hands(mp_image) if self.settings.get("hand_tracking") else \
                {"present": False, "gesture": "none", "landmarks": []}

            with self._lock:
                self._hand_state = hand_ctx
                ok_enc, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if ok_enc:
                    self._last_frame_jpeg = buf.tobytes()

            self._write_presence(pose_ctx)

    def _process_pose(self, mp_image) -> dict:
        result = self._pose_landmarker.detect(mp_image)
        if not result.pose_landmarks:
            self._prev_pose_landmarks = None
            return {"present": False}

        pts = result.pose_landmarks[0]
        nose = pts[0]
        l_sh, r_sh = pts[11], pts[12]
        l_hip, r_hip = pts[23], pts[24]

        # face context derived from pose keypoints (no separate face model needed)
        area = abs(l_sh.x - r_sh.x) * abs((l_sh.y + r_sh.y) / 2 - nose.y) * 4
        distance = "close" if area > 0.06 else ("medium" if area > 0.015 else "far")
        face = {
            "present": True,
            "position": {"x": round(nose.x, 2), "y": round(nose.y, 2)},
            "distance": distance,
        }

        hip_visible = (getattr(l_hip, "visibility", 0) > 0.5) or (getattr(r_hip, "visibility", 0) > 0.5)
        shoulder_mid_y = (l_sh.y + r_sh.y) / 2

        moving = False
        if self._prev_pose_landmarks is not None:
            deltas = [
                math.hypot(pts[i].x - self._prev_pose_landmarks[i].x,
                           pts[i].y - self._prev_pose_landmarks[i].y)
                for i in (11, 12, 15, 16)  # shoulders + wrists
            ]
            moving = (sum(deltas) / len(deltas)) > 0.02
        self._prev_pose_landmarks = pts

        shoulder_width = abs(l_sh.x - r_sh.x) or 1.0
        lean = abs((l_sh.x + r_sh.x) / 2 - 0.5) / shoulder_width > 0.6

        posture = "standing" if hip_visible and (l_hip.y - shoulder_mid_y) > 0.35 else "sitting"
        if lean:
            posture = "leaning"
        elif moving:
            posture = "moving"

        return {"present": True, "posture": posture, "face": face}

    def _process_hands(self, mp_image) -> dict:
        result = self._gesture_recognizer.recognize(mp_image)
        if not result.hand_landmarks:
            return {"present": False, "gesture": "none", "landmarks": []}

        landmarks = result.hand_landmarks[0]
        gesture = "none"
        if result.gestures and result.gestures[0]:
            top = max(result.gestures[0], key=lambda c: c.score)
            gesture = _GESTURE_MAP.get(top.category_name, "unknown")

        # built-in vocabulary has no "pinch" — detect it geometrically as an override
        if self.settings.get("gesture_recognition"):
            scale = _dist(landmarks[0], landmarks[9]) or 1.0
            if _dist(landmarks[4], landmarks[8]) / scale < 0.35:
                gesture = "pinch"
        else:
            gesture = "none"

        return {
            "present": True,
            "gesture": gesture,
            "landmarks": [(round(p.x, 3), round(p.y, 3)) for p in landmarks],
        }

    def _write_presence(self, pose_ctx):
        try:
            pose_ctx = pose_ctx or {"present": False}
            payload = {
                "updated": time.time(),
                "face": pose_ctx.get("face", {"present": False}),
                "body": {"present": pose_ctx.get("present", False), "posture": pose_ctx.get("posture")},
            }
            with open(PRESENCE_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f)
        except Exception:
            pass


def read_presence() -> dict:
    """Backend-only accessor (e.g. for an MCP tool) — face/body context,
    never surfaced in the hand-tracking UI widget."""
    try:
        with open(PRESENCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"face": {"present": False}, "body": {"present": False}}
