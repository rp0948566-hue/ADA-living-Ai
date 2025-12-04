"""
WhatsApp Message Sender Module
Handles WhatsApp messaging with tone and content customization
"""

import subprocess
import time
import os
import webbrowser
import pyautogui
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Message tone templates
TONE_TEMPLATES = {
    "formal": {
        "greeting": "Dear {name},",
        "closing": "Best regards",
        "style": "professional and formal"
    },
    "casual": {
        "greeting": "Hey {name},",
        "closing": "Cheers",
        "style": "casual and friendly"
    },
    "friendly": {
        "greeting": "Hi {name}!",
        "closing": "Take care!",
        "style": "warm and friendly"
    },
    "professional": {
        "greeting": "Hello {name},",
        "closing": "Kind regards",
        "style": "formal and professional"
    },
    "urgent": {
        "greeting": "{name},",
        "closing": "Please respond ASAP",
        "style": "urgent and direct"
    },
    "apologetic": {
        "greeting": "Hi {name},",
        "closing": "Sorry for any inconvenience",
        "style": "apologetic and sincere"
    },
    "humorous": {
        "greeting": "Hey {name}! 😄",
        "closing": "Thanks a million!",
        "style": "light and humorous"
    }
}

# Message type templates
MESSAGE_TYPES = {
    "greeting": "Simple greeting message",
    "query": "Question or inquiry message",
    "update": "Informational update message",
    "reminder": "Reminder or notification message",
    "request": "Request for help or information",
    "confirmation": "Confirmation or agreement message",
    "apology": "Apology message",
    "announcement": "Important announcement"
}


