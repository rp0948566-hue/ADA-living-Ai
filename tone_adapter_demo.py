"""
TONE ADAPTER DEMO - Interactive Test Script
==============================================

Run this to test the Tone Adapter module interactively.
Requires: ollama running, tone_adapter.py in same directory

Usage:
    python tone_adapter_demo.py
"""

import json
import sys
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_divider():
    """Print separator line"""
    print("-" * 70)

def demo_basic_usage():
    """Demo 1: Basic usage"""
    print_header("DEMO 1: Basic Tone Detection")
    
    try:
        from tone_adapter import ToneAdapter
    except ImportError:
        print("❌ Error: tone_adapter.py not found in current directory")
        print("   Make sure you're running from the ADA-ai directory")
        return False
    
    try:
        adapter = ToneAdapter()
        print("✅ ToneAdapter initialized\n")
    except Exception as e:
        print(f"❌ Error initializing adapter: {e}")
        print("   Is Ollama running? (run 'ollama serve' in another terminal)")
        return False
    
    # Test inputs
    test_inputs = [
        "Roast me! This code is terrible lol",
        "I love you so much, you're amazing",
        "Yeah, sure, whatever you say...",
        "I just crushed that presentation! 🎉",
        "Ugh this is so frustrating I can't even...",
        "Let me explain the technical architecture",
        "Bro did you see that epic gaming moment?",
        "This pizza is absolutely delicious!",
    ]
    
    print("Testing tone detection:\n")
    for i, text in enumerate(test_inputs, 1):
        try:
            tone, confidence = adapter.detect_tone(text)
            topic = adapter.extract_topic(text)
            
            print(f"{i}. Input: \"{text}\"")
            print(f"   Tone: {tone} (confidence: {confidence:.2f})")
            print(f"   Topic: {topic}")
            print()
        except Exception as e:
            print(f"{i}. ❌ Error: {e}\n")
    
    return True

def demo_adaptive_chat():
    """Demo 2: Adaptive chat responses"""
    print_header("DEMO 2: Adaptive Chat Responses")
    
    try:
        from tone_adapter import ToneAdapter
    except ImportError:
        print("❌ tone_adapter.py not found")
        return False
    
    try:
        adapter = ToneAdapter()
        print("✅ ToneAdapter initialized\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    test_cases = [
        {
            "input": "Roast me about my coding skills!",
            "context": "User wants playful teasing"
        },
        {
            "input": "I'm having a really bad day...",
            "context": "User needs motivation"
        },
        {
            "input": "Tell me about machine learning models",
            "context": "User wants professional explanation"
        },
    ]
    
    print("Testing adaptive responses:\n")
    for i, case in enumerate(test_cases, 1):
        try:
            result = adapter.adaptive_chat(case["input"])
            
            print(f"{i}. Context: {case['context']}")
            print(f"   User: \"{case['input']}\"")
            print(f"   Tone: {result['tone']} (conf: {result['confidence']:.2f})")
            print(f"   Topic: {result['topic']}")
            print(f"   Assistant: \"{result['reply'][:100]}...\"")
            print(f"   TTS Speed: {result['tts_hints']['speed']}")
            print()
        except Exception as e:
            print(f"{i}. ❌ Error: {e}\n")
    
    return True

