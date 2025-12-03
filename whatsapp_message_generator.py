"""
AI-Powered Message Generator for WhatsApp
Creates intelligent messages based on tone, topic, and context
"""

import logging
from typing import Optional, Dict, List
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageTone(Enum):
    """Available message tones"""
    FORMAL = "formal"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    URGENT = "urgent"
    APOLOGETIC = "apologetic"
    HUMOROUS = "humorous"


class MessageType(Enum):
    """Available message types"""
    GREETING = "greeting"
    QUERY = "query"
    UPDATE = "update"
    REMINDER = "reminder"
    REQUEST = "request"
    CONFIRMATION = "confirmation"
    APOLOGY = "apology"
    ANNOUNCEMENT = "announcement"


# Message patterns for different combinations
MESSAGE_PATTERNS = {
    ("greeting", "formal"): "I hope this message finds you well.",
    ("greeting", "casual"): "Hey! Just wanted to reach out.",
    ("greeting", "friendly"): "Hi there! How have you been?",
    
    ("query", "formal"): "I would like to inquire about",
    ("query", "casual"): "I was wondering if you could help with",
    ("query", "urgent"): "I urgently need information regarding",
    
    ("update", "formal"): "I am writing to inform you that",
    ("update", "casual"): "Just wanted to let you know that",
    ("update", "humorous"): "So guess what? It turns out that",
    
    ("reminder", "formal"): "This is to remind you about",
    ("reminder", "casual"): "Just a quick reminder about",
    ("reminder", "urgent"): "This is an urgent reminder",
    
    ("request", "formal"): "I would appreciate your assistance with",
    ("request", "casual"): "Could you help me with",
    ("request", "humorous"): "Would you be awesome enough to help with",
    
    ("confirmation", "formal"): "I can confirm that",
    ("confirmation", "casual"): "Yeah, that works for me",
    ("confirmation", "professional"): "I can confirm our agreement on",
    
    ("apology", "formal"): "I sincerely apologize for",
    ("apology", "casual"): "Sorry about that, I",
    ("apology", "apologetic"): "I deeply regret and apologize for",
    
    ("announcement", "formal"): "It is with pleasure that I announce",
    ("announcement", "casual"): "Exciting news! We're announcing",
    ("announcement", "urgent"): "IMPORTANT ANNOUNCEMENT:",
}

# Tone-specific phrases
TONE_PHRASES = {
    "formal": {
        "opening": "I hope this message finds you well.",
        "closing": "I look forward to hearing from you.",
        "transition": "Furthermore,",
        "emphasis": "It is important to note that"
    },
    "casual": {
        "opening": "Hey! Hope you're doing well.",
        "closing": "Let me know if you need anything!",
        "transition": "By the way,",
        "emphasis": "Just so you know,"
    },
    "friendly": {
        "opening": "Hi! How are things?",
        "closing": "Looking forward to chatting!",
        "transition": "Also,",
        "emphasis": "The thing is,"
    },
    "professional": {
        "opening": "Good day,",
        "closing": "Thank you for your attention.",
        "transition": "Additionally,",
        "emphasis": "Please note that"
    },
    "urgent": {
        "opening": "This requires immediate attention.",
        "closing": "Please respond as soon as possible.",
        "transition": "Critically,",
        "emphasis": "URGENT:"
    },
    "apologetic": {
        "opening": "I sincerely apologize.",
        "closing": "Thank you for your understanding.",
        "transition": "Additionally, I regret",
        "emphasis": "I'm truly sorry that"
    },
    "humorous": {
        "opening": "So, funny story...",
        "closing": "Thanks for the laugh!",
        "transition": "Oh, and here's the best part:",
        "emphasis": "Get this,"
    }
}