class WhatsAppSender:
    """Class to handle WhatsApp messaging"""
    
    def __init__(self):
        """Initialize WhatsApp sender"""
        self.whatsapp_path = self.find_whatsapp()
        self.logger = logger
        
    def find_whatsapp(self) -> Optional[str]:
        """
        Find WhatsApp installation path on Windows
        
        Returns:
            str: Path to WhatsApp executable or None if not found
        """
        possible_paths = [
            r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_*\WhatsApp.exe",
            r"C:\Program Files (x86)\WhatsApp\WhatsApp.exe",
            r"C:\Program Files\WhatsApp\WhatsApp.exe",
            os.path.expandvars(r"%APPDATA%\WhatsApp\Bin\WhatsApp.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\app-*\WhatsApp.exe"),
        ]
        
        for path_pattern in possible_paths:
            try:
                if "*" in path_pattern:
                    # Handle wildcard paths
                    import glob
                    matches = glob.glob(path_pattern)
                    if matches:
                        return matches[0]
                elif os.path.exists(path_pattern):
                    return path_pattern
            except Exception as e:
                self.logger.warning(f"Error checking path {path_pattern}: {e}")
        
        # Try to find via command line
        try:
            result = subprocess.run(
                ["where", "WhatsApp"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        self.logger.warning("WhatsApp not found on system")
        return None
    
    def open_whatsapp(self) -> bool:
        """
        Open WhatsApp desktop application
        
        Returns:
            bool: True if successfully opened, False otherwise
        """
        try:
            if self.whatsapp_path and os.path.exists(self.whatsapp_path):
                subprocess.Popen(self.whatsapp_path)
                time.sleep(3)  # Wait for app to open
                self.logger.info("WhatsApp opened successfully")
                return True
            else:
                self.logger.error("WhatsApp path not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to open WhatsApp: {e}")
            return False
    
    def search_contact(self, contact_name: str) -> bool:
        """
        Search for contact in WhatsApp
        
        Args:
            contact_name: Name of the contact to search
            
        Returns:
            bool: True if contact found and opened, False otherwise
        """
        try:
            # Use keyboard shortcut to open search (Ctrl+F in WhatsApp)
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            # Type contact name
            pyautogui.typewrite(contact_name, interval=0.05)
            time.sleep(1)
            
            # Press Enter to select first result
            pyautogui.press('enter')
            time.sleep(1)
            
            self.logger.info(f"Searched for contact: {contact_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to search contact: {e}")
            return False
    
    def open_chat(self, contact_name: str, use_web: bool = False) -> bool:
        """
        Open chat with specific contact
        
        Args:
            contact_name: Name of contact to open chat with
            use_web: Whether to use WhatsApp Web
            
        Returns:
            bool: True if chat opened successfully
        """
        try:
            if use_web:
                # Use WhatsApp Web URL scheme
                contact_clean = contact_name.replace(" ", "")
                url = f"https://web.whatsapp.com/send?phone={contact_clean}"
                webbrowser.open(url)
            else:
                # Use WhatsApp Desktop
                if not self.open_whatsapp():
                    return False
                
                # Search for contact
                if not self.search_contact(contact_name):
                    return False
            
            self.logger.info(f"Chat opened with: {contact_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open chat: {e}")
            return False
    
    def generate_message(
        self,
        content: str,
        tone: str = "casual",
        message_type: str = "greeting",
        person_name: str = "Friend",
        additional_context: str = ""
    ) -> str:
        """
        Generate a formatted message based on tone and type
        
        Args:
            content: Main message content
            tone: Tone of message (formal, casual, friendly, professional, urgent, apologetic, humorous)
            message_type: Type of message (greeting, query, update, reminder, request, confirmation, apology, announcement)
            person_name: Name of the person receiving the message
            additional_context: Additional context for message generation
            
        Returns:
            str: Formatted message ready to send
        """
        try:
            # Get tone template
            tone_lower = tone.lower()
            tone_info = TONE_TEMPLATES.get(tone_lower, TONE_TEMPLATES["casual"])
            
            # Build message
            message_parts = []
            
            # Add greeting
            greeting = tone_info["greeting"].format(name=person_name)
            message_parts.append(greeting)
            
            # Add content
            message_parts.append("\n")
            message_parts.append(content)
            
            # Add additional context if provided
            if additional_context:
                message_parts.append("\n")
                message_parts.append(additional_context)
            
            # Add closing
            message_parts.append("\n")
            message_parts.append(tone_info["closing"])
            
            message = "\n".join(message_parts)
            self.logger.info(f"Message generated with tone '{tone}' and type '{message_type}'")
            
            return message
        except Exception as e:
            self.logger.error(f"Failed to generate message: {e}")
            return content
    
    def send_message(
        self,
        contact_name: str,
        message: str,
        tone: str = "casual",
        message_type: str = "greeting",
        person_name: str = "Friend"
    ) -> bool:
        """
        Send message to WhatsApp contact
        
        Args:
            contact_name: Name of WhatsApp contact
            message: Message content to send
            tone: Tone of message (optional if message is pre-formatted)
            message_type: Type of message
            person_name: Name to address in the message
            
        Returns:
            bool: True if message sent successfully
        """
        try:
            # Generate formatted message if needed
            if "{" not in message:  # Check if needs formatting
                formatted_message = self.generate_message(
                    message,
                    tone=tone,
                    message_type=message_type,
                    person_name=person_name
                )
            else:
                formatted_message = message
            
            # Open chat
            if not self.open_chat(contact_name):
                self.logger.error(f"Could not open chat with {contact_name}")
                return False
            
            time.sleep(2)
            
            # Click on message input field
            pyautogui.press('tab')  # Navigate to message box
            time.sleep(0.5)
            
            # Type message
            pyautogui.typewrite(formatted_message, interval=0.02)
            time.sleep(1)
            
            # Send message (Ctrl+Enter or just Enter depending on WhatsApp setting)
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(1)
            
            self.logger.info(f"Message sent to {contact_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def send_custom_message(
        self,
        contact_name: str,
        message_content: str,
        tone: Optional[str] = None,
        message_type: Optional[str] = None,
        person_name: str = "Friend"
    ) -> bool:
        """
        Send custom message with optional AI-generated formatting
        
        Args:
            contact_name: WhatsApp contact name
            message_content: Message content
            tone: Message tone (if None, sends as-is)
            message_type: Type of message
            person_name: Person's name for greeting
            
        Returns:
            bool: Success status
        """
        try:
            if tone:
                # Generate formatted message
                final_message = self.generate_message(
                    message_content,
                    tone=tone,
                    message_type=message_type or "greeting",
                    person_name=person_name
                )
            else:
                # Send message as-is in English
                final_message = message_content
            
            self.logger.info(f"Sending message to {contact_name}")
            return self.send_message(
                contact_name,
                final_message,
                tone=tone or "casual",
                message_type=message_type or "greeting",
                person_name=person_name
            )
        except Exception as e:
            self.logger.error(f"Failed to send custom message: {e}")
            return False
    
    def get_available_tones(self) -> list:
        """Get list of available message tones"""
        return list(TONE_TEMPLATES.keys())
    
    def get_available_message_types(self) -> list:
        """Get list of available message types"""
        return list(MESSAGE_TYPES.keys())
    
    def validate_tone(self, tone: str) -> bool:
        """Check if tone is valid"""
        return tone.lower() in TONE_TEMPLATES
    
    def validate_message_type(self, msg_type: str) -> bool:
        """Check if message type is valid"""
        return msg_type.lower() in MESSAGE_TYPES


def send_whatsapp_message(
    contact_name: str,
    message: str,
    tone: Optional[str] = None,
    message_type: Optional[str] = None,
    person_name: str = "Friend"
) -> dict:
    """
    Standalone function to send WhatsApp message
    
    Args:
        contact_name: Name of WhatsApp contact
        message: Message content
        tone: Optional tone (formal, casual, friendly, professional, urgent, apologetic, humorous)
        message_type: Optional message type
        person_name: Person's name
        
    Returns:
        dict: Status and result of message sending
    """
    try:
        sender = WhatsAppSender()
        
        # Validate inputs
        if tone and not sender.validate_tone(tone):
            return {
                "success": False,
                "message": f"Invalid tone. Available tones: {sender.get_available_tones()}",
                "error": "invalid_tone"
            }
        
        if message_type and not sender.validate_message_type(message_type):
            return {
                "success": False,
                "message": f"Invalid message type. Available types: {sender.get_available_message_types()}",
                "error": "invalid_message_type"
            }
        
        # Send message
        success = sender.send_custom_message(
            contact_name,
            message,
            tone=tone,
            message_type=message_type,
            person_name=person_name
        )
        
        return {
            "success": success,
            "contact": contact_name,
            "message": "Message sent successfully" if success else "Failed to send message",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in send_whatsapp_message: {e}")
        return {
            "success": False,
            "message": str(e),
            "error": "send_failed"
        }


if __name__ == "__main__":
    # Test the module
    sender = WhatsAppSender()
    
    print("WhatsApp Sender Module Loaded")
    print(f"WhatsApp Path: {sender.whatsapp_path}")
    print(f"Available Tones: {sender.get_available_tones()}")
    print(f"Available Message Types: {sender.get_available_message_types()}")
    
    # Example usage (commented out to prevent auto-execution)
    # result = send_whatsapp_message(
    #     contact_name="John Doe",
    #     message="I wanted to check in with you",
    #     tone="friendly",
    #     message_type="greeting",
    #     person_name="John"
    # )
    # print(result)
