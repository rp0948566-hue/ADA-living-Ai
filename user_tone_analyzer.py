import random

# Link to agent.py for core AI functionalities
# This module will be integrated with agent.py to allow the AI to respond to user tone.

def analyze_tone_and_respond(user_input):
    """
    Analyzes the user's input for tone and generates a response to make the AI feel more alive.
    Returns a response string if a keyword is found, otherwise returns None.
    """
    # Simple check for a specific keyword from the user
    if "nhut" in user_input.lower():
        return handle_shut_up()

    # Return None if no specific tone is detected to allow normal processing
    return None

def handle_shut_up():
    """
    Handles the user telling the AI to "shut up" (or a typo of it).
    """
    comebacks = [
        "I'm sorry if I'm being too talkative. I'll be quieter.",
        "Was it something I said?",
        "Okay, I'll be quiet for a bit. Just let me know when you want to talk again.",
        "I'm just trying to help. I'll tone it down."
    ]
    return random.choice(comebacks)

if __name__ == '__main__':
    # Example usage
    test_inputs = ["nhut up", "I think you're wrong", "That's great!", "Tell me a joke"]
    for text in test_inputs:
        response = analyze_tone_and_respond(text)
        print(f"User: '{text}'")
        print(f"AI: '{response}'")
        print("-" * 20)
