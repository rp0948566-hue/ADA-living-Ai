"""
TONE ADAPTER INTEGRATION GUIDE FOR agent.py
=============================================

This guide shows exactly how to integrate ToneAdapter into agent.py for
adaptive tone-matched responses in your ADA-AI system.

Three integration patterns are provided:
1. Simple: Basic setup in __init__ and console loop
2. Advanced: With history, prosody, and logging
3. Full: Complete integration with voice/TTS
"""

# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION PATTERN 1: SIMPLE (Minimal Changes)
# ═════════════════════════════════════════════════════════════════════════════

"""
Add these imports at top of agent.py:

from tone_adapter import ToneAdapter, ToneConfig

Then in your Assistant class __init__:

    def __init__(self) -> None:
        # ... existing code ...
        
        # Initialize Tone Adapter
        self.tone_adapter = ToneAdapter(
            config=ToneConfig(model='llama3.1')
        )
        logger.info("✅ Tone Adapter loaded")

Then in your main chat loop (console or voice):

    # OLD CODE:
    # response = llm.generate(user_text)
    
    # NEW CODE:
    result = self.tone_adapter.adaptive_chat(user_text)
    reply = result['reply']
    tone = result['tone']
    
    print(f"[{tone.upper()}] {reply}")
"""

# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION PATTERN 2: ADVANCED (With History & Prosody)
# ═════════════════════════════════════════════════════════════════════════════

"""
More sophisticated integration maintaining conversation history and TTS hints.

In your Assistant class:

    def __init__(self) -> None:
        # ... existing code ...
        
        # Initialize Tone Adapter with config
        tone_config = ToneConfig(
            model='llama3.1',
            log_file='memory/tone_logs.json',
            max_history=5,
            max_words=200
        )
        self.tone_adapter = ToneAdapter(config=tone_config)
        self.conversation_history = []
        
        logger.info("✅ Tone Adapter initialized")
        logger.info(f"   Model: {self.tone_adapter.config.model}")
        logger.info(f"   Log: {self.tone_adapter.config.log_file}")

Then in your chat function:

    async def process_user_input(self, user_text: str) -> None:
        '''Process input with tone adaptation.'''
        try:
            # Get adaptive response with full metadata
            result = self.tone_adapter.adaptive_chat(
                user_text,
                conversation_history=self.conversation_history
            )
            
            # Extract all metadata
            reply = result['reply']
            tone = result['tone']
            topic = result['topic']
            intent = result['intent']
            confidence = result['confidence']
            tts_hints = result['tts_hints']
            
            # Display tone indicator
            tone_emoji = {
                'playful_roast': '😏',
                'romantic': '❤️',
                'sarcastic': '😒',
                'motivational': '🔥',
                'excited': '🚀',
                'frustrated': '😤',
                'professional': '💼',
                'neutral': '🤖'
            }
            emoji = tone_emoji.get(tone, '🤖')
            
            # Log to console
            print(f"\\n{emoji} [{tone.upper()}] Topic: {topic}")
            print(f"   Intent: {intent} | Confidence: {confidence:.2f}")
            print(f"   Reply: {reply}\\n")
            
            # Update history for next exchange
            self.conversation_history.append({
                'role': 'user',
                'content': user_text,
                'tone': tone,
                'topic': topic
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': reply
            })
            
            # Optional: Trim history if too long
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Log session metrics
            metrics = self.tone_adapter.get_metrics()
            print(f"Session: {metrics['total_interactions']} interactions, "
                  f"avg conf: {metrics['avg_confidence']:.2f}")
            
        except Exception as e:
            logger.error(f"Tone adaptation failed: {e}")
            # Fallback to simple response
            print(f"Response: {user_text}")
"""

# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION PATTERN 3: FULL (With TTS Prosody Integration)
# ═════════════════════════════════════════════════════════════════════════════

"""
Complete integration with TTS engine using prosody hints.

Prerequisites:
- TTS system installed (e.g., pyttsx3, gTTS, or custom)
- Audio output configured

In your Assistant class:

    def __init__(self) -> None:
        # ... existing code ...
        
        # Load tone adapter with YAML config
        tone_config = ToneConfig(config_file='tone_config.yaml')
        self.tone_adapter = ToneAdapter(config=tone_config)
        
        # Initialize TTS engine
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_enabled = True
        except ImportError:
            logger.warning("⚠️ pyttsx3 not found; TTS disabled")
            self.tts_enabled = False

Then add a method for TTS with prosody:

    def speak_adaptive(self, reply: str, prosody_hints: dict) -> None:
        '''Speak reply with prosody hints from tone adapter.'''
        if not self.tts_enabled:
            return
        
        try:
            # Apply prosody hints
            speed = prosody_hints.get('speed', 1.0)
            pitch = prosody_hints.get('pitch', 1.0)
            volume = prosody_hints.get('volume', 1.0)
            
            self.tts_engine.setProperty('rate', int(150 * speed))
            self.tts_engine.setProperty('volume', volume)
            
            logger.debug(f"TTS: speed={speed}, pitch={pitch}, volume={volume}")
            self.tts_engine.say(reply)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            logger.error(f"TTS playback failed: {e}")

Then use in chat loop:

    async def process_voice_input(self, user_audio_path: str) -> None:
        '''Process voice input with full tone adaptation + TTS.'''
        # Transcribe audio (using Whisper or similar)
        user_text = transcribe_audio(user_audio_path)
        
        # Get adaptive response
        result = self.tone_adapter.adaptive_chat(
            user_text,
            conversation_history=self.conversation_history
        )
        
        # Extract metadata
        reply = result['reply']
        tone = result['tone']
        prosody = result['tts_hints']
        
        # Speak with tone-matched prosody
        self.speak_adaptive(reply, prosody)
        
        # Update history
        self.conversation_history.append({
            'role': 'user',
            'content': user_text,
            'tone': tone
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': reply
        })
        
        logger.info(f"✅ Processed: {user_text[:50]}... → {tone}")
"""

# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE: Complete Updated Class
# ═════════════════════════════════════════════════════════════════════════════

"""
Here's a complete example class showing all integration points:

from tone_adapter import ToneAdapter, ToneConfig

class Assistant(Agent):
    def __init__(self) -> None:
        # ... your existing Agent init code ...
        
        # 🧠 Initialize Tone Adapter
        logger.info("🧠 Loading Tone Adapter...")
        self.tone_adapter = ToneAdapter(
            config=ToneConfig(
                model='llama3.1',
                config_file='tone_config.yaml'  # Optional YAML config
            )
        )
        logger.info(f"   ✅ Model: {self.tone_adapter.config.model}")
        logger.info(f"   ✅ Log: {self.tone_adapter.config.log_file}")
        
        # Conversation tracking
        self.conversation_history = []
    
    async def generate_adaptive_reply(self, user_input: str) -> dict:
        '''Generate adaptive response using tone adapter.'''
        
        # Get tone-matched response
        result = self.tone_adapter.adaptive_chat(
            user_input,
            conversation_history=self.conversation_history
        )
        
        # Update history
        self.conversation_history.append({
            'role': 'user',
            'content': user_input
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': result['reply']
        })
        
        return result
    
    def log_session_info(self) -> None:
        '''Log session statistics.'''
        metrics = self.tone_adapter.get_metrics()
        logger.info(f"📊 Session Metrics:")
        logger.info(f"   Total interactions: {metrics['total_interactions']}")
        logger.info(f"   Avg confidence: {metrics['avg_confidence']:.2f}")
        logger.info(f"   Log file: {metrics['log_file']}")
"""

# ═════════════════════════════════════════════════════════════════════════════
# QUICK CHECKLIST
# ═════════════════════════════════════════════════════════════════════════════

"""
Integration Checklist:

☑ 1. Import ToneAdapter and ToneConfig
      from tone_adapter import ToneAdapter, ToneConfig

☑ 2. Initialize in __init__
      self.tone_adapter = ToneAdapter(config=ToneConfig(...))

☑ 3. Replace chat calls
      result = self.tone_adapter.adaptive_chat(user_text, history)

☑ 4. Extract metadata
      reply = result['reply']
      tone = result['tone']
      prosody = result['tts_hints']

☑ 5. Maintain history (optional)
      self.conversation_history.append({'role': 'user', 'content': text})
      self.conversation_history.append({'role': 'assistant', 'content': reply})

☑ 6. Log metrics (optional)
      metrics = self.tone_adapter.get_metrics()

☑ 7. Test
      python test_tone_adapter.py -v

☑ 8. Run agent
      python agent.py console
"""

# ═════════════════════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ═════════════════════════════════════════════════════════════════════════════

"""
Q: "Ollama not available"
A: Install: pip install ollama
   Then ensure Ollama server is running: ollama serve

Q: "YAML config not loading"
A: pip install pyyaml
   Check tone_config.yaml syntax (must be valid YAML)

Q: "History gets too long"
A: Trim history periodically:
   if len(self.conversation_history) > 20:
       self.conversation_history = self.conversation_history[-20:]

Q: "Tone detection not accurate"
A: Add more keywords to tone_keywords in ToneConfig
   Check user input (must contain keywords)

Q: "TTS not working"
A: pip install pyttsx3
   Test: pyttsx3 -t "Hello world"

Q: "Logging to wrong file"
A: Check tone_adapter.py: log_file path
   Ensure memory/ directory exists
"""

# ═════════════════════════════════════════════════════════════════════════════
# MINIMAL WORKING EXAMPLE
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Minimal example: Just copy-paste to test."""
    from tone_adapter import ToneAdapter, ToneConfig
    
    # Create adapter
    adapter = ToneAdapter()
    
    # Test input
    user_input = "Roast me! lol this is fun"
    
    # Get adaptive response
    result = adapter.adaptive_chat(user_input)
    
    # Print results
    print(f"\nInput: {user_input}")
    print(f"Tone: {result['tone']}")
    print(f"Reply: {result['reply']}")
    print(f"Prosody: {result['tts_hints']}")
    print(f"\n✅ Integration working!")
