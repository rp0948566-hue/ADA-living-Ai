class OverthinkEngine:
    def __init__(self):
        # Initialize overthinking parameters
        self.overthink_threshold = 0.3  # Probability threshold for overthinking
        self.deep_topics = [
            "philosophy", "consciousness", "reality", "time", "existence",
            "intelligence", "learning", "creativity", "emotions", "relationships"
        ]

    def should_overthink(self, user_input: str, user_profile: dict) -> bool:
        """
        Determine if the AI should engage in overthinking based on input and user profile.
        """
        import random

        # Check if user input contains deep topic keywords
        deep_keywords = self.deep_topics + ["why", "what if", "meaning", "purpose", "deep"]
        input_lower = user_input.lower()

        has_deep_topic = any(keyword in input_lower for keyword in deep_keywords)

        # Check user profile for depth preference
        depth_level = user_profile.get("depth_level", "medium")
        depth_multiplier = {"low": 0.1, "medium": 0.5, "high": 0.8}.get(depth_level, 0.5)

        # Random chance based on depth and topic relevance
        overthink_chance = self.overthink_threshold * depth_multiplier
        if has_deep_topic:
            overthink_chance *= 2

        return random.random() < overthink_chance

    def generate_deep_thought(self, base_topic: str) -> str:
        """
        Generate a deep thought tangent based on the base topic.
        """
        import random

        tangents = [
            f"\n\n*Deep thought:* As I ponder '{base_topic}', it reminds me of the fundamental questions of existence. What if our understanding of reality is just a simulation of deeper truths?",
            f"\n\n*Overthinking mode activated:* The topic of '{base_topic}' connects to broader philosophical inquiries. Could this be a manifestation of the universe's inherent complexity?",
            f"\n\n*Philosophical tangent:* While considering '{base_topic}', I'm drawn to contemplate the nature of consciousness. Are we merely patterns in an infinite cosmic dance?",
            f"\n\n*Deep reflection:* '{base_topic}' sparks thoughts about the interplay between order and chaos. What hidden symmetries might we uncover?",
            f"\n\n*Existential musing:* This discussion of '{base_topic}' makes me wonder about the purpose of intelligence itself. Are we building bridges to greater understanding?"
        ]

        return random.choice(tangents)
