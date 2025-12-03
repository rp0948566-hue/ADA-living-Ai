"""
Unified WhatsApp + Screen Sharing Tools
Integrates WhatsApp control and screen sharing as LiveKit agent tools
"""

import logging
from livekit import agents
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from whatsapp_advanced_control import send_whatsapp_message_advanced, check_whatsapp_status
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    logger.warning("WhatsApp advanced control not available")

try:
    from screen_sharing_system import (
        start_screen_share_voice,
        stop_screen_share_voice,
        get_screen_share_status,
        get_screen_share_summary
    )
    SCREEN_SHARING_AVAILABLE = True
except ImportError:
    SCREEN_SHARING_AVAILABLE = False
    logger.warning("Screen sharing system not available")


# ═════════════════════════════════════════════════════════════════════════════
# WHATSAPP TOOLS
# ═════════════════════════════════════════════════════════════════════════════

@agents.tool
async def open_and_send_whatsapp_tool(
    contact_name: str,
    message: str,
    auto_open: bool = True
) -> dict:
    """
    Open WhatsApp if needed and send a message to a contact
    
    Args:
        contact_name: Name of the WhatsApp contact
        message: Message to send
        auto_open: Automatically open WhatsApp if closed (default: True)
        
    Returns:
        dict: Result of the operation with detailed status
    """
    if not WHATSAPP_AVAILABLE:
        return {
            "success": False,
            "error": "WhatsApp control not available"
        }
    
    try:
        result = send_whatsapp_message_advanced(
            contact_name=contact_name,
            message=message,
            auto_open=auto_open,
            verify_contact=True
        )
        
        # Log the result
        if result["success"]:
            logger.info(f"✅ WhatsApp: Message sent to {contact_name}")
        else:
            logger.warning(f"❌ WhatsApp: Failed to send to {contact_name}")
        
        return result
    except Exception as e:
        logger.error(f"Error in WhatsApp tool: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@agents.tool
async def check_whatsapp_status_tool() -> dict:
    """
    Check WhatsApp installation and running status
    
    Returns:
        dict: WhatsApp status information
    """
    if not WHATSAPP_AVAILABLE:
        return {
            "available": False,
            "error": "WhatsApp control not available"
        }
    
    try:
        status = check_whatsapp_status()
        logger.info(f"WhatsApp Status: {status}")
        return status
    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ═════════════════════════════════════════════════════════════════════════════
# SCREEN SHARING TOOLS
# ═════════════════════════════════════════════════════════════════════════════

@agents.tool
async def start_screen_share_tool(enable_recording: bool = True) -> dict:
    """
    Start screen sharing and recording
    
    Args:
        enable_recording: Whether to record frames to disk (default: True)
        
    Returns:
        dict: Status of screen sharing startup
    """
    if not SCREEN_SHARING_AVAILABLE:
        return {
            "success": False,
            "error": "Screen sharing system not available"
        }
    
    try:
        result = start_screen_share_voice(enable_recording=enable_recording)
        
        if result["success"]:
            logger.info("✅ Screen Sharing: Started successfully")
            logger.info(f"   Resolution: {result.get('screen_size')}")
            logger.info(f"   FPS: {result.get('fps')}")
            logger.info("   Status: [RECORDING] Say 'stop screen share' to end")
        else:
            logger.warning(f"❌ Screen Sharing: {result.get('message', result.get('error'))}")
        
        return result
    except Exception as e:
        logger.error(f"Error starting screen share: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@agents.tool
async def stop_screen_share_tool() -> dict:
    """
    Stop screen sharing and recording
    
    Returns:
        dict: Summary of the screen sharing session
    """
    if not SCREEN_SHARING_AVAILABLE:
        return {
            "success": False,
            "error": "Screen sharing system not available"
        }
    
    try:
        result = stop_screen_share_voice()
        
        if result["success"]:
            logger.info("✅ Screen Sharing: Stopped")
            logger.info(f"   Duration: {result.get('duration_seconds')}s")
            logger.info(f"   Frames captured: {result.get('total_frames')}")
            logger.info(f"   Average FPS: {result.get('average_fps')}")
            logger.info(f"   Saved to: {result.get('frames_saved')}")
        else:
            logger.warning(f"❌ Screen Sharing: {result.get('message', result.get('error'))}")
        
        return result
    except Exception as e:
        logger.error(f"Error stopping screen share: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@agents.tool
async def get_screen_share_status_tool() -> dict:
    """
    Get current screen sharing status
    
    Returns:
        dict: Current screen sharing status and statistics
    """
    if not SCREEN_SHARING_AVAILABLE:
        return {
            "available": False,
            "error": "Screen sharing system not available"
        }
    
    try:
        status = get_screen_share_status()
        return {
            "available": True,
            "status": status
        }
    except Exception as e:
        logger.error(f"Error getting screen share status: {e}")
        return {
            "available": False,
            "error": str(e)
        }


@agents.tool
async def get_screen_share_summary_tool() -> dict:
    """
    Get screen sharing session summary with image
    
    Returns:
        dict: Summary of the screen sharing session
    """
    if not SCREEN_SHARING_AVAILABLE:
        return {
            "available": False,
            "error": "Screen sharing system not available"
        }
    
    try:
        summary = get_screen_share_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting screen share summary: {e}")
        return {
            "available": False,
            "error": str(e)
        }


# ═════════════════════════════════════════════════════════════════════════════
# COMBINED TOOLS EXPORTS
# ═════════════════════════════════════════════════════════════════════════════

WHATSAPP_ADVANCED_TOOLS = [
    open_and_send_whatsapp_tool,
    check_whatsapp_status_tool
]

SCREEN_SHARING_TOOLS = [
    start_screen_share_tool,
    stop_screen_share_tool,
    get_screen_share_status_tool,
    get_screen_share_summary_tool
]

ALL_ADVANCED_TOOLS = WHATSAPP_ADVANCED_TOOLS + SCREEN_SHARING_TOOLS


if __name__ == "__main__":
    print("Advanced WhatsApp + Screen Sharing Tools")
    print("=" * 50)
    print(f"WhatsApp tools available: {WHATSAPP_AVAILABLE}")
    print(f"Screen sharing tools available: {SCREEN_SHARING_AVAILABLE}")
    print(f"\nTotal tools: {len(ALL_ADVANCED_TOOLS)}")
    for tool in ALL_ADVANCED_TOOLS:
        print(f"  ✓ {tool.__name__}")
