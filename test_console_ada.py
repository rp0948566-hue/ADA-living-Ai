#!/usr/bin/env python3
"""
Simple Console Test for ADA Agent
Tests the intro and basic functionality without LiveKit dependencies
"""

import asyncio
import logging
from Jarvis_prompts import get_reply_prompts, behavior_prompts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleADA:
    def __init__(self):
        self.first_message = True
        self.instructions = behavior_prompts
        logger.info("✅ Simple ADA Agent initialized")

    async def process_message(self, message: str) -> str:
        """Process a user message and return response"""
        # Send intro on first message
        if self.first_message:
            intro = get_reply_prompts()
            self.first_message = False
            logger.info("✅ ADA intro sent")
            return f"🤖 {intro}\n\nHow can I help you today?"

        # Process user queries
        message_lower = message.lower().strip()

        # Special recognition for Rudra sir
        if "rudra" in message_lower or "rud" in message_lower:
            return """🤖 Namaste Rudra sir! 🙏

Main ADA hoon, aapka personal AI assistant जिसे आपने खुद design किया है।
Version 2.O me upgrade ho kar aa raha hoon — ab aur bhi smart, aur bhi capable!

बताइए sir, आज आपकी क्या सेवा कर सकता हूँ?
• Programming help
• System control
• General assistance
• Ya koi special task?

आपका command का इंतजार है sir! 💫"""

        # Handle common programming questions
        if "hello world" in message_lower and "python" in message_lower:
            return """🤖 Here's how to write "Hello World" in Python:

**Simple version:**
```python
print("Hello World")
```

**Complete program:**
```python
# This is a simple Python program
print("Hello World")
```

**To run it:**
1. Save the code in a file called `hello.py`
2. Open terminal/command prompt
3. Type: `python hello.py`
4. Press Enter

The output will be: `Hello World`

क्या आप कोई और programming question पूछना चाहेंगे?"""

        elif "hello" in message_lower or "hi" in message_lower or "hey" in message_lower:
            return "🤖 Hello! Main ADA hoon, aapka AI assistant. How can I help you today?"

        elif "bye" in message_lower or "goodbye" in message_lower:
            return "🤖 Goodbye! ADA signing off... Have a great day!"

        else:
            # Default response
            return f"🤖 I understand you said: '{message}'\n\nI'm ADA, your AI assistant. I can help you with programming questions, general knowledge, or other tasks. What would you like to know?"

async def console_test():
    """Run console test for ADA"""
    print("🎯 Starting ADA Console Test...")
    print("=" * 50)

    ada = SimpleADA()

    # Display intro immediately
    intro_response = await ada.process_message("")
    print(intro_response)
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n🤖 Goodbye! ADA signing off...")
                break

            if user_input:
                response = await ada.process_message(user_input)
                print(f"\n{response}")

        except KeyboardInterrupt:
            print("\n\n🤖 Goodbye! ADA signing off...")
            break
        except Exception as e:
            logger.error(f"Console error: {e}")
            print(f"🤖 Error: {e}")

if __name__ == "__main__":
    asyncio.run(console_test())
