"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              LEARNING BRIDGE - ABCD.py ↔ agent.py INTEGRATION                ║
║              Continuous Auto-Learning System with Silent Mode                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module creates a bidirectional bridge between:
  • ABCD.py (Knowledge Base) - Contains all learning data
  • agent.py (AI Agent) - Learns, generates, and expands knowledge
  
Features:
  ✓ Continuous background learning
  ✓ Silent word acquisition (no output)
  ✓ Automatic word generation from patterns
  ✓ Memory persistence and recall
  ✓ Multi-language support
  ✓ Real-time knowledge expansion
"""

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path

# Import ABCD learning components
try:
    from ABCD import (
        ContinuousLearningSystem,
        WordBreaker,
        MULTILANGUAGE_DATABASE,
        HINDI_NUMBER_SYSTEM,
        convert_number_to_hindi,
        GRAMMAR_RULES,
        COLORS,
        SPELLING_RULES,
        HINDI_ENGLISH_BRIDGE,
        NUMBERS_DATABASE,
        HINDI_DEVANAGARI,
        ENGLISH_ALPHABET
    )
except ImportError as e:
    print(f"⚠️ Warning: Could not import ABCD components: {e}")
    ContinuousLearningSystem = None

# ============================================================================
# LEARNING BRIDGE CONFIGURATION
# ============================================================================

LEARNING_CONFIG = {
    "AUTO_LEARN": True,
    "SILENT_MODE": True,
    "BATCH_SIZE": 50,
    "SAVE_INTERVAL": 60,  # seconds
    "MEMORY_FILE": "memory/learning_database.json",
    "ENABLED_LANGUAGES": ["english", "hindi", "spanish", "french", "german"],
    "AUTO_EXPAND": True,
    "PATTERN_RECOGNITION": True
}

# ============================================================================
# LEARNING BRIDGE CLASS
# ============================================================================

class LearningBridge:
    """
    Central bridge connecting agent.py with ABCD.py knowledge base
    Handles continuous learning, word generation, and memory management
    """
    
    def __init__(self):
        """Initialize learning bridge with configuration"""
        self.learning_system = ContinuousLearningSystem() if ContinuousLearningSystem else None
        self.memory_file = LEARNING_CONFIG["MEMORY_FILE"]
        self.learning_queue = []
        self.generated_count = 0
        self.learned_count = 0
        self.is_running = False
        self.silent_mode = LEARNING_CONFIG["SILENT_MODE"]
        
        # Ensure memory directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Load existing learning data
        self.load_learning_memory()
    
    def load_learning_memory(self):
        """Load previously learned words from memory file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self.learning_system:
                        self.learned_count = data.get("total_learned", 0)
                        self.generated_count = data.get("total_generated", 0)
                        if not self.silent_mode:
                            print(f"✓ Loaded learning memory: {self.learned_count} words learned")
            except json.JSONDecodeError:
                if not self.silent_mode:
                    print("⚠️ Could not decode learning memory file")
    
    def save_learning_memory(self):
        """Save all learning data to persistent memory"""
        if self.learning_system:
            try:
                memory_data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_learned": self.learned_count,
                    "total_generated": self.generated_count,
                    "learned_words": self.learning_system.learned_words,
                    "generated_words": self.learning_system.generated_words[-100:],  # Keep last 100
                    "silence_words_count": len(self.learning_system.silence_words)
                }
                
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(memory_data, f, ensure_ascii=False, indent=2)
                
                if not self.silent_mode:
                    print(f"💾 Learning memory saved: {self.learned_count} words")
            except Exception as e:
                print(f"❌ Error saving learning memory: {e}")
    
    def inject_abcd_knowledge(self):
        """
        Inject all ABCD knowledge into learning system
        This happens silently in background
        """
        if not self.learning_system:
            return
        
        count = 0
        
        # Learn from English Alphabet
        for letter, data in ENGLISH_ALPHABET.get("uppercase", {}).items():
            self.learning_system.learn_new_word(
                letter,
                f"{data.get('example')} (letter {letter})",
                language="english",
                tags=["alphabet", "letter"]
            )
            count += 1
        
        # Learn from Numbers
        for num, data in NUMBERS_DATABASE.items():
            self.learning_system.learn_new_word(
                str(num),
                data.get("english", ""),
                language="english",
                tags=["number"]
            )
            count += 1
        
        # Learn from Hindi Devanagari
        for char, data in HINDI_DEVANAGARI.get("vowels", {}).items():
            self.learning_system.learn_new_word(
                char,
                data.get("english", ""),
                language="hindi",
                tags=["devanagari", "vowel"]
            )
            count += 1
        
        # Learn from Grammar Rules
        for pos, data in GRAMMAR_RULES.get("parts_of_speech", {}).items():
            for example in data.get("examples", []):
                self.learning_system.learn_new_word(
                    example,
                    f"Example of {pos}",
                    language="english",
                    tags=["grammar", pos]
                )
                count += 1
        
        # Learn from Colors
        for color_type, colors in COLORS.items():
            for color_name, color_data in colors.items():
                self.learning_system.learn_new_word(
                    color_data.get("english", ""),
                    color_data.get("tone", ""),
                    language="english",
                    tags=["color"]
                )
                count += 1
        
        # Learn from Hindi-English Bridge
        for word_pair in HINDI_ENGLISH_BRIDGE.get("common_words", []):
            self.learning_system.learn_new_word(
                word_pair.get("english", ""),
                word_pair.get("hindi", ""),
                language="english",
                tags=["bilingual", "common"]
            )
            count += 1
        
        self.learned_count += count
        if not self.silent_mode:
            print(f"✓ Injected {count} knowledge entries from ABCD")
    
    def learn_from_agent_context(self, context_data):
        """
        Agent reads environment and learns from context
        Silently absorbs new words, meanings, and patterns
        """
        if not self.learning_system:
            return
        
        if isinstance(context_data, dict):
            for key, value in context_data.items():
                if isinstance(value, str):
                    self.learning_system.learn_new_word(
                        key,
                        value,
                        language="english"
                    )
                    self.learning_system.add_silent_word(key)
                    self.learned_count += 1
        
        return {"learned_items": len(context_data), "status": "silent_learning"}
    
    def generate_new_words_batch(self, count=50):
        """
        Generate new words from learned patterns
        Uses prefix-root-suffix combinations
        """
        if not self.learning_system:
            return
        
        generated_batch = []
        prefixes = ["un", "re", "dis", "mis", "over", "under", "pre"]
        suffixes = ["ing", "ed", "er", "est", "ly", "ness", "ment"]
        roots = list(self.learning_system.learned_words.keys())[:20]
        
        if not roots:
            roots = ["happy", "run", "play", "make", "break", "like", "love"]
        
        for i in range(count):
            prefix = prefixes[i % len(prefixes)] if i % 3 == 0 else None
            suffix = suffixes[i % len(suffixes)] if i % 3 != 0 else None
            root = roots[i % len(roots)]
            
            generated = self.learning_system.generate_new_word(
                prefix or "",
                root,
                suffix or ""
            )
            generated_batch.append(generated)
            self.generated_count += 1
        
        if not self.silent_mode:
            print(f"✓ Generated {len(generated_batch)} new words")
        
        return generated_batch
    
    def continuous_learning_loop(self, duration=None):
        """
        Run continuous background learning loop
        Can run indefinitely or for specified duration (seconds)
        """
        if not self.learning_system:
            return
        
        self.is_running = True
        start_time = time.time()
        
        if not self.silent_mode:
            print("🔄 Starting continuous learning loop (SILENT MODE)")
        
        # Initial knowledge injection
        self.inject_abcd_knowledge()
        
        cycle = 0
        try:
            while self.is_running:
                cycle += 1
                
                # Save learning memory periodically
                if cycle % 5 == 0:
                    self.save_learning_memory()
                
                # Generate new words periodically
                if cycle % 3 == 0:
                    self.generate_new_words_batch(LEARNING_CONFIG["BATCH_SIZE"])
                
                # Process learning queue
                if self.learning_queue:
                    batch = self.learning_queue[:LEARNING_CONFIG["BATCH_SIZE"]]
                    self.learning_system.continuous_expand(batch)
                    self.learning_queue = self.learning_queue[LEARNING_CONFIG["BATCH_SIZE"]:]
                
                # Check duration
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Sleep to prevent CPU overload
                time.sleep(1)
        
        except KeyboardInterrupt:
            if not self.silent_mode:
                print("\n⏹️ Learning loop interrupted")
        
        finally:
            self.is_running = False
            self.save_learning_memory()
            if not self.silent_mode:
                print(f"📊 Final stats: {self.learned_count} learned, {self.generated_count} generated")
    
    def start_background_learning(self):
        """Start learning in background thread"""
        if not self.learning_system:
            return None
        
        thread = threading.Thread(target=self.continuous_learning_loop, daemon=True)
        thread.start()
        
        if not self.silent_mode:
            print("🚀 Background learning thread started")
        
        return thread
    
    def get_random_learned_word(self):
        """Get random word from learned vocabulary"""
        if self.learning_system and self.learning_system.learned_words:
            import random
            word = random.choice(list(self.learning_system.learned_words.keys()))
            return {
                "word": word,
                "data": self.learning_system.learned_words[word]
            }
        return None
    
    def get_stats(self):
        """Get learning statistics"""
        return {
            "total_learned": self.learned_count,
            "total_generated": self.generated_count,
            "learning_system_active": self.learning_system is not None,
            "running": self.is_running,
            "silent_words": len(self.learning_system.silence_words) if self.learning_system else 0
        }
    
    def add_to_learning_queue(self, items):
        """Add items to learning queue for processing"""
        if isinstance(items, list):
            self.learning_queue.extend(items)
        elif isinstance(items, dict):
            self.learning_queue.append(items)
        return len(self.learning_queue)
    
    def generate_multilingual_mapping(self):
        """
        Generate mapping of words across multiple languages
        Helps AI understand language relationships
        """
        mapping = {}
        
        for lang_code, lang_data in MULTILANGUAGE_DATABASE.items():
            mapping[lang_code] = {
                "language": lang_data.get("language", ""),
                "native_name": lang_data.get("native_name", ""),
                "alphabet": lang_data.get("alphabet", []),
                "numbers": lang_data.get("numbers", {}),
                "common_words": lang_data.get("common_words", [])
            }
        
        return mapping
    
    def convert_numbers_to_hindi(self, numbers_list):
        """Convert multiple numbers to Hindi"""
        return {num: convert_number_to_hindi(num) for num in numbers_list}

