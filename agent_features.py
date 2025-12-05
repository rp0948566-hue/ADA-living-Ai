from livekit.agents import llm, function_tool
from livekit.agents.llm import LLM, ChatContext, ChatRole, LLMStream, ChatChunk, ToolContext
# Choice and ChoiceDelta might be missing in strict exports of some versions
# We define fallbacks to ensure compatibility
try:
    from livekit.agents.llm import Choice, ChoiceDelta
except ImportError:
    from dataclasses import dataclass, field
    from typing import List, Optional

    @dataclass
    class ChoiceDelta:
        content: Optional[str] = None
        role: Optional[ChatRole] = None
        tool_calls: Optional[List] = None

    @dataclass
    class Choice:
        delta: ChoiceDelta
        index: int = 0

from reminder_system import ReminderSystem
from ollama_integration import generate_response as ollama_generate_response

# ═════════════════════════════════════════════════════════════════════════════
# 🧠 OLLAMA LOCAL LLM INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════
class OllamaStream(LLMStream):
    """Stream implementation for OllamaLLM to satisfy LiveKit Agent requirements."""
    def __init__(self, chat_ctx: ChatContext, fnc_ctx: ToolContext | None):
        super().__init__(chat_ctx=chat_ctx, fnc_ctx=fnc_ctx)
    
    async def __aiter__(self):
        # Build prompt from conversation history
        prompt = ""
        for msg in self._chat_ctx.messages:
            # Simple prompt formatting
            role_label = msg.role.name.title() if msg.role else "User"
            if msg.text:
                prompt += f"{role_label}: {msg.text}\n"
        
        # Fetch full response from Ollama (non-streaming in this adapter)
        response_text = await ollama_generate_response(prompt)
        
        # Create a single chunk containing the full response
        # This mimics a stream with one packet which satisfies the SDK
        chunk = ChatChunk(
            choices=[
                Choice(
                    delta=ChoiceDelta(content=response_text, role=ChatRole.ASSISTANT),
                    index=0
                )
            ]
        )
        yield chunk

class OllamaLLM(LLM):
    """
    This class is a custom wrapper that allows the LiveKit agent framework to use
    a local Ollama model as its brain instead of a cloud service like Google's.
    """
    def __init__(self):
        super().__init__()

    # Updated signature to match LiveKit LLM base class requirements
    def chat(
        self,
        chat_ctx: ChatContext,
        fnc_ctx: ToolContext | None = None,
        temperature: float | None = None,
        n: int | None = None,
        parallel_tool_calls: bool | None = None,
    ) -> LLMStream:
        return OllamaStream(chat_ctx, fnc_ctx)


# ═════════════════════════════════════════════════════════════════════════════
# ⏰ REMINDER SYSTEM TOOL
# ═════════════════════════════════════════════════════════════════════════════
@function_tool(description="Adds a reminder for the user. For example: 'remind me to call John tomorrow at 5pm'")
def add_reminder(message: str, time_str: str):
    """Adds a reminder for the user. For example: 'remind me to call John tomorrow at 5pm'"""
    # Create an instance of the reminder system
    reminder_system = ReminderSystem()
    # Add the reminder and return the confirmation message
    return reminder_system.add_reminder(message, time_str)