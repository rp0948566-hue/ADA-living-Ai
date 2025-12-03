"""
TONE ADAPTER INTEGRATION CHECKLIST
===================================

Use this checklist to track your progress integrating the Tone Adapter
module into your ADA-AI system.
"""

# ═════════════════════════════════════════════════════════════════════════════
# PRE-INTEGRATION CHECKLIST
# ═════════════════════════════════════════════════════════════════════════════

PRE_INTEGRATION = """
Before you start integrating Tone Adapter into agent.py:

PHASE 1: INSTALLATION ✓
  □ Install dependencies: pip install -r requirements_tone_adapter.txt
    └─ Commands:
       • pip install ollama pytest pyyaml pyttsx3
       • Verify: python -c "import ollama, pytest, yaml; print('OK')"
  
  □ Verify Ollama is installed
    └─ Commands:
       • Download from https://ollama.ai
       • Install and verify: ollama --version
  
  □ Ensure file structure
    └─ Check:
       • tone_adapter.py (exists in ADA-ai/)
       • test_tone_adapter.py (exists in ADA-ai/)
       • tone_config.yaml (exists in ADA-ai/)
       • agent.py (main file to modify)

PHASE 2: TESTING (BEFORE INTEGRATION)
  □ Run Ollama service
    └─ Open terminal 1:
       • ollama serve
       • Wait for: "Listening on 127.0.0.1:11434"
  
  □ Verify Ollama connection
    └─ Open terminal 2:
       • python -c "import ollama; print(ollama.list()['models'])"
       • Should list available models
  
  □ Run demo script
    └─ python tone_adapter_demo.py
    └─ Select option: 0 (run all demos)
    └─ Expected: All tests should show ✅
  
  □ Run test suite
    └─ pytest test_tone_adapter.py -v
    └─ Expected: All 24+ tests should PASS

  □ Check log file creation
    └─ ls -la memory/tone_logs.json
    └─ Should exist and contain JSON data

STATUS: ✅ All pre-integration checks passed?
         → Proceed to integration

         ❌ Some checks failed?
         → See TROUBLESHOOTING section below
"""

# ═════════════════════════════════════════════════════════════════════════════
# INTEGRATION CHECKLIST
# ═════════════════════════════════════════════════════════════════════════════

INTEGRATION_STEPS = """
PHASE 3: INTEGRATION INTO agent.py

Step 1: Add Imports
  □ Location: Top of agent.py (with other imports)
  □ Add these lines:
    
    from tone_adapter import ToneAdapter, ToneConfig

  □ Verify: File saves without import errors

Step 2: Initialize Tone Adapter
  □ Location: In your Assistant class __init__ method
  □ Add after existing initializations:
    
    # Initialize tone adapter
    self.tone_adapter = ToneAdapter()
    logger.info("✅ Tone Adapter initialized")

  □ Verify: Class initializes without errors

Step 3: Modify Chat Method
  □ Location: Your main chat processing method (e.g., process_chat, chat_turn, etc.)
  □ Current code (BEFORE):
    
    def chat(self, user_input):
        response = self.llm.generate(user_input)
        return response

  □ Replace with (AFTER):
    
    def chat(self, user_input):
        # Use tone adapter for adaptive response
        result = self.tone_adapter.adaptive_chat(user_input)
        
        # Access response components
        response = result['reply']              # The actual response text
        tone = result['tone']                   # Detected tone (playful_roast, etc.)
        confidence = result['confidence']       # Confidence score (0.0-1.0)
        topic = result['topic']                 # Detected topic
        tts_hints = result['tts_hints']         # Voice prosody hints
        
        return response

  □ Verify: Chat method works with new code

Step 4: (Optional) Add Voice Prosody
  □ Location: Where audio/TTS output is generated
  □ Add prosody hints:
    
    result = self.tone_adapter.adaptive_chat(user_input)
    response = result['reply']
    prosody = result['tts_hints']
    
    # Apply to TTS engine:
    tts_engine.setProperty('rate', 200 * prosody['speed'])    # Speed adjustment
    tts_engine.setProperty('pitch', 1.0 * prosody['pitch'])   # Pitch adjustment
    tts_engine.say(response)

  □ Verify: Voice output uses prosody hints

Step 5: (Optional) Add Conversation History
  □ Location: Main conversation loop
  □ Initialize history:
    
    self.conversation_history = []

  □ Update chat method:
    
    def chat(self, user_input):
        result = self.tone_adapter.adaptive_chat(
            user_input,
            self.conversation_history  # Pass history
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
        
        return result['reply']

  □ Verify: History is maintained across turns
"""

# ═════════════════════════════════════════════════════════════════════════════
# VERIFICATION CHECKLIST
# ═════════════════════════════════════════════════════════════════════════════

