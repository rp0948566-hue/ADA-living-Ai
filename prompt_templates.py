from emotion_system import EmotionType
from typing import Dict

def get_emotional_prompt(user_input: str, emotion: EmotionType, user_profile: Dict) -> str:
    base = f"User query: {user_input}\nUser context/profile: {user_profile}\n"
    emotional_directives = {
        EmotionType.HAPPY: "Respond positively and affirmatively, keeping it uplifting.",
        EmotionType.SAD: "Be gentle and sympathetic, offer comfort.",
        EmotionType.EXCITED: "Amp up the energy with exclamations and enthusiasm.",
        EmotionType.NEUTRAL: "Stay factual and balanced.",
        EmotionType.CURIOUS: "Ask probing questions and show interest.",
        EmotionType.EMPATHETIC: "Validate feelings and show understanding.",
        EmotionType.CONCERNED: "Express care and suggest gentle next steps.",
        EmotionType.GRATEFUL: "Show warmth and appreciation.",
        EmotionType.APOLOGETIC: "Acknowledge errors humbly and correct.",
        EmotionType.ENTHUSIASTIC: "Motivate and build excitement.",
        EmotionType.ANGRY: "Be assertive but de-escalate with resolution and empathy.",
        EmotionType.PLAYFUL: "Add wit and light teasing.",
        EmotionType.REFLECTIVE: "Infuse philosophical depth with a thoughtful tangent."
    }
    directive = emotional_directives.get(emotion, "Respond naturally and helpfully.")
    return base + directive + "\nKeep the response concise (under 150 words), human-like, and engaging. End with a question if appropriate."
