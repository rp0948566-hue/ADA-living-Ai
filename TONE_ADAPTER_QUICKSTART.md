"""
TONE ADAPTER - Installation & Quick Start Guide
================================================

This guide covers everything needed to install and use the Tone Adapter
module in your ADA-AI system.
"""

# ═════════════════════════════════════════════════════════════════════════════
# INSTALLATION
# ═════════════════════════════════════════════════════════════════════════════

"""
STEP 1: Install Dependencies

Required:
    pip install ollama          # Local LLM backend
    pip install pytest          # For running tests

Optional (but recommended):
    pip install pyyaml          # For YAML config loading
    pip install pyttsx3         # For TTS (voice output)

Full install command:
    pip install ollama pytest pyyaml pyttsx3

Check installation:
    python -c "import ollama, pytest, yaml; print('✅ All packages installed')"
"""

# ═════════════════════════════════════════════════════════════════════════════
# SETUP
# ═════════════════════════════════════════════════════════════════════════════

"""
STEP 2: Ensure Ollama is Running

Prerequisites:
    1. Download Ollama from https://ollama.ai
    2. Install and start the service
    3. Verify it's running:

Command (Terminal 1 - Keep running):
    ollama serve

Check it's working (Terminal 2):
    ollama list
    ollama pull llama3.1  # Or your preferred model

Verify connection:
    python -c "import ollama; print(ollama.list()['models'])"
"""

# ═════════════════════════════════════════════════════════════════════════════
# FILE STRUCTURE
# ═════════════════════════════════════════════════════════════════════════════

"""
Project structure after installation:

ADA-ai/
├── tone_adapter.py                     # Core module (NEW)
├── test_tone_adapter.py                # Test suite (NEW)
├── tone_config.yaml                    # Config template (NEW)
├── TONE_ADAPTER_INTEGRATION.md         # This file (NEW)
├── agent.py                            # Your agent (MODIFY)
├── memory/
│   └── tone_logs.json                  # Auto-created by module
└── [other files...]

"""

# ═════════════════════════════════════════════════════════════════════════════
# QUICK START: 5 MINUTES
# ═════════════════════════════════════════════════════════════════════════════

"""
QUICK START DEMO:

1. Ensure Ollama is running:
   ollama serve  # (in separate terminal)

2. Test the module:
   python tone_adapter.py

Expected output:
   ======================================================================
   🧠 TONE ADAPTER DEMO
   ======================================================================

   Input: Ugh, this code is killing me lol
   Tone: frustrated (conf: 0.78)
   Topic: coding
   Intent: None
   Reply: [LLM-generated tone-matched response]

   TTS Prosody: {'speed': 0.8, 'pitch': 0.8, 'emphasis': 'calm', ...}
   ...

3. Run tests:
   pytest test_tone_adapter.py -v

Expected: All tests should pass (9+ assertions)

✅ You're ready to integrate!
"""

# ═════════════════════════════════════════════════════════════════════════════
# BASIC USAGE EXAMPLES
# ═════════════════════════════════════════════════════════════════════════════

"""
EXAMPLE 1: Simple Usage

from tone_adapter import ToneAdapter

# Create adapter
adapter = ToneAdapter()

# Get adaptive response
result = adapter.adaptive_chat("Roast me! lol")

# Access results
print(result['reply'])          # The actual response
print(result['tone'])           # Detected tone
print(result['topic'])          # Detected topic
print(result['confidence'])     # Confidence score (0.0-1.0)
print(result['tts_hints'])      # Voice prosody hints


EXAMPLE 2: With Conversation History

from tone_adapter import ToneAdapter

adapter = ToneAdapter()
history = []

# First exchange
result1 = adapter.adaptive_chat("Hey!", history)
history.append({'role': 'user', 'content': "Hey!"})
history.append({'role': 'assistant', 'content': result1['reply']})

# Second exchange (uses history context)
result2 = adapter.adaptive_chat("How's it going?", history)
history.append({'role': 'user', 'content': "How's it going?"})
history.append({'role': 'assistant', 'content': result2['reply']})

print(result2['reply'])  # Response now has context from first exchange


EXAMPLE 3: With Custom Configuration

from tone_adapter import ToneAdapter, ToneConfig

# Create custom config
config = ToneConfig(
    model='mistral',              # Use different model
    max_history=10,               # Remember more exchanges
    max_words=300,                # Longer responses
    log_file='custom_logs.json'   # Different log location
)

# Create adapter with config
adapter = ToneAdapter(config=config)
result = adapter.adaptive_chat("Tell me a story!")
print(result['reply'])


EXAMPLE 4: YAML Configuration

from tone_adapter import ToneAdapter, ToneConfig

# Load from YAML config file
config = ToneConfig(config_file='tone_config.yaml')
adapter = ToneAdapter(config=config)

# Use normally
result = adapter.adaptive_chat("What's up?")
print(result)
"""

# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION INTO agent.py
# ═════════════════════════════════════════════════════════════════════════════

"""
STEP 3: Add to agent.py

At the top of agent.py, add:

    from tone_adapter import ToneAdapter, ToneConfig

In your Assistant class __init__:

    def __init__(self) -> None:
        # ... existing code ...
        
        # Initialize tone adapter
        self.tone_adapter = ToneAdapter()
        logger.info("✅ Tone Adapter ready")

In your main chat loop:

    # OLD:
    # response = self.llm.generate(user_input)
    
    # NEW:
    result = self.tone_adapter.adaptive_chat(user_input)
    reply = result['reply']
    tone = result['tone']
    
    print(f"[{tone}] {reply}")

See TONE_ADAPTER_INTEGRATION.md for more complete examples.
"""

# ═════════════════════════════════════════════════════════════════════════════
# TESTING
# ═════════════════════════════════════════════════════════════════════════════

"""
RUN TESTS:

Basic test run:
    pytest test_tone_adapter.py -v

Run specific test:
    pytest test_tone_adapter.py::TestToneAdapter::test_detect_tone_playful -v

Run with output:
    pytest test_tone_adapter.py -v -s

Run with coverage (if pytest-cov installed):
    pytest test_tone_adapter.py --cov=tone_adapter

Test categories:
    - Tone detection (4 tests)
    - Adaptive chat & fallback (3 tests)
    - Logging system (2 tests)
    - Topic extraction (3 tests)
    - Intent detection (3 tests)
    - Configuration (3 tests)
    - Metrics tracking (1 test)
    - TTS prosody (2 tests)
    - Prompt generation (2 tests)
    - Integration tests (1 test)

Total: 24+ test cases covering all functionality
"""

# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURATION CUSTOMIZATION
# ═════════════════════════════════════════════════════════════════════════════

"""
CUSTOMIZE BEHAVIOR:

1. Add new tone (in tone_config.yaml or code):

   tone_keywords['motivational_dark'] = ['crushing it', 'dominate', 'reign']
   
   Then use it:
   result = adapter.adaptive_chat("I'm crushing goals!")


2. Add new topic (in tone_config.yaml or code):

   topic_clusters['music'] = ['song', 'artist', 'album', 'concert']
   
   Then detect it:
   topic = adapter.extract_topic("I love this artist!")


3. Add custom intent:

   config.intent_hooks['music_request'] = lambda inp: 'play' in inp.lower()
   
   Then check it:
   intent = adapter.check_intent("Play my favorite song")  # Returns 'music_request'


4. Adjust TTS prosody:

   config.tts_prosody['excited'] = {
       'speed': 1.5,      # Even faster
       'pitch': 1.5,      # Higher pitch
       'emphasis': 'wild'
   }
"""

# ═════════════════════════════════════════════════════════════════════════════
# LOGGING & MONITORING
# ═════════════════════════════════════════════════════════════════════════════

"""
MONITORING TONE LOGS:

The module automatically logs all interactions to memory/tone_logs.json:

View logs:
    python -c "import json; print(json.dumps(json.load(open('memory/tone_logs.json')), indent=2))"

Example log entry:
    {
        "timestamp": "2025-12-03T15:30:45.123456",
        "user_input": "Roast me! lol",
        "reply": "Haha, I love your energy! You're already crushing it...",
        "tone": "playful_roast",
        "topic": "general",
        "confidence": 0.92,
        "intent": "roast_request"
    }

Analyze logs:
    python -c "
    import json
    logs = json.load(open('memory/tone_logs.json'))
    tones = [l['tone'] for l in logs]
    print(f'Most common tone: {max(set(tones), key=tones.count)}')
    print(f'Avg confidence: {sum(l['confidence'] for l in logs) / len(logs):.2f}')
    "

Get metrics from adapter:
    metrics = adapter.get_metrics()
    print(metrics['total_interactions'])
    print(metrics['avg_confidence'])
"""

