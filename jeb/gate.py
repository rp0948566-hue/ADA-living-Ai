"""Zero-token gate: decide if Jeb should answer an utterance. No LLM here."""
import re
import time
from dataclasses import dataclass, field

QUESTION = re.compile(r"\?\s*$|^(what|why|how|when|where|who|which|can|could|should|is|are|do|does|did|will|would)\b", re.I)
COMMAND = re.compile(r"^(open|close|play|stop|pause|search|find|show|run|type|click|write|send|remind|set|turn|start|tell|check|look|read|fix|build|make|create|delete|install)\b", re.I)
# Wake words (plus the spellings whisper tends to produce). Nothing else addresses Jeb except an Alt tap, claps, or an answer to his own question.
ADDRESS = re.compile(r"\b(jeb|jeff|jev|jed|jebb)\b", re.I)
# Talking to someone else in the room: a name + greeting, or "yes/no" answers with no question context.
OTHER_PERSON = re.compile(r"^(hey|hi|hello|yes|yeah|no|okay|ok|thanks|thank you|hmm|uh|um)\b[\s,.!]*\w{0,12}[.!]?$", re.I)


# A spoken promise of action. If one is said and no tool ran this turn, Jeb must own up to it.
PROMISE = re.compile(r"\b(on it|checking|looking( it)? up|opening|launching|searching|pulling (it|that) up|let me (open|pull|check|look|search|find|run|start)|i'?ll (open|run|check|search|start|launch)|i'?m (opening|checking|running|starting|launching))\b", re.I)
WINDOW = 8.0  # seconds after Jeb stops speaking when any follow-up is for him, no name/Alt needed


def hollow_promise(reply: str, tool_ran: bool) -> bool:
    return bool(PROMISE.search(reply)) and not tool_ran


@dataclass
class Gate:
    """State: recent typing, Alt hold, last time Jeb spoke."""
    alt_down_at: float | None = None
    alt_combo: bool = False
    last_key_at: float = 0.0
    last_spoke_at: float = 0.0
    names: set = field(default_factory=lambda: {"jeb", "jeff"})
    force: bool = False
    expect_reply: bool = False  # Jeb just asked a question, so the next utterance is probably the answer

    # --- keyboard events (from evdev) ---
    def key(self, name: str, down: bool, now: float | None = None):
        now = time.monotonic() if now is None else now
        if name in ("KEY_LEFTALT", "KEY_RIGHTALT"):
            if down:
                self.alt_down_at, self.alt_combo = now, False
            else:
                # clean tap (no other key during hold, under 0.6s) = "I need you"
                if self.alt_down_at is not None and not self.alt_combo and now - self.alt_down_at < 0.6:
                    self.force = True
                self.alt_down_at = None
        else:
            self.last_key_at = now
            if self.alt_down_at is not None:
                self.alt_combo = True  # Alt used in a shortcut, not a request

    def typing(self, now: float, window: float = 1.5) -> bool:
        return now - self.last_key_at < window

    # --- decision ---
    def decide(self, text: str, now: float | None = None, claps: int = 0) -> tuple[bool, str]:
        now = time.monotonic() if now is None else now
        t = text.strip()
        if self.force:
            self.force = False
            return True, "alt-tap"
        if claps >= 2:
            return True, "claps"
        if not t:
            return False, "empty"
        low = t.lower()
        if any(n in low for n in self.names) or ADDRESS.search(t):
            return True, "addressed"
        if self.typing(now):
            return False, "user typing"
        if OTHER_PERSON.match(t):
            return False, "side talk"
        if self.expect_reply and now - self.last_spoke_at < WINDOW and not OTHER_PERSON.match(t):
            self.expect_reply = False
            return True, "answer"
        # Everything else (commands, questions, chatter) is for other people unless Jeb was addressed.
        return False, "ambient"
