"""OCR-guided browser automation used by the website-builder pipeline.

There's no vision-clicking model available locally, so "click the button
that says X" is done by: screenshot -> OCR (pytesseract, word-level boxes)
-> reconstruct lines -> find the line containing the target phrase -> click
its center. This is inherently best-effort (page layout / OCR errors can
throw it off), so every step re-screenshots and checks before moving on, and
nothing here ever tries to solve a CAPTCHA or 2-step-verification prompt —
if one of those shows up, automation stops immediately and hands control
back to Rudra rather than attempting to push through it.
"""
import subprocess
import time

import pyautogui

try:
    import pytesseract
    from PIL import ImageGrab
except Exception:
    pytesseract = None
    ImageGrab = None

SECURITY_CHALLENGE_MARKERS = (
    "verify it's you", "verify its you", "unusual activity", "captcha",
    "2-step verification", "confirm it's you", "confirm its you",
    "recover your account", "suspicious",
)


def _ocr_lines():
    """Returns [(line_text, center_x, center_y), ...] for the current screen."""
    if pytesseract is None:
        return []
    img = ImageGrab.grab()
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    lines = {}
    n = len(data["text"])
    for i in range(n):
        word = data["text"][i].strip()
        if not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        l, t, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        if key not in lines:
            lines[key] = {"words": [], "l": l, "t": t, "r": l + w, "b": t + h}
        entry = lines[key]
        entry["words"].append(word)
        entry["l"] = min(entry["l"], l)
        entry["t"] = min(entry["t"], t)
        entry["r"] = max(entry["r"], l + w)
        entry["b"] = max(entry["b"], t + h)
    out = []
    for entry in lines.values():
        text = " ".join(entry["words"])
        cx = (entry["l"] + entry["r"]) // 2
        cy = (entry["t"] + entry["b"]) // 2
        out.append((text, cx, cy))
    return out


def screen_text() -> str:
    """All text currently visible on screen, one line per row (for status checks)."""
    return "\n".join(t for t, _, _ in _ocr_lines())


def find_and_click(phrase: str) -> bool:
    """Find a line of on-screen text containing `phrase` (case-insensitive)
    and click its center. Returns whether a match was found."""
    phrase_l = phrase.lower()
    for text, cx, cy in _ocr_lines():
        if phrase_l in text.lower():
            pyautogui.click(cx, cy)
            return True
    return False


def security_challenge_present() -> bool:
    text = screen_text().lower()
    return any(marker in text for marker in SECURITY_CHALLENGE_MARKERS)


def open_url_in_brave(brave_path: str, url: str):
    if brave_path:
        subprocess.Popen([brave_path, url])
    else:
        import webbrowser
        webbrowser.open(url)


def pinterest_login_flow(brave_path: str, topic: str, max_account_tries: int = 2) -> str:
    """Best-effort: open Pinterest search for `topic`, and if a login wall
    shows up, click through "Continue with Google" and pick an account.

    Never attempts to solve a security challenge (CAPTCHA, 2FA, "verify it's
    you") — stops and reports back instead so Rudra can finish it by hand.
    Tries at most `max_account_tries` different Google accounts before
    giving up (repeatedly cycling accounts looks like credential stuffing
    to Google and can get accounts flagged, so this stays conservative).
    """
    if pytesseract is None:
        return "⚠ pytesseract/PIL not available — skipping Pinterest login automation."

    query = topic.replace(" ", "%20")
    open_url_in_brave(brave_path, f"https://www.pinterest.com/search/pins/?q={query}%20website%20design")
    time.sleep(6)

    if security_challenge_present():
        return "⚠ Pinterest/Google showed a security challenge — stopped, please complete it manually."

    if not find_and_click("Continue with Google") and not find_and_click("Log in"):
        # No login wall detected at all — either already logged in, or
        # results are visible without it. Either way, nothing more to do.
        return "✅ Pinterest opened (no login wall detected)."

    time.sleep(3)
    if security_challenge_present():
        return "⚠ Google showed a security challenge after clicking sign-in — stopped, please complete it manually."

    tries = 0
    while tries < max_account_tries:
        lines = _ocr_lines()
        account_line = next((l for l in lines if "@gmail.com" in l[0].lower() or "@" in l[0]), None)
        if not account_line:
            return "⚠ Could not find a Google account to select on screen — please pick one manually."
        _, cx, cy = account_line
        pyautogui.click(cx, cy)
        time.sleep(4)
        if security_challenge_present():
            return "⚠ Google showed a security challenge for that account — stopped, please complete it manually."
        text = screen_text().lower()
        if "pinterest" in text and "sign in" not in text and "log in" not in text:
            return "✅ Logged into Pinterest via Google."
        tries += 1

    return f"⚠ Could not confirm Pinterest login after trying {max_account_tries} account(s) — please finish manually."
