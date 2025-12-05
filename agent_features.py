from livekit.agents import tool
from livekit.agents.llm import LLM, ChatContext, ChatMessage, ChatRole
from reminder_system import ReminderSystem
from ollama_integration import generate_response as ollama_generate_response

# ═════════════════════════════════════════════════════════════════════════════
# 🧠 OLLAMA LOCAL LLM INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════
class OllamaLLM(LLM):
    """
    This class is a custom wrapper that allows the LiveKit agent framework to use
    a local Ollama model as its brain instead of a cloud service like Google's.
    """
    def __init__(self):
        super().__init__()

    async def chat(self, history: ChatContext) -> 'ChatMessage':
        # Build a single prompt from the conversation history
        prompt = ""
        for msg in history.messages:
            prompt += f"{msg.role}: {msg.text}\n"
        
        # Get a response from the local Ollama model
        response_text = await ollama_generate_response(prompt)
        
        # Return the response in the format the agent expects
        return ChatMessage(role=ChatRole.ASSISTANT, text=response_text)


# ═════════════════════════════════════════════════════════════════════════════
# ⏰ REMINDER SYSTEM TOOL
# ═════════════════════════════════════════════════════════════════════════════
@tool
def add_reminder(message: str, time_str: str):
    """Adds a reminder for the user. For example: 'remind me to call John tomorrow at 5pm'"""
    # Create an instance of the reminder system
    reminder_system = ReminderSystem()
    # Add the reminder and return the confirmation message
    return reminder_system.add_reminder(message, time_str)

