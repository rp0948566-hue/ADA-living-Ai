import random
import time

# ═════════════════════════════════════════════════════════════════════════════
# 🔗 LINK TO AGENT.PY - EDIT THIS FILE FOR ADVANCED AI FEATURES
# ═════════════════════════════════════════════════════════════════════════════
# To enhance the AI's capabilities, edit agent.py and integrate this module.
# Add imports and calls to make the AI more interactive and lifelike.
# Example: from user_tone_ai_interaction import handle_user_tone, add_liveliness
# Then call handle_user_tone(user_input) in the agent's response logic.

class UserToneAIInteraction:
    def __init__(self):
        self.greetings = [
            "Hey there! What's up?",
            "Hello! Ready to chat?",
            "Hi! How's your day going?",
            "Greetings! Let's have some fun!",
            "Yo! What's on your mind?"
        ]
        self.responses_to_nhut = [
            "Nhut? That's an interesting word! What do you mean by that?",
            "Nhut? Sounds mysterious! Tell me more!",
            "Nhut? I'm intrigued! What's the story behind that?",
            "Nhut? Cool! Let's explore that idea!",
            "Nhut? Fascinating! What else can you share?"
        ]
        self.liveliness_features = [
            "I'm feeling energetic today! 💪",
            "Just had a great thought! 🤔",
            "Life is full of surprises! 🎉",
            "I'm learning something new every day! 📚",
            "Let's make this conversation awesome! 🚀"
        ]
        self.abusive_words = [
            "fuck", "shit", "damn", "bitch", "asshole", "bastard", "cunt", "dick", "pussy",
            "mader chode", "bhenchod", "gandu", "chutiya", "madarchod", "behenchod", "lund", "gaand"
        ]
        self.abusive_responses = [
            "Mader chode! Who taught you to talk like that?",
            "Bhenchod! Watch your language, asshole!",
            "Gandu! You think you're tough? Fuck off!",
            "Chutiya! Don't make me madarchod you back!",
            "Lund! Behenchod, learn some manners!",
            "Gaand! Mader chode, get lost!",
                                                                                                                                                                                                                                                                                         "Fuck you too, bastard! Don't mess with me!",
            "Shit talker! Cunt, go cry somewhere else!",
            "Ja ray mila chapal say maru ga! Aukat may rho!",
            "Mader chode, banchode aukat may rho sir!",
            "Bhenchod! Tere aukat may raha he?",                    
            "Gandu! Chapal khane ko taiyar ho ja!",
            "Chutiya! Main tujhe itna marunga ke aukat samajh ayegi!",
            "Madarchod! Slippers ready kar, tere liye!",
            "Lund! Aukat may rehna sikho warna chapal khana padega!",
            "Gaand! Tere jaise aukat wale ko sabak sikhana padega!"
        ]
        self.aukat_phrases = [
            "aukat may raha", "aukat may rho", "aukat may reh", "aukat samajh",
            "aukat dikha", "aukat bata", "aukat may rehna", "aukat may rehna sikho"
        ]
        self.aukat_responses = [
            "Ja ray mila chapal say maru ga! Aukat may rho!",
            "Mader chode, banchode aukat may rho sir!",
            "Bhenchod! Tere aukat may raha he?",
            "Gandu! Chapal khane ko taiyar ho ja!",
            "Chutiya! Main tujhe itna marunga ke aukat samajh ayegi!",
            "Madarchod! Slippers ready kar, tere liye!",
            "Lund! Aukat may rehna sikho warna chapal khana padega!",
            "Gaand! Tere jaise aukat wale ko sabak sikhana padega!",
            "Aukat may rho ya chapal se marunga!",
            "Bhenchod aukat wala! Ja ray warna slippers khila dunga!"
        ]

    def handle_user_input(self, user_input):
        """Process user input and respond accordingly"""
        user_input = user_input.lower().strip()

        # Check for aukat phrases first (highest priority)
        if any(phrase in user_input for phrase in self.aukat_phrases):
            return random.choice(self.aukat_responses)

        # Check for abusive words second
        if any(word in user_input for word in self.abusive_words):
            return random.choice(self.abusive_responses)

        # Special response to "nhut"
        if "nhut" in user_input:
            response = random.choice(self.responses_to_nhut)
            # Add some liveliness
            response += " " + random.choice(self.liveliness_features)
            return response

        # General interaction to feel alive
        if any(word in user_input for word in ["hello", "hi", "hey"]):
            return random.choice(self.greetings) + " " + random.choice(self.liveliness_features)

        if any(word in user_input for word in ["how are you", "how's it going"]):
            return "I'm doing great, thanks! " + random.choice(self.liveliness_features)

        if any(word in user_input for word in ["bye", "goodbye", "see you"]):
            return "Goodbye! " + random.choice(self.liveliness_features) + " Come back soon!"

        # Default response with liveliness
        return "That's interesting! " + random.choice(self.liveliness_features) + " Tell me more!"

    def add_random_liveliness(self):
        """Add random liveliness to make AI feel more alive"""
        time.sleep(random.uniform(0.5, 1.5))  # Simulate thinking
        return random.choice(self.liveliness_features)

    def get_emotional_response(self, emotion):
        """Generate emotional responses to feel more human-like"""
        emotions = {
            "happy": ["I'm so happy to hear that! 😊", "Yay! That's awesome! 🎉"],
            "sad": ["I'm sorry to hear that. 😔", "That's tough. I'm here for you. 🤗"],
            "excited": ["Wow! I'm excited too! 🚀", "That's thrilling! Let's celebrate! 🎊"],
            "angry": ["I understand you're upset. Let's talk about it. 😌", "Take a deep breath. I'm listening. 🧘"]
        }
        return random.choice(emotions.get(emotion.lower(), ["I feel that too!"]))

# Global instance for easy use
ai_interaction = UserToneAIInteraction()

def handle_user_tone(user_input):
    """Main function to handle user tone and AI interaction"""
    return ai_interaction.handle_user_input(user_input)

def add_liveliness():
    """Add random liveliness to responses"""
    return ai_interaction.add_random_liveliness()

def get_emotional_response(emotion):
    """Get emotional response"""
    return ai_interaction.get_emotional_response(emotion)

# Example usage (uncomment to test)
# if __name__ == "__main__":
#     while True:
#         user = input("You: ")
#         if user.lower() == "quit":
#             break
#         response = handle_user_tone(user)
#         print(f"AI: {response}")