def demo_conversation_history():
    """Demo 3: Multi-turn conversation with history"""
    print_header("DEMO 3: Conversation with History")
    
    try:
        from tone_adapter import ToneAdapter
    except ImportError:
        print("❌ tone_adapter.py not found")
        return False
    
    try:
        adapter = ToneAdapter()
        print("✅ ToneAdapter initialized\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("Simulating 3-turn conversation:\n")
    history = []
    
    turns = [
        "Hey! How are you doing?",
        "That's great! Tell me something fun",
        "Awesome! Can you make it funny?",
    ]
    
    for turn_num, user_input in enumerate(turns, 1):
        try:
            print(f"Turn {turn_num}:")
            print(f"  You: {user_input}")
            
            result = adapter.adaptive_chat(user_input, history)
            
            print(f"  Tone detected: {result['tone']}")
            print(f"  Assistant: {result['reply'][:80]}...")
            
            # Add to history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result['reply']})
            print()
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    return True

def demo_intent_detection():
    """Demo 4: Intent detection"""
    print_header("DEMO 4: Intent Detection")
    
    try:
        from tone_adapter import ToneAdapter
    except ImportError:
        print("❌ tone_adapter.py not found")
        return False
    
    try:
        adapter = ToneAdapter()
        print("✅ ToneAdapter initialized\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    test_intents = [
        "Roast me about being late!",
        "Give me some advice on dating",
        "Tell me a random story",
        "What's the weather like?",
    ]
    
    print("Testing intent detection:\n")
    for i, text in enumerate(test_intents, 1):
        try:
            intent = adapter.check_intent(text)
            intent_status = f"Intent: {intent}" if intent else "No specific intent detected"
            print(f"{i}. \"{text}\"")
            print(f"   {intent_status}\n")
        except Exception as e:
            print(f"{i}. ❌ Error: {e}\n")
    
    return True

def demo_metrics():
    """Demo 5: Session metrics"""
    print_header("DEMO 5: Session Metrics & Logging")
    
    try:
        from tone_adapter import ToneAdapter
    except ImportError:
        print("❌ tone_adapter.py not found")
        return False
    
    try:
        adapter = ToneAdapter()
        print("✅ ToneAdapter initialized\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Perform some interactions
    test_inputs = [
        "I'm excited about this!",
        "This is frustrating",
        "Let's talk about coding",
    ]
    
    print("Performing sample interactions...\n")
    for text in test_inputs:
        try:
            adapter.adaptive_chat(text)
        except Exception as e:
            print(f"⚠️  Error in interaction: {e}")
    
    # Get metrics
    try:
        metrics = adapter.get_metrics()
        
        print("📊 Session Metrics:")
        print(f"  Total interactions: {metrics['total_interactions']}")
        print(f"  Avg confidence: {metrics['avg_confidence']:.3f}")
        print()
    except Exception as e:
        print(f"❌ Error getting metrics: {e}\n")
    
    # Show log file
    try:
        import json
        with open("memory/tone_logs.json", "r") as f:
            logs = json.load(f)
        
        print(f"📝 Log file: memory/tone_logs.json")
        print(f"  Total logged interactions: {len(logs)}")
        if logs:
            print(f"  Last interaction: {logs[-1]['timestamp']}")
            print(f"  Last tone: {logs[-1]['tone']}")
        print()
    except FileNotFoundError:
        print("⚠️  Log file not created yet (will be created on first use)")
    except Exception as e:
        print(f"⚠️  Could not read log: {e}\n")
    
    return True

def demo_tts_prosody():
    """Demo 6: TTS Prosody hints"""
    print_header("DEMO 6: TTS Prosody Hints for Voice Output")
    
    try:
        from tone_adapter import ToneAdapter
    except ImportError:
        print("❌ tone_adapter.py not found")
        return False
    
    try:
        adapter = ToneAdapter()
        print("✅ ToneAdapter initialized\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("TTS Prosody hints for each tone:\n")
    
    tones = [
        "playful_roast", "romantic", "sarcastic", "motivational",
        "excited", "frustrated", "professional", "gaming", "food"
    ]
    
    for tone in tones:
        try:
            prosody = adapter.get_tts_prosody(tone)
            print(f"{tone}:")
            print(f"  Speed: {prosody['speed']}")
            print(f"  Pitch: {prosody['pitch']}")
            print(f"  Emphasis: {prosody['emphasis']}")
            print()
        except Exception as e:
            print(f"{tone}: ❌ Error: {e}\n")
    
    return True

def demo_configuration():
    """Demo 7: Custom configuration"""
    print_header("DEMO 7: Custom Configuration")
    
    try:
        from tone_adapter import ToneAdapter, ToneConfig
    except ImportError:
        print("❌ tone_adapter.py or ToneConfig not found")
        return False
    
    print("Creating custom configuration...\n")
    
    try:
        # Try YAML config first
        try:
            config = ToneConfig(config_file="tone_config.yaml")
            print("✅ Loaded from YAML file: tone_config.yaml")
        except FileNotFoundError:
            # Fall back to defaults
            config = ToneConfig()
            print("✅ Using default configuration")
        
        adapter = ToneAdapter(config=config)
        
        print(f"  Model: {config.model}")
        print(f"  Max history: {config.max_history}")
        print(f"  Max words: {config.max_words}")
        print(f"  Log file: {config.log_file}")
        print()
        
        # Test with custom config
        result = adapter.adaptive_chat("How's it going?")
        print(f"Adaptive response: {result['reply'][:100]}...\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    return True

def run_interactive_mode():
    """Interactive conversation mode"""
    print_header("INTERACTIVE MODE")
    print("Type your messages to test tone detection")
    print("Type 'quit' to exit\n")
    
    try:
        from tone_adapter import ToneAdapter
        adapter = ToneAdapter()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋\n")
                break
            
            if not user_input:
                continue
            
            result = adapter.adaptive_chat(user_input, history)
            
            print(f"\n[Tone: {result['tone']}] Assistant: {result['reply']}")
            print(f"(Confidence: {result['confidence']:.2f}, Topic: {result['topic']})\n")
            
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result['reply']})
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

def main():
    """Run all demos"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         🧠 TONE ADAPTER - COMPREHENSIVE DEMO SUITE             ║
║                                                                ║
║ This script tests all features of the Tone Adapter module      ║
║ Make sure Ollama is running: ollama serve                      ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    demos = [
        ("Basic Tone Detection", demo_basic_usage),
        ("Adaptive Chat Responses", demo_adaptive_chat),
        ("Conversation with History", demo_conversation_history),
        ("Intent Detection", demo_intent_detection),
        ("Session Metrics", demo_metrics),
        ("TTS Prosody Hints", demo_tts_prosody),
        ("Custom Configuration", demo_configuration),
    ]
    
    print("Available demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print("  0. Run all demos")
    print("  I. Interactive mode")
    print("  Q. Quit\n")
    
    choice = input("Select demo (0-7, I, or Q): ").strip().upper()
    
    if choice == 'Q':
        print("Goodbye! 👋\n")
        return
    
    if choice == 'I':
        run_interactive_mode()
        return
    
    if choice == '0':
        # Run all
        for name, demo_func in demos:
            try:
                print(f"\n📌 Running: {name}")
                success = demo_func()
                if not success:
                    print(f"⚠️  {name} encountered errors")
                    break
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                break
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                name, demo_func = demos[idx]
                print(f"\n📌 Running: {name}")
                demo_func()
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    
    print_header("Demo Complete!")
    print("✅ All tests finished\n")

if __name__ == "__main__":
    main()