VERIFICATION = """
PHASE 4: VERIFICATION (AFTER INTEGRATION)

Step 1: Syntax Check
  □ Run: python agent.py (should import without errors)
  □ Expected: No ImportError or ModuleNotFoundError
  □ Status: ✅ or ❌

Step 2: Initialization Test
  □ Start your agent
  □ Check logs for: "✅ Tone Adapter initialized"
  □ Status: ✅ or ❌

Step 3: Single Tone Test
  □ Send input: "Roast me! This is hilarious"
  □ Check:
    • Response received? ✅ or ❌
    • Tone detected (should be playful_roast)? ✅ or ❌
    • Confidence > 0.5? ✅ or ❌

Step 4: Multiple Tone Test
  □ Send: "I'm so frustrated right now"
    → Check: tone should be 'frustrated'
    → Status: ✅ or ❌
  
  □ Send: "I love this so much!"
    → Check: tone should be 'excited' or 'romantic'
    → Status: ✅ or ❌
  
  □ Send: "Please explain how machine learning works"
    → Check: tone should be 'professional'
    → Status: ✅ or ❌

Step 5: History Test (if implemented)
  □ Turn 1: "Hi there!"
    → Response received? ✅ or ❌
  
  □ Turn 2: "How are you?"
    → Response shows context awareness? ✅ or ❌
  
  □ Turn 3: "Tell me a story"
    → Response continues conversation properly? ✅ or ❌

Step 6: Logging Test
  □ Check: memory/tone_logs.json exists? ✅ or ❌
  □ Verify: Contains entries for all chats? ✅ or ❌
  □ Check format: Valid JSON? ✅ or ❌

Step 7: Performance Test
  □ Monitor memory usage (should be low)
  □ Check response time (should be < 5 seconds)
  □ Verify: No crashes or errors? ✅ or ❌

INTEGRATION STATUS: 
  ✅ All 7 verification steps passed?
     → Integration successful! 🎉
  
  ❌ Some steps failed?
     → See TROUBLESHOOTING section
"""

# ═════════════════════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ═════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING = """
COMMON ISSUES & SOLUTIONS

Issue 1: "ModuleNotFoundError: No module named 'tone_adapter'"
  Cause: tone_adapter.py not in current directory or not in Python path
  Fix:
    1. Check: Is tone_adapter.py in the ADA-ai/ directory?
    2. Verify: python -c "import sys; print(sys.path)"
    3. From ADA-ai directory, run: python agent.py
    4. Or add to Python path: export PYTHONPATH="${PYTHONPATH}:/path/to/ADA-ai"

Issue 2: "Connection refused" or Ollama errors
  Cause: Ollama service not running
  Fix:
    1. Open separate terminal
    2. Run: ollama serve
    3. Wait for: "Listening on 127.0.0.1:11434"
    4. Verify model: ollama list
    5. Try again in main terminal

Issue 3: "Model not found" error
  Cause: Ollama model not available
  Fix:
    1. Pull the model: ollama pull llama3.1
    2. Or use different model:
       config = ToneConfig(model='mistral')
    3. Verify available: ollama list

Issue 4: Tests fail with "assert" errors
  Cause: Tone detection not working as expected
  Fix:
    1. Check Ollama is running
    2. Check model is installed: ollama pull llama3.1
    3. Run single test: pytest test_tone_adapter.py::TestToneAdapter::test_detect_tone_playful -v
    4. Check tone keywords in tone_config.yaml

Issue 5: "YAML config file not found"
  Cause: tone_config.yaml missing
  Fix:
    1. Check file exists: ls tone_config.yaml
    2. Or don't use config file:
       config = ToneConfig()  # Uses defaults
    3. Or install PyYAML: pip install pyyaml

Issue 6: Memory file not created
  Cause: memory/ directory doesn't exist or permissions issue
  Fix:
    1. Create directory: mkdir memory
    2. Check permissions: chmod 755 memory
    3. Verify: ls -la memory/

Issue 7: Responses are generic/not tone-matched
  Cause: LLM not receiving tone context properly
  Fix:
    1. Check tone is detected: print(result['tone'])
    2. Check confidence: print(result['confidence'])
    3. Try different input: Use keywords from tone_config.yaml
    4. Increase max_words: ToneConfig(max_words=500)

Issue 8: Slow responses or timeouts
  Cause: Ollama processing is slow
  Fix:
    1. Use faster model: ToneConfig(model='tinyllama')
    2. Reduce max_words: ToneConfig(max_words=100)
    3. Increase timeout: Modify tone_adapter.py line with timeout
    4. Check system resources: CPU/RAM available?

Issue 9: agent.py crashes after integration
  Cause: Syntax error or incompatible code
  Fix:
    1. Syntax check: python -m py_compile agent.py
    2. Run from directory: cd ADA-ai && python agent.py
    3. Check indentation in agent.py modification
    4. Use try/except: 
       try:
           result = self.tone_adapter.adaptive_chat(user_input)
       except Exception as e:
           print(f"Tone adapter error: {e}")
           result = {'reply': user_input}  # Fallback

