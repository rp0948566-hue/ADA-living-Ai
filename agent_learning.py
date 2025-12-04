"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  AGENT LEARNING INTEGRATION MODULE                           ║
║              Seamless integration of learning_bridge with agent.py            ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides functions and utilities for agent.py to:
  ✓ Automatically learn from interactions
  ✓ Generate new words silently
  ✓ Expand knowledge base continuously
  ✓ Access multi-language resources
  ✓ Convert between number systems
  ✓ Break down and analyze words
  ✓ Save learning to persistent memory
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Import learning bridge components
try:
    from learning_bridge import (
        initialize_learning_bridge,
        get_learning_bridge,
        get_agent_interface,
        AgentLearningInterface,
        LearningBridge
    )
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    print("⚠️ Warning: Learning bridge not available")

# Import ABCD components
try:
    from ABCD import (
        WordBreaker,
        MULTILANGUAGE_DATABASE,
        GRAMMAR_RULES,
        COLORS,
        SPELLING_RULES
    )
    ABCD_AVAILABLE = True
except ImportError:
    ABCD_AVAILABLE = False
    print("⚠️ Warning: ABCD module not available")

# ============================================================================
# AGENT LEARNING UTILITIES
# ============================================================================

class AgentLearningTools:
    """
    Collection of tools for agent to use learning system
    All methods work silently in background
    """
    
    _interface = None
    _bridge = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize learning tools once"""
        if not cls._initialized and BRIDGE_AVAILABLE:
            cls._interface = get_agent_interface()
            cls._bridge = get_learning_bridge()
            cls._initialized = True
            return True
        return False
    
    @classmethod
    def silent_learn_word(cls, word, meaning, language="english"):
        """
        Learn a word silently (no output)
        Called during agent interactions
        """
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            return cls._interface.agent_learn(word, meaning, language)
        return False
    
    @classmethod
    def silent_learn_batch(cls, words_list):
        """
        Silently learn multiple words at once
        Each item: {"word": str, "meaning": str, "language": str}
        """
        if not cls._initialized:
            cls.initialize()
        
        count = 0
        for item in words_list:
            if cls._interface:
                cls._interface.agent_learn(
                    item.get("word", ""),
                    item.get("meaning", ""),
                    item.get("language", "english")
                )
                count += 1
        
        return count
    
    @classmethod
    def generate_word(cls, prefix, root, suffix):
        """Generate a new word from components"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            return cls._interface.agent_generate(prefix, root, suffix)
        return None
    
    @classmethod
    def get_word_family(cls, word):
        """Get all related words and variations"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            return cls._interface.agent_get_word_family(word)
        return None
    
    @classmethod
    def break_word(cls, word):
        """Break word into components (prefix-root-suffix)"""
        if ABCD_AVAILABLE:
            return WordBreaker.break_word(word)
        return None
    
    @classmethod
    def number_to_hindi(cls, number):
        """Convert number to Hindi text"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            return cls._interface.agent_convert_to_hindi(number)
        return None
    
    @classmethod
    def get_language_data(cls, language_code):
        """Get complete data for a language"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            return cls._interface.agent_get_language_data(language_code)
        return None
    
    @classmethod
    def get_learning_stats(cls):
        """Get current learning statistics"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            return cls._interface.agent_get_stats()
        return None
    
    @classmethod
    def save_learning_memory(cls):
        """Save all learning to persistent memory"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._interface:
            cls._interface.agent_save_memory()
            return True
        return False
    
    @classmethod
    def start_background_learning(cls):
        """Start continuous silent learning in background"""
        if not cls._initialized:
            cls.initialize()
        
        if cls._bridge:
            return cls._bridge.start_background_learning()
        return None

# ============================================================================
# SPECIALIZED AGENT LEARNING FUNCTIONS
# ============================================================================

def agent_learn_from_conversation(user_input, ai_response):
    """
    Agent learns from each conversation exchange
    Extracts key words and meanings
    """
    if not BRIDGE_AVAILABLE:
        return
    
    # Extract potential new words from user input
    words = user_input.split()
    for word in words:
        if len(word) > 3:  # Only learn words longer than 3 chars
            AgentLearningTools.silent_learn_word(word, f"From user: {user_input[:50]}")
    
    # Extract from AI response
    words = ai_response.split()
    for word in words:
        if len(word) > 3:
            AgentLearningTools.silent_learn_word(word, f"AI used: {ai_response[:50]}")

def agent_learn_from_screen_text(text_on_screen):
    """
    Agent learns from text visible on screen
    Silent absorption of vocabulary
    """
    if not BRIDGE_AVAILABLE:
        return
    
    # Split and filter
    words = text_on_screen.split()[:100]  # Limit to first 100 words
    
    batch = []
    for word in words:
        if len(word) > 2 and word.isalpha():
            batch.append({
                "word": word,
                "meaning": "From screen",
                "language": "english"
            })
    
    if batch:
        AgentLearningTools.silent_learn_batch(batch)

def agent_learn_from_search_results(search_results):
    """
    Agent learns from Google search results
    Extracts words, meanings, and context
    """
    if not BRIDGE_AVAILABLE:
        return
    
    batch = []
    
    if isinstance(search_results, dict):
        for result in search_results.get("results", [])[:10]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            # Extract key words from title
            for word in title.split()[:5]:
                if len(word) > 3 and word.isalpha():
                    batch.append({
                        "word": word,
                        "meaning": snippet[:50],
                        "language": "english"
                    })
    
    if batch:
        AgentLearningTools.silent_learn_batch(batch)

def agent_expand_with_multilanguage(base_word):
    """
    Expand knowledge by learning same word in multiple languages
    """
    if not BRIDGE_AVAILABLE:
        return
    
    bridge = get_learning_bridge()
    if bridge and bridge.learning_system:
        # Learn word with language variants
        languages = ["english", "hindi", "spanish", "french", "german"]
        for lang in languages:
            lang_data = AgentLearningTools.get_language_data(lang)
            if lang_data and lang_data.get("common_words"):
                # Find similar word and learn variant
                for word_data in lang_data["common_words"]:
                    AgentLearningTools.silent_learn_word(
                        base_word,
                        f"Language variant: {lang}",
                        lang
                    )

def agent_continuous_expansion():
    """
    Agent continuously expands knowledge base
    Called periodically during operation
    """
    if not BRIDGE_AVAILABLE:
        return
    
    bridge = get_learning_bridge()
    if bridge:
        # Generate new words
        generated = bridge.generate_new_words_batch(20)
        
        # Save progress
        bridge.save_learning_memory()
        
        return {"generated": len(generated), "status": "expanded"}

def agent_get_smart_response_data(query):
    """
    Agent gets smart response data from learning system
    Combines ABCD knowledge with learned words
    """
    if not BRIDGE_AVAILABLE:
        return {}
    
    response_data = {
        "query": query,
        "learned_context": [],
        "word_variants": [],
        "language_translations": []
    }
    
    # Get word family if query is a word
    family = AgentLearningTools.get_word_family(query)
    if family:
        response_data["word_variants"] = family.get("related", [])
    
    # Get language data
    for lang_code in ["hindi", "spanish", "french"]:
        lang_data = AgentLearningTools.get_language_data(lang_code)
        if lang_data:
            response_data["language_translations"].append({
                "language": lang_code,
                "data": lang_data
            })
    
    return response_data

# ============================================================================
# INTEGRATION WITH AGENT SESSION
# ============================================================================

def integrate_learning_with_agent_session(agent_session):
    """
    Integrate learning system with agent session
    Called when agent starts
    """
    if not BRIDGE_AVAILABLE:
        return None
    
    # Initialize learning tools
    AgentLearningTools.initialize()
    
    # Start background learning
    learning_thread = AgentLearningTools.start_background_learning()
    
    # Add learning metadata to session
    agent_session.learning_enabled = True
    agent_session.learning_thread = learning_thread
    
    return learning_thread

def save_agent_learning_session(agent_session):
    """Save learning from current agent session"""
    if not BRIDGE_AVAILABLE:
        return False
    
    AgentLearningTools.save_learning_memory()
    return True

# ============================================================================
# HOOK FUNCTIONS FOR AGENT.PY
# ============================================================================

def pre_conversation_hook(message):
    """
    Called before agent processes user message
    Learn from user input
    """
    agent_learn_from_conversation(message, "")

def post_conversation_hook(user_input, ai_response):
    """
    Called after agent generates response
    Learn from both input and output
    """
    agent_learn_from_conversation(user_input, ai_response)
    
    # Periodically save
    import random
    if random.random() < 0.1:  # 10% chance
        AgentLearningTools.save_learning_memory()

def on_screen_update_hook(screen_text):
    """
    Called when screen changes
    Learn from visible text
    """
    agent_learn_from_screen_text(screen_text)

def on_search_hook(search_results):
    """
    Called after search results
    Learn from search data
    """
    agent_learn_from_search_results(search_results)

# ============================================================================
# DEMONSTRATION
# ============================================================================

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║          AGENT LEARNING INTEGRATION MODULE DEMO                ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Initialize
    print("1️⃣ Initializing learning tools...")
    AgentLearningTools.initialize()
    
    # Silent learning
    print("2️⃣ Silent word learning...")
    test_words = [
        {"word": "algorithm", "meaning": "Step-by-step procedure", "language": "english"},
        {"word": "machine", "meaning": "Device for doing work", "language": "english"},
        {"word": "intelligência", "meaning": "Capacity to understand", "language": "portuguese"}
    ]
    learned = AgentLearningTools.silent_learn_batch(test_words)
    print(f"   ✓ Learned {learned} words silently")
    
    # Word generation
    print("3️⃣ Generating new words...")
    generated = AgentLearningTools.generate_word("un", "think", "able")
    if generated:
        print(f"   Generated: {generated['generated_word']}")
    
    # Word breaking
    print("4️⃣ Breaking down words...")
    broken = AgentLearningTools.break_word("unhappiness")
    if broken:
        print(f"   Structure: {broken['structure']}")
    
    # Number conversion
    print("5️⃣ Converting numbers...")
    hindi_num = AgentLearningTools.number_to_hindi(42)
    print(f"   42 in Hindi: {hindi_num}")
    
    # Get stats
    print("6️⃣ Learning statistics...")
    stats = AgentLearningTools.get_learning_stats()
    if stats:
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    # Save memory
    print("7️⃣ Saving learning memory...")
    saved = AgentLearningTools.save_learning_memory()
    print(f"   {'✓ Saved' if saved else '✗ Failed to save'}")
    
    print("\n" + "=" * 70)
    print("✅ AGENT LEARNING INTEGRATION READY")
    print("=" * 70)
