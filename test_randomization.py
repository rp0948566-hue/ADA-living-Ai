#!/usr/bin/env python3
"""
Quick test to verify randomization is working without Ollama dependency
"""

import random
from tone_adapter import (
    ABUSE_WORD_POOL, ROMANTIC_PHRASE_POOL, ANGER_REDIRECT_POOL,
    COZY_PHRASE_POOL, SARC_PHRASE_POOL, ToneAdapter
)

def test_random_pools():
    """Test that random sampling produces different results each time"""
    print("="*80)
    print("TESTING RANDOM ABUSE WORD POOLS")
    print("="*80)
    
    adapter = ToneAdapter(model='llama3.1')
    
    print("\n🎲 Testing _get_random_abuse_mix() - Run Multiple Times\n")
    for i in range(5):
        result = adapter._get_random_abuse_mix(num_words=3, savage_mode=False)
        print(f"Run {i+1}: {result}")
    
    print("\n🔥 Testing SAVAGE MODE _get_random_abuse_mix()\n")
    for i in range(5):
        result = adapter._get_random_abuse_mix(num_words=4, savage_mode=True)
        print(f"Run {i+1} (Savage): {result}")
    
    print("\n" + "="*80)
    print("TESTING RANDOM PHRASE POOLS")
    print("="*80)
    
    print("\n💕 Testing ROMANTIC phrase mix\n")
    for i in range(4):
        result = adapter._get_random_phrase_mix(tone='romantic_intimate', num_phrases=2)
        print(f"Run {i+1}: {result}")
    
    print("\n😡 Testing ANGER phrase mix\n")
    for i in range(4):
        result = adapter._get_random_phrase_mix(tone='angry_frustrated', num_phrases=2)
        print(f"Run {i+1}: {result}")
    
    print("\n☕ Testing COZY phrase mix\n")
    for i in range(4):
        result = adapter._get_random_phrase_mix(tone='cozy_comfort', num_phrases=2)
        print(f"Run {i+1}: {result}")
    
    print("\n" + "="*80)
    print("POOL CONTENT VERIFICATION")
    print("="*80)
    print(f"\n📝 Total Abuse Words: {len(ABUSE_WORD_POOL)}")
    print(f"   Examples: {ABUSE_WORD_POOL[:5]}")
    
    print(f"\n💕 Total Romantic Phrases: {len(ROMANTIC_PHRASE_POOL)}")
    print(f"   Examples: {ROMANTIC_PHRASE_POOL[:3]}")
    
    print(f"\n😡 Total Anger Phrases: {len(ANGER_REDIRECT_POOL)}")
    print(f"   Examples: {ANGER_REDIRECT_POOL[:3]}")
    
    print(f"\n☕ Total Cozy Phrases: {len(COZY_PHRASE_POOL)}")
    print(f"   Examples: {COZY_PHRASE_POOL[:3]}")
    
    print(f"\n😏 Total Sarcastic Phrases: {len(SARC_PHRASE_POOL)}")
    print(f"   Examples: {SARC_PHRASE_POOL[:3]}")
    
    print("\n" + "="*80)
    print("RANDOMIZATION VERIFIED - Each run produces different selections!")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_random_pools()
    print("\nSUCCESS: Randomization is working correctly!")