Issue 10: TTS prosody hints not working
  Cause: Prosody not connected to voice engine
  Fix:
    1. Check pyttsx3 installed: pip install pyttsx3
    2. Apply prosody correctly:
       prosody = result['tts_hints']
       engine.setProperty('rate', 200 * prosody['speed'])
    3. Test TTS separately: Check pyttsx3 documentation

STILL STUCK?
  1. Check memory/tone_logs.json for error patterns
  2. Run: pytest test_tone_adapter.py -v -s (verbose output)
  3. Enable debug: Set DEBUG=1 in tone_adapter.py
  4. Check README files:
     - TONE_ADAPTER_INTEGRATION.md
     - TONE_ADAPTER_QUICKSTART.md
  5. Restart Ollama: killall ollama && ollama serve
"""

# ═════════════════════════════════════════════════════════════════════════════
# ROLLBACK PLAN
# ═════════════════════════════════════════════════════════════════════════════

ROLLBACK = """
EMERGENCY ROLLBACK (If integration goes wrong)

Quick Rollback:
  1. Restore agent.py from backup:
     git checkout agent.py
     (if using git)
  
  2. Or manually remove these lines:
     - import ToneAdapter line (top)
     - self.tone_adapter = ToneAdapter() (in __init__)
     - result = self.tone_adapter.adaptive_chat() (in chat method)
     - Restore old response = self.llm.generate() line

  3. Verify restoration:
     python agent.py
     (should work without tone_adapter errors)

  4. Check git status:
     git status
     git diff

Keep Working Backups:
  1. Before integration: git commit "Pre-tone-adapter integration"
  2. Or: cp agent.py agent.py.backup
  3. After integration: git commit "Tone adapter integrated"

Test in Sandbox First:
  1. Create: agent_test.py (copy of agent.py)
  2. Integrate ToneAdapter into agent_test.py only
  3. Test thoroughly
  4. Once working, integrate into agent.py
"""

# ═════════════════════════════════════════════════════════════════════════════
# FINAL SIGN-OFF
# ═════════════════════════════════════════════════════════════════════════════

SIGN_OFF = """
INTEGRATION SIGN-OFF

Date: ________________
Integrator: ________________

Pre-Integration Checks:
  □ All dependencies installed
  □ Ollama running and verified
  □ tone_adapter.py, test suite passing
  □ agent.py backed up

Integration Steps Completed:
  □ Imports added
  □ ToneAdapter initialized
  □ Chat method updated
  □ (Optional) Voice prosody added
  □ (Optional) History tracking added

Verification Completed:
  □ Syntax check passed
  □ Initialization test passed
  □ Single tone test passed
  □ Multiple tone test passed
  □ History test passed (if implemented)
  □ Logging test passed
  □ Performance test passed

Issues Encountered:
  (List any issues and how they were resolved)
  _________________________________________________
  _________________________________________________

Final Status: ✅ INTEGRATION COMPLETE

Notes:
  _________________________________________________
  _________________________________________________

Sign-off: _______________________________________
"""

# ═════════════════════════════════════════════════════════════════════════════
# PRINT CHECKLIST
# ═════════════════════════════════════════════════════════════════════════════

def print_section(title, content):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")
    print(content)

if __name__ == "__main__":
    import sys
    
    sections = {
        'pre': ('PRE-INTEGRATION CHECKLIST', PRE_INTEGRATION),
        'integration': ('INTEGRATION STEPS', INTEGRATION_STEPS),
        'verify': ('VERIFICATION CHECKLIST', VERIFICATION),
        'trouble': ('TROUBLESHOOTING', TROUBLESHOOTING),
        'rollback': ('ROLLBACK PLAN', ROLLBACK),
        'signoff': ('INTEGRATION SIGN-OFF', SIGN_OFF),
        'all': None,
    }
    
    if len(sys.argv) > 1:
        section = sys.argv[1].lower()
        if section in sections and section != 'all':
            title, content = sections[section]
            print_section(title, content)
        elif section == 'all':
            for key in ['pre', 'integration', 'verify', 'trouble', 'rollback', 'signoff']:
                title, content = sections[key]
                print_section(title, content)
        else:
            print("Usage: python TONE_ADAPTER_INTEGRATION_CHECKLIST.py [section]")
            print("\nAvailable sections:")
            for key in sections:
                if key != 'all':
                    print(f"  {key}")
    else:
        # Print all
        for key in ['pre', 'integration', 'verify', 'trouble', 'rollback', 'signoff']:
            title, content = sections[key]
            print_section(title, content)

print("""

╔════════════════════════════════════════════════════════════════╗
║    🧠 TONE ADAPTER INTEGRATION CHECKLIST - READY TO USE        ║
║                                                                ║
║ Print this document and use it to track integration progress   ║
║                                                                ║
║ Usage: python TONE_ADAPTER_INTEGRATION_CHECKLIST.py [section]  ║
║ Options: pre | integration | verify | trouble | rollback      ║
║          signoff | all                                         ║
╚════════════════════════════════════════════════════════════════╝
""")