# ============================================================================
# AGENT INTEGRATION HELPER
# ============================================================================

class AgentLearningInterface:
    """
    Interface for agent.py to use learning system
    Simple API for agent to learn and generate words
    """
    
    def __init__(self):
        self.bridge = LearningBridge()
        self.bridge.silent_mode = True  # Always silent by default
    
    def agent_learn(self, word, meaning, language="english"):
        """Agent learns a new word silently"""
        if self.bridge.learning_system:
            self.bridge.learning_system.learn_new_word(word, meaning, language)
            self.bridge.learned_count += 1
            return True
        return False
    
    def agent_generate(self, prefix, root, suffix):
        """Agent generates a new word"""
        if self.bridge.learning_system:
            return self.bridge.learning_system.generate_new_word(prefix, root, suffix)
        return None
    
    def agent_get_word_family(self, word):
        """Agent retrieves word family"""
        if self.bridge.learning_system:
            return self.bridge.learning_system.get_word_family(word)
        return None
    
    def agent_convert_to_hindi(self, number):
        """Agent converts number to Hindi"""
        return convert_number_to_hindi(number)
    
    def agent_get_language_data(self, language_code):
        """Agent gets data for specific language"""
        return MULTILANGUAGE_DATABASE.get(language_code, {})
    
    def agent_get_stats(self):
        """Agent gets learning statistics"""
        return self.bridge.get_stats()
    
    def agent_save_memory(self):
        """Agent saves learning to permanent memory"""
        self.bridge.save_learning_memory()
    
    def start_silent_learning(self):
        """Start silent continuous learning"""
        return self.bridge.start_background_learning()

