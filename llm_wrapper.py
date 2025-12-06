from livekit.plugins import google
from conversation_logger import update_last_entry

class LLMWrapper(google.beta.realtime.RealtimeModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def say(self, text, **kwargs):
        update_last_entry(text)
        return await super().say(text, **kwargs)
