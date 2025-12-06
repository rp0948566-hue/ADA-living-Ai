from emotion_system import EmotionSystem, EmotionType
from memory_manager import MemoryManager
from overthink_engine import OverthinkEngine
from prompt_templates import get_emotional_prompt
# Assume an LLM wrapper; replace with your actual LLM call (e.g., OpenAI, Grok API)
# For demo, we'll use a simple mock LLM.

class MockLLM:
    def generate(self, prompt: str) -> str:
        # Mock response; replace with real LLM
        return f"Base response to: {prompt.split('User query: ')[1].split('\\n')[0]}. Here's some insightful info."

class AdaAgent:
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.emotion_system = EmotionSystem()
        self.memory = MemoryManager()
        self.overthink = OverthinkEngine()
        self.llm = MockLLM()  # Replace with real LLM
        self.conversation_history = []

    def generate_response(self, user_input: str) -> str:
        # Step 1: Load user data and history
        user_profile = self.memory.load_user_data(self.user_id)
        self.conversation_history = self.memory.get_conversation_history(self.user_id)

        # Step 2: Analyze context and detect/set emotion
        self.emotion_system.analyze_user_context(user_input, user_profile, self.conversation_history)

        # Step 3: Self-generate emotion if applicable
        self.emotion_system.self_generate_emotion(self.conversation_history)

        # Step 4: Generate base response via LLM with emotional prompt
        emotional_prompt = get_emotional_prompt(user_input, self.emotion_system.current_emotion, user_profile)
        base_response = self.llm.generate(emotional_prompt)

        # Step 5: Add overthinking if triggered
        if self.overthink.should_overthink(user_input, user_profile):
            overthink_tangent = self.overthink.generate_deep_thought(base_topic=user_input)
            base_response += overthink_tangent

        # Step 6: Process with emotional tone
        emotional_response = self.emotion_system.add_emotional_tone(base_response)

        # Step 7: If angry, ensure de-escalation
        if self.emotion_system.current_emotion == EmotionType.ANGRY:
            emotional_response += " Let's team up to fix this—what's your take?"

        # Step 8: Save interaction (reads/writes every time for freshness)
        self.memory.save_interaction(user_input, emotional_response, self.emotion_system.current_emotion.value, self.user_id)
        self.conversation_history.append({"input": user_input, "response": emotional_response})

        return emotional_response

# ================================================
# Example Usage: Run this to test
# ================================================

if __name__ == "__main__":
    # Initialize Ada
    ada = AdaAgent(user_id="test_user")

    # Save initial profile
    ada.memory.save_user_data("test_user", {"favorite_topic": "AI", "depth_level": "high"})

    # Test chats
    test_inputs = [
        "I'm so frustrated with this bug!",
        "What's the meaning of life?",
        "Thanks for the help earlier!",
        "Tell me about weather."  # Triggers potential overthink
    ]

    print("=== Ada AI Emotion System Demo ===\n")
    for inp in test_inputs:
        response = ada.generate_response(inp)
        print(f"User: {inp}\nAda: {response}\n{'-'*50}\n")

    print("Demo complete. Check ada_memory.json for saved data!")