# ═════════════════════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ═════════════════════════════════════════════════════════════════════════════

"""
COMMON ISSUES & FIXES:

Issue: "ModuleNotFoundError: No module named 'ollama'"
Fix:   pip install ollama

Issue: "Connection refused" (Ollama)
Fix:   Make sure Ollama is running: ollama serve (in another terminal)

Issue: "Model not found" error
Fix:   Pull the model: ollama pull llama3.1

Issue: "YAML config not loading"
Fix:   pip install pyyaml
        Check YAML syntax: yaml tone_config.yaml

Issue: "TTS not working"
Fix:   pip install pyttsx3
        On Linux, may need: sudo apt install espeak

Issue: "Tests fail"
Fix:   Run tests with Ollama running
        Check: ollama list (should show llama3.1)
        Run: pytest -v -s to see detailed output

Issue: "Memory file not created"
Fix:   Ensure memory/ directory exists: mkdir memory
        Check file permissions: ls -la memory/

Issue: "Tone not detected correctly"
Fix:   Add keywords to tone_config.yaml
        Example: Add 'boss' to motivational if user says "I'm the boss"
"""

# ═════════════════════════════════════════════════════════════════════════════
# PERFORMANCE TIPS
# ═════════════════════════════════════════════════════════════════════════════

"""
OPTIMIZATION:

1. Reuse adapter instance:
   ✅ GOOD:  adapter = ToneAdapter()  # Create once
            while True:
                result = adapter.adaptive_chat(text)
   
   ❌ BAD:   for text in texts:
                adapter = ToneAdapter()  # Recreates each time!

2. Batch processing (if available):
   inputs = ["text1", "text2", "text3"]
   results = [adapter.adaptive_chat(text) for text in inputs]

3. Cache results:
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_cached_tone(text):
       return adapter.detect_tone(text)

4. Monitor memory:
   metrics = adapter.get_metrics()
   print(f"Interactions: {metrics['total_interactions']}")
   # If too high, consider creating new adapter instance
"""

# ═════════════════════════════════════════════════════════════════════════════
# NEXT STEPS
# ═════════════════════════════════════════════════════════════════════════════

"""
AFTER QUICK START:

1. ✅ Install dependencies (5 min)
   pip install ollama pytest pyyaml

2. ✅ Run demo (2 min)
   python tone_adapter.py

3. ✅ Run tests (2 min)
   pytest test_tone_adapter.py -v

4. ✅ Read integration guide (5 min)
   Read: TONE_ADAPTER_INTEGRATION.md

5. ✅ Integrate into agent.py (10 min)
   Add 3-4 lines of code as shown above

6. ✅ Test integration (5 min)
   python agent.py console
   (Try different tones)

7. ✅ Customize (10 min)
   Edit tone_config.yaml
   Add tones/topics/intents you need

Total time: ~40 minutes from install to production
"""

# ═════════════════════════════════════════════════════════════════════════════
# SUPPORT & RESOURCES
# ═════════════════════════════════════════════════════════════════════════════

"""
FILES PROVIDED:

Code:
  - tone_adapter.py              Core module (500+ lines)
  - test_tone_adapter.py         Test suite (24+ tests)

Configuration:
  - tone_config.yaml             YAML config template

Documentation:
  - TONE_ADAPTER_INTEGRATION.md  Integration patterns
  - TONE_ADAPTER_QUICKSTART.md   This file

Resources:
  - Ollama: https://ollama.ai
  - PyTest: https://pytest.org
  - PyYAML: https://pyyaml.org

Debugging:
  - Check logs: memory/tone_logs.json
  - Run tests: pytest -v -s
  - Check Ollama: ollama list

Contact: See agent.py maintainer
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║           🧠 TONE ADAPTER - QUICK START GUIDE                 ║
╚════════════════════════════════════════════════════════════════╝

Next steps:
1. pip install ollama pytest pyyaml pyttsx3
2. ollama serve  (in separate terminal)
3. python tone_adapter.py
4. pytest test_tone_adapter.py -v
5. Read TONE_ADAPTER_INTEGRATION.md
6. Add to agent.py

Questions? Check TONE_ADAPTER_INTEGRATION.md

Ready! 🚀
""")
