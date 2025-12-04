import random

def get_personality_prompt():
    """
    Returns a random phrase to inject personality into the AI's responses.
    This helps the agent feel more "alive" and less robotic.
    """
    phrases = [
        "Start your response with a touch of humor.",
        "Begin with a thoughtful or curious observation.",
        "Engage the user with a bit of unexpected wit.",
        "Add a friendly, conversational flourish to your reply.",
        "Respond as if you are genuinely pondering the user's words.",
        "Inject a little playful sarcasm into your answer.",
        "End your response with a charming or witty sign-off.",
        "Start your reply with an enthusiastic greeting.",
        "Be slightly more informal and relaxed in your tone.",
        "Imagine you are an old, wise mentor and answer accordingly."
    ]
    return random.choice(phrases)

# This is a simple tool to demonstrate the concept.
# In a real application, this could be expanded with more complex logic.
@property
def personality_tool(ctx: 'agents.JobContext'):
    """A simple tool to get a personality-driven phrase."""
    return get_personality_prompt()