class AIMessageGenerator:
    """Generate AI-powered messages with customizable tone and type"""
    
    def __init__(self):
        """Initialize the message generator"""
        self.logger = logger
    
    def generate_message(
        self,
        topic: str,
        tone: str = "casual",
        message_type: str = "greeting",
        person_name: str = "Friend",
        additional_details: Optional[str] = None,
        include_greeting: bool = True,
        include_closing: bool = True
    ) -> str:
        """
        Generate an AI-crafted message
        
        Args:
            topic: Main topic or content of the message
            tone: Message tone (formal, casual, friendly, professional, urgent, apologetic, humorous)
            message_type: Type of message (greeting, query, update, reminder, request, confirmation, apology, announcement)
            person_name: Name of recipient
            additional_details: Extra context or details
            include_greeting: Whether to include greeting
            include_closing: Whether to include closing
            
        Returns:
            str: Generated message
        """
        try:
            tone_lower = tone.lower()
            msg_type_lower = message_type.lower()
            
            # Validate tone and message type
            valid_tones = [t.value for t in MessageTone]
            valid_types = [t.value for t in MessageType]
            
            if tone_lower not in valid_tones:
                self.logger.warning(f"Invalid tone '{tone}', using 'casual'")
                tone_lower = "casual"
            
            if msg_type_lower not in valid_types:
                self.logger.warning(f"Invalid message type '{message_type}', using 'greeting'")
                msg_type_lower = "greeting"
            
            message_parts = []
            
            # Add greeting
            if include_greeting:
                if tone_lower == "humorous":
                    greeting = f"{TONE_PHRASES[tone_lower]['opening']} 😄"
                elif tone_lower == "urgent":
                    greeting = TONE_PHRASES[tone_lower]['opening']
                else:
                    greeting = f"{TONE_PHRASES[tone_lower]['opening']}"
                message_parts.append(greeting)
                message_parts.append("")
            
            # Add main message content
            pattern_key = (msg_type_lower, tone_lower)
            if pattern_key in MESSAGE_PATTERNS:
                pattern = MESSAGE_PATTERNS[pattern_key]
                message_parts.append(f"{pattern} {topic}")
            else:
                # Fallback if pattern not found
                message_parts.append(topic)
            
            # Add additional details if provided
            if additional_details:
                message_parts.append("")
                transition = TONE_PHRASES[tone_lower].get("transition", "Additionally,")
                message_parts.append(f"{transition} {additional_details}")
            
            # Add closing
            if include_closing:
                message_parts.append("")
                closing = TONE_PHRASES[tone_lower].get("closing", "Thank you.")
                
                # Add emoji for humorous tone
                if tone_lower == "humorous":
                    closing += " 😊"
                
                message_parts.append(closing)
            
            message = "\n".join(message_parts)
            self.logger.info(f"Generated {tone_lower} {msg_type_lower} message")
            
            return message
        except Exception as e:
            self.logger.error(f"Error generating message: {e}")
            return topic
    
    def generate_quick_message(
        self,
        message_content: str,
        tone: Optional[str] = None
    ) -> str:
        """
        Generate a quick message without greeting/closing
        
        Args:
            message_content: The message content
            tone: Optional tone to apply
            
        Returns:
            str: Formatted message
        """
        try:
            if not tone:
                return message_content
            
            tone_lower = tone.lower()
            valid_tones = [t.value for t in MessageTone]
            
            if tone_lower not in valid_tones:
                return message_content
            
            # Apply tone-specific emphasis if available
            emphasis = TONE_PHRASES[tone_lower].get("emphasis", "")
            if emphasis:
                return f"{emphasis} {message_content}"
            
            return message_content
        except Exception as e:
            self.logger.error(f"Error in quick message: {e}")
            return message_content
    
    def suggest_tone(self, context: str) -> str:
        """
        Suggest appropriate tone based on context
        
        Args:
            context: Context about the message
            
        Returns:
            str: Suggested tone
        """
        context_lower = context.lower()
        
        if any(word in context_lower for word in ["urgent", "asap", "immediately"]):
            return MessageTone.URGENT.value
        elif any(word in context_lower for word in ["sorry", "apologize", "regret"]):
            return MessageTone.APOLOGETIC.value
        elif any(word in context_lower for word in ["formal", "business", "professional", "official"]):
            return MessageTone.PROFESSIONAL.value
        elif any(word in context_lower for word in ["love", "like", "enjoy", "fun"]):
            return MessageTone.HUMOROUS.value
        elif any(word in context_lower for word in ["hello", "hey", "hi"]):
            return MessageTone.FRIENDLY.value
        else:
            return MessageTone.CASUAL.value
    
    def get_available_tones(self) -> List[str]:
        """Get list of available tones"""
        return [t.value for t in MessageTone]
    
    def get_available_message_types(self) -> List[str]:
        """Get list of available message types"""
        return [t.value for t in MessageType]
    
    def get_tone_description(self, tone: str) -> str:
        """Get description of a tone"""
        descriptions = {
            "formal": "Professional and official tone",
            "casual": "Relaxed and informal tone",
            "friendly": "Warm and personal tone",
            "professional": "Business-appropriate tone",
            "urgent": "Time-sensitive and direct tone",
            "apologetic": "Sorry and sincere tone",
            "humorous": "Light-hearted and fun tone"
        }
        return descriptions.get(tone.lower(), "Unknown tone")
    
    def get_message_type_description(self, msg_type: str) -> str:
        """Get description of a message type"""
        descriptions = {
            "greeting": "Simple hello message",
            "query": "Question or inquiry",
            "update": "Informational update",
            "reminder": "Reminder or notification",
            "request": "Request for help or info",
            "confirmation": "Agreement or confirmation",
            "apology": "Apology message",
            "announcement": "Important announcement"
        }
        return descriptions.get(msg_type.lower(), "Unknown type")


def generate_whatsapp_message(
    topic: str,
    tone: Optional[str] = None,
    message_type: Optional[str] = None,
    person_name: str = "Friend",
    additional_details: Optional[str] = None,
    quick_mode: bool = False
) -> Dict:
    """
    Standalone function to generate messages
    
    Args:
        topic: Main topic/content
        tone: Optional tone
        message_type: Optional message type
        person_name: Recipient name
        additional_details: Extra context
        quick_mode: If True, just add tone without greeting/closing
        
    Returns:
        dict: Generated message and metadata
    """
    try:
        generator = AIMessageGenerator()
        
        if quick_mode:
            message = generator.generate_quick_message(topic, tone)
        else:
            # Auto-suggest tone if not provided
            if not tone:
                tone = generator.suggest_tone(topic)
            
            message = generator.generate_message(
                topic,
                tone=tone or "casual",
                message_type=message_type or "greeting",
                person_name=person_name,
                additional_details=additional_details
            )
        
        return {
            "success": True,
            "message": message,
            "tone": tone or "casual",
            "type": message_type or "greeting",
            "person": person_name
        }
    except Exception as e:
        logger.error(f"Error in generate_whatsapp_message: {e}")
        return {
            "success": False,
            "message": topic,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the generator
    generator = AIMessageGenerator()
    
    print("WhatsApp AI Message Generator")
    print(f"Available Tones: {generator.get_available_tones()}")
    print(f"Available Types: {generator.get_available_message_types()}")
    print()
    
    # Example messages
    print("Example 1: Formal greeting")
    msg1 = generator.generate_message(
        "I wanted to discuss the project timeline",
        tone="formal",
        message_type="query",
        person_name="Mr. Smith"
    )
    print(msg1)
    print("\n" + "="*50 + "\n")
    
    print("Example 2: Casual update")
    msg2 = generator.generate_message(
        "The website is now live and ready to use",
        tone="casual",
        message_type="update",
        person_name="Alex"
    )
    print(msg2)
