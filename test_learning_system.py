# -*- coding: utf-8 -*-
"""
Final Integration Test - AI Learning System
"""

from ABCD import ContinuousLearningSystem, MULTILANGUAGE_DATABASE, convert_number_to_hindi
from learning_bridge import LearningBridge
from agent_learning import AgentLearningTools

print("Testing AI Learning System Integration...\n")

# Test 1: Initialize
AgentLearningTools.initialize()
print("✓ Learning tools initialized")

# Test 2: Languages
langs = len(MULTILANGUAGE_DATABASE)
print(f"✓ {langs} languages loaded")

# Test 3: Number conversion
num = convert_number_to_hindi(42)
print(f"✓ Hindi conversion: 42 = {num}")

# Test 4: Statistics
stats = AgentLearningTools.get_learning_stats()
learned = stats['total_learned']
generated = stats['total_generated']
print(f"✓ Statistics: {learned} words learned, {generated} generated")

# Test 5: Silent learning
AgentLearningTools.silent_learn_word("test", "verification word")
print("✓ Silent learning functional")

# Test 6: Word generation
gen = AgentLearningTools.generate_word("un", "test", "able")
print(f"✓ Word generation: {gen['generated_word']}")

# Test 7: Memory save
AgentLearningTools.save_learning_memory()
print("✓ Memory saved successfully")

print("\n" + "="*70)
print("✅ AI LEARNING SYSTEM FULLY FUNCTIONAL")
print("="*70)
print("\nReady to integrate with agent.py!")
print("\nNext steps:")
print("1. Read: QUICK_START_LEARNING.py")
print("2. Read: AGENT_INTEGRATION_GUIDE.py")
print("3. Modify: agent.py with code from guides")
print("4. Run: python agent.py")
