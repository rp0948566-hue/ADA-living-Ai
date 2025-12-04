"""
WhatsApp Tool Wrappers for LiveKit Agent Integration
Converts WhatsApp functionality into properly formatted LiveKit agent tools
"""

import logging
from livekit import agents
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from whatsapp_sender import send_whatsapp_message, WhatsAppSender
    from whatsapp_message_generator import generate_whatsapp_message, AIMessageGenerator
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    logger.warning("WhatsApp modules not available")


@agents.tool
async def send_whatsapp_tool(
    contact_name: str,
    message: str,
    tone: Optional[str] = None,
    message_type: Optional[str] = None
) -> dict:
    """
    Send a WhatsApp message to a contact
    
    Args:
        contact_name: Name of the WhatsApp contact to message
        message: The message content to send
        tone: Optional tone (formal, casual, friendly, professional, urgent, apologetic, humorous)
        message_type: Optional message type (greeting, query, update, reminder, request, confirmation, apology, announcement)
        
    Returns:
        dict: Status of message sending operation
    """
    if not WHATSAPP_AVAILABLE:
        return {
            "success": False,
            "error": "WhatsApp modules not available"
        }
    
    try:
        result = send_whatsapp_message(
            contact_name=contact_name,
            message=message,
            tone=tone,
            message_type=message_type,
            person_name=contact_name
        )
        return result
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@agents.tool
async def generate_whatsapp_message_tool(
    topic: str,
    tone: Optional[str] = None,
    message_type: Optional[str] = None,
    person_name: str = "Friend",
    quick_mode: bool = False
) -> dict:
    """
    Generate an AI-crafted message with specific tone and type
    
    Args:
        topic: Main topic or content of the message
        tone: Optional tone (formal, casual, friendly, professional, urgent, apologetic, humorous)
        message_type: Optional message type (greeting, query, update, reminder, request, confirmation, apology, announcement)
        person_name: Name of the recipient
        quick_mode: If True, just add tone without greeting/closing
        
    Returns:
        dict: Generated message with metadata
    """
    if not WHATSAPP_AVAILABLE:
        return {
            "success": False,
            "error": "WhatsApp modules not available"
        }
    
    try:
        result = generate_whatsapp_message(
            topic=topic,
            tone=tone,
            message_type=message_type,
            person_name=person_name,
            quick_mode=quick_mode
        )
        return result
    except Exception as e:
        logger.error(f"Error generating message: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@agents.tool
async def get_whatsapp_info_tool() -> dict:
    """
    Get WhatsApp system information and available options
    
    Returns:
        dict: WhatsApp status and available options
    """
    if not WHATSAPP_AVAILABLE:
        return {
            "success": False,
            "error": "WhatsApp modules not available",
            "status": "not_available"
        }
    
    try:
        sender = WhatsAppSender()
        generator = AIMessageGenerator()
        
        return {
            "success": True,
            "whatsapp_path": sender.whatsapp_path,
            "whatsapp_installed": sender.whatsapp_path is not None,
            "available_tones": sender.get_available_tones(),
            "available_message_types": sender.get_available_message_types(),
            "message_generator_available": True,
            "status": "ready"
        }
    except Exception as e:
        logger.error(f"Error getting WhatsApp info: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Export the tools
WHATSAPP_TOOLS = [
    send_whatsapp_tool,
    generate_whatsapp_message_tool,
    get_whatsapp_info_tool
]


if __name__ == "__main__":
    print("WhatsApp Tool Wrappers Loaded")
    print(f"WhatsApp Available: {WHATSAPP_AVAILABLE}")
    print(f"Number of tools: {len(WHATSAPP_TOOLS)}")
