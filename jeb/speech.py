"""Turn text into something nice to hear: no paths, URLs, code or symbol noise read aloud."""
import re

URL = re.compile(r"https?://\S+|www\.\S+")
HEX = re.compile(r"\b[0-9a-f]{12,}\b", re.I)
MD = re.compile(r"[`*_#>|~^]+|\[(\w[^\]]*)\]\([^)]*\)")


def _tail(tok: str) -> str:
    tok = tok.rstrip("/").split("/")[-1]
    return tok or "a folder"


# TTS reads these as words ("ram", "gpu"); spell them out letter by letter
SPELL = re.compile(r"\b(RAM|CPU|GPU|SSD|HDD|USB|VRAM|API|URL|GB|MB|TB|PC|OS|UI|GUI|AI|LLM|SQL|HTML|CSS|JSON|PDF|WiFi|SSH|TTS|STT)\b")
_SAY = {"GB": "gigabytes", "MB": "megabytes", "TB": "terabytes", "VRAM": "video R A M", "WiFi": "wifi"}


def _spell(m):
    w = m.group(1)
    return _SAY.get(w) or " ".join(w)


def speakable(text: str) -> str:
    t = URL.sub("a link", text)
    t = MD.sub(lambda m: m.group(1) or " ", t)
    t = SPELL.sub(_spell, t)
    t = HEX.sub("an ID", t)
    t = " ".join(_tail(w) if "/" in w and re.search(r"\w", w) and len(w) > 2 and not re.fullmatch(r"\w+/\w+", w) else w for w in t.split())
    t = " ".join(w for w in t.split() if re.search(r"\w", w))
    t = re.sub(r"[{}<>\\=\[\]]+", " ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" -:;,")
    return t if re.search(r"\w", t) else ""
