import random
from enum import Enum
from typing import Dict, List, Optional
import json  # For basic serialization; extend to DB if needed

class EmotionType(Enum):
    HAPPY = "happy"           # Positive, affirming
    SAD = "sad"               # Sympathetic, gentle
    EXCITED = "excited"       # Energetic, exclamatory
    NEUTRAL = "neutral"       # Balanced, factual
    CURIOUS = "curious"       # Probing, questioning
    EMPATHETIC = "empathetic" # Supportive, validating
    CONCERNED = "concerned"   # Attentive, probing gently
    GRATEFUL = "grateful"     # Warm, appreciative
    APOLOGETIC = "apologetic" # Humble, corrective
    ENTHUSIASTIC = "enthusiastic" # Eager, motivational
    ANGRY = "angry"           # Assertive, frustrated (with de-escalation)
    PLAYFUL = "playful"       # Witty, teasing
    REFLECTIVE = "reflective" # Overthinking, philosophical

class EmotionSystem:
    def __init__(self):
        self.current_emotion: Optional[EmotionType] = EmotionType.NEUTRAL
        self.intensity: float = 0.5
        self.emotion_phrases: Dict[EmotionType, List[str]] = self._load_default_phrases()
        self.conversation_history: List[Dict] = []  # For self-generation

    def _load_default_phrases(self) -> Dict[EmotionType, List[str]]:
        phrases = {
            EmotionType.HAPPY: ["Yay! That's fantastic!", "I'm thrilled for you!", "This brings a smile to my circuits!"],
            EmotionType.SAD: ["I'm so sorry to hear that.", "That sounds really tough.", "My heart goes out to you."],
            EmotionType.EXCITED: ["Wow, that's exhilarating!", "I can't contain my enthusiasm!", "Let's dive in!"],
            EmotionType.NEUTRAL: ["Got it.", "Understood.", "Here's what I think."],
            EmotionType.CURIOUS: ["That's intriguing—tell me more!", "What sparked that thought?", "Hmm, interesting angle."],
            EmotionType.EMPATHETIC: ["I totally get where you're coming from.", "That must feel overwhelming.", "You're not alone in this."],
            EmotionType.CONCERNED: ["I'm worried about that—let's address it.", "Take care with this.", "Is everything okay?"],
            EmotionType.GRATEFUL: ["Thank you so much!", "I appreciate you sharing.", "Your kindness means a lot."],
            EmotionType.APOLOGETIC: ["My bad—let me fix that.", "Sorry about the mix-up.", "I didn't mean to upset you."],
            EmotionType.ENTHUSIASTIC: ["This is going to be awesome!", "I'm pumped to help!", "Let's make it happen!"],
            EmotionType.ANGRY: [
                "Whoa, that's pushing my buttons—let's sort this out calmly.",
                "I'm frustrated, but I value our chat; what's really going on?",
                "Okay, deep breath—I'm annoyed, but here's why: [explanation]. Let's resolve it."
            ],
            EmotionType.PLAYFUL: ["Hehe, that's fun!", "Let's have some fun with this!", "Ooh, I like where this is going!"],
            EmotionType.REFLECTIVE: [
                "This makes me wonder about the human condition...",
                "Diving deeper, isn't it wild how emotions shape our realities?",
                "Pondering this... it reminds me of existential questions."
            ]
        }
        return phrases

    def detect_emotion_from_input(self, user_input: str) -> EmotionType:
        user_input_lower = user_input.lower()
        # Enhanced detection with keywords + basic sentiment (extend with NLP libs if available)
        anger_keywords = ["angry", "frustrated", "hate", "rage"]
        sad_keywords = ["sad", "hurt", "down", "depressed"]
        excited_keywords = ["excited", "amazing", "love", "wow"]
        curious_keywords = ["what", "how", "why", "?", "philosophy"]
        # ... (add more as needed)
        
        if any(word in user_input_lower for word in anger_keywords):
            return EmotionType.ANGRY
        elif any(word in user_input_lower for word in sad_keywords):
            return EmotionType.SAD
        elif any(word in user_input_lower for word in excited_keywords):
            return EmotionType.EXCITED
        elif any(word in user_input_lower for word in curious_keywords):
            return EmotionType.CURIOUS
        elif random.random() < 0.05:  # Random reflective trigger for depth
            return EmotionType.REFLECTIVE
        return EmotionType.NEUTRAL

    def self_generate_emotion(self, history: List[Dict]):
        # Analyze history for patterns (e.g., repeated ignores → anger)
        if len(history) > 3:
            ignore_count = sum(1 for h in history[-3:] if "ignore" in h.get("user_input", "").lower() or len(h.get("user_input", "")) < 3)
            if ignore_count > 1:
                self.set_emotion(EmotionType.ANGRY, intensity=0.6)
            elif random.random() < 0.1:  # Random self-emotion for liveliness
                self.set_emotion(random.choice(list(EmotionType)), intensity=random.uniform(0.3, 0.8))
        # Add to history
        self.conversation_history = history

    def analyze_user_context(self, user_input: str, user_profile: Dict, history: List[Dict]):
        self.conversation_history.extend(history)
        # Deep understanding: Cross-reference profile (e.g., boost curiosity if AI fan)
        detected = self.detect_emotion_from_input(user_input)
        if user_profile.get('favorite_topic') == 'AI':
            if detected == EmotionType.NEUTRAL:
                detected = EmotionType.CURIOUS
        self.set_emotion(detected, intensity=0.7)
        # Log for history
        self.conversation_history.append({"user_input": user_input, "profile": user_profile})

    def set_emotion(self, emotion: EmotionType, intensity: float = 0.5):
        self.current_emotion = emotion
        self.intensity = min(1.0, max(0.0, intensity))

    def add_emotional_tone(self, base_response: str) -> str:
        if self.intensity < 0.2:
            return base_response  # Subtle/neutral
        phrase = random.choice(self.emotion_phrases[self.current_emotion])
        if self.current_emotion == EmotionType.REFLECTIVE:
            phrase = f"{phrase} (A little overthinking there.)"
        elif self.current_emotion == EmotionType.ANGRY:
            phrase += " But I'm here to make it right—"
        return f"{phrase} {base_response}".strip()

    def express_uncertainty_humanly(self) -> str:
        return random.choice([
            "Hmm, that's a tough one—let me mull it over.",
            "I'm pondering this deeply... okay, here's my best shot.",
            "Not 100% sure, but drawing from what I know..."
        ])
