#!/usr/bin/env python3
"""
Test script for user_tone_ai_interaction.py module
Tests abusive language detection and aukat phrase responses
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_tone_ai_interaction import handle_user_tone

def test_abusive_words():
    """Test detection of abusive words"""
    print("🧪 Testing Abusive Word Detection...")

    abusive_inputs = [
        "fuck you",
        "shit talker",
        "mader chode",
        "bhenchod asshole",
        "gandu chutiya",
        "madarchod lund",
        "behenchod gaand"
    ]

    for input_text in abusive_inputs:
        response = handle_user_tone(input_text)
        print(f"Input: '{input_text}' -> Response: '{response}'")
        # Check if response contains abusive elements or threat elements
        assert any(word in response.lower() for word in ["mader chode", "bhenchod", "gandu", "chutiya", "madarchod", "lund", "gaand", "fuck", "shit", "asshole", "bastard", "cunt", "chapal", "maru", "marunga", "aukat"]), f"Expected abusive response for '{input_text}', got '{response}'"

    print("✅ Abusive word detection tests passed!\n")

def test_aukat_phrases():
    """Test detection of aukat phrases"""
    print("🧪 Testing Aukat Phrase Detection...")

    aukat_inputs = [
        "aukat may raha",
        "aukat may rho",
        "aukat may reh",
        "aukat samajh",
        "aukat dikha",
        "aukat bata",
        "aukat may rehna",
        "aukat may rehna sikho"
    ]

    for input_text in aukat_inputs:
        response = handle_user_tone(input_text)
        print(f"Input: '{input_text}' -> Response: '{response}'")
        # Check if response contains aukat or abusive elements
        assert any(word in response.lower() for word in ["aukat", "chapal", "maru", "marunga", "mader chode", "bhenchod", "gandu"]), f"Expected aukat response for '{input_text}', got '{response}'"

    print("✅ Aukat phrase detection tests passed!\n")

def test_normal_interactions():
    """Test normal conversation responses"""
    print("🧪 Testing Normal Conversation Responses...")

    normal_inputs = [
        "hello",
        "hi there",
        "how are you",
        "goodbye",
        "bye",
        "nhut"
    ]

    for input_text in normal_inputs:
        response = handle_user_tone(input_text)
        print(f"Input: '{input_text}' -> Response: '{response}'")
        # Ensure no abusive content in normal responses
        assert not any(word in response.lower() for word in ["mader chode", "bhenchod", "gandu", "chutiya", "madarchod", "lund", "gaand", "fuck", "shit", "asshole"]), f"Unexpected abusive content in normal response for '{input_text}': '{response}'"

    print("✅ Normal conversation tests passed!\n")

def test_random_variation():
    """Test that responses vary randomly"""
    print("🧪 Testing Random Response Variation...")

    test_input = "fuck you"
    responses = set()

    # Get multiple responses to check variation
    for _ in range(10):
        response = handle_user_tone(test_input)
        responses.add(response)

    print(f"Collected {len(responses)} unique responses for '{test_input}':")
    for resp in responses:
        print(f"  - '{resp}'")

    # Should have some variation (at least 3 different responses)
    assert len(responses) >= 3, f"Expected at least 3 different responses, got {len(responses)}"

    print("✅ Random variation tests passed!\n")

def test_edge_cases():
    """Test edge cases"""
    print("🧪 Testing Edge Cases...")

    edge_cases = [
        "",  # Empty string
        "   ",  # Whitespace only
        "AUKAT MAY RAHA",  # Uppercase
        "FuCk YoU",  # Mixed case
        "hello fuck you",  # Mixed normal and abusive
        "aukat may raha fuck",  # Mixed aukat and abusive
    ]

    for input_text in edge_cases:
        try:
            response = handle_user_tone(input_text)
            print(f"Input: '{input_text}' -> Response: '{response}'")
        except Exception as e:
            print(f"Input: '{input_text}' -> Error: {e}")
            raise

    print("✅ Edge case tests passed!\n")

def run_all_tests():
    """Run all test functions"""
    print("🚀 Starting Comprehensive Testing of user_tone_ai_interaction.py\n")

    try:
        test_abusive_words()
        test_aukat_phrases()
        test_normal_interactions()
        test_random_variation()
        test_edge_cases()

        print("🎉 All tests passed successfully!")
        print("✅ The abusive language and aukat response features are working correctly.")

    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