# ============================================================================
# INITIALIZATION
# ============================================================================

# Create global learning bridge instance
global_learning_bridge = None

def initialize_learning_bridge(silent=True):
    """Initialize global learning bridge"""
    global global_learning_bridge
    
    if global_learning_bridge is None:
        global_learning_bridge = LearningBridge()
        global_learning_bridge.silent_mode = silent
        
        if not silent:
            print("✓ Learning bridge initialized")
    
    return global_learning_bridge

def get_learning_bridge():
    """Get global learning bridge instance"""
    global global_learning_bridge
    
    if global_learning_bridge is None:
        global_learning_bridge = initialize_learning_bridge(silent=True)
    
    return global_learning_bridge

def get_agent_interface():
    """Get agent learning interface"""
    return AgentLearningInterface()

# ============================================================================
# STANDALONE DEMO
# ============================================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          LEARNING BRIDGE - ABCD.py ↔ agent.py                  ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Initialize bridge
    bridge = initialize_learning_bridge(silent=False)
    
    print("\n1️⃣  INJECTING ABCD KNOWLEDGE...")
    bridge.inject_abcd_knowledge()
    
    print("\n2️⃣  GENERATING NEW WORDS...")
    generated = bridge.generate_new_words_batch(10)
    for word in generated[:5]:
        print(f"   Generated: {word['generated_word']}")
    
    print("\n3️⃣  LEARNING FROM CONTEXT...")
    context = {
        "python": "Programming language",
        "code": "Written instructions",
        "learn": "Acquire knowledge"
    }
    bridge.learn_from_agent_context(context)
    
    print("\n4️⃣  MULTI-LANGUAGE MAPPING...")
    mapping = bridge.generate_multilingual_mapping()
    print(f"   Supported languages: {len(mapping)}")
    
    print("\n5️⃣  HINDI NUMBER CONVERSION...")
    numbers = [1, 10, 25, 50, 100]
    hindi_nums = bridge.convert_numbers_to_hindi(numbers)
    for num, hindi in hindi_nums.items():
        print(f"   {num:3d} = {hindi}")
    
    print("\n6️⃣  LEARNING STATISTICS...")
    stats = bridge.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n7️⃣  SAVING LEARNING MEMORY...")
    bridge.save_learning_memory()
    
    print("\n" + "=" * 70)
    print("✅ LEARNING BRIDGE READY FOR AGENT INTEGRATION")
    print("=" * 70)
