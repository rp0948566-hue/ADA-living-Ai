Mood Logger feature

This feature logs mood detections from the camera to a CSV file `mood_log.csv` at the repository root.

Functions:
- log_mood(description: str): append a row with timestamp, mood (if present), and the original description.
- read_logs(limit: int): return last `limit` rows from the log.

Usage:
Import lazily in `agent.py` and call `log_mood(desc)` each time `get_camera_view()` is called or after the agent reads camera data.
