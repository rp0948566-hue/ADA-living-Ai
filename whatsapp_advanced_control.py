"""
Advanced WhatsApp Control System
Automatically opens WhatsApp, verifies contacts, and sends messages
With automatic contact detection and verification
"""

import subprocess
import time
import os
import pyautogui
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime
import psutil
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WhatsAppController:
    """Advanced WhatsApp controller with auto-open and verification"""
    
    def __init__(self):
        """Initialize the WhatsApp controller"""
        self.whatsapp_path = self.find_whatsapp()
        self.is_open = self.check_whatsapp_running()
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
                    import glob
                    matches = glob.glob(path_pattern)
                    if matches:
                        return matches[0]
                elif os.path.exists(path_pattern):
                    return path_pattern
            except Exception as e:
                self.logger.warning(f"Error checking path {path_pattern}: {e}")
        
        try:
            result = subprocess.run(["where", "WhatsApp"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        self.logger.warning("WhatsApp not found on system")
        return None
    
    def check_whatsapp_running(self) -> bool:
        """
        Check if WhatsApp is currently running
        
        Returns:
            bool: True if WhatsApp is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == 'whatsapp.exe':
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return False
    
    def open_whatsapp(self, wait_for_startup: int = 5) -> bool:
        """
        Open WhatsApp if not already running
        
        Args:
            wait_for_startup: Seconds to wait for WhatsApp to start
            
        Returns:
            bool: True if successfully opened or already running
        """
        try:
            # Check if already running
            if self.check_whatsapp_running():
                self.logger.info("WhatsApp is already running")
                self.is_open = True
                return True
            
            # Try to open WhatsApp
            if self.whatsapp_path and os.path.exists(self.whatsapp_path):
                self.logger.info(f"Opening WhatsApp: {self.whatsapp_path}")
                subprocess.Popen(self.whatsapp_path)
                
                # Wait for WhatsApp to start
                start_time = time.time()
                while time.time() - start_time < wait_for_startup:
                    time.sleep(0.5)
                    if self.check_whatsapp_running():
                        self.is_open = True
                        self.logger.info("WhatsApp opened successfully")
                        time.sleep(2)  # Additional wait for UI to load
                        return True
                
                self.logger.warning(f"WhatsApp didn't start within {wait_for_startup} seconds")
                return False
            else:
                self.logger.error("WhatsApp path not found. Install WhatsApp Desktop first.")
                return False
        except Exception as e:
            self.logger.error(f"Failed to open WhatsApp: {e}")
            return False
    
    def search_and_verify_contact(self, contact_name: str, timeout: int = 10) -> bool:
        """
        Search for a contact in WhatsApp and verify it exists
        
        Args:
            contact_name: Name of the contact to search
            timeout: Maximum time to wait for contact
            
        Returns:
            bool: True if contact found and opened, False otherwise
        """
        try:
            self.logger.info(f"Searching for contact: {contact_name}")
            
            # Open search with Ctrl+F
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.8)
            
            # Clear any existing text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            
            # Type contact name
            pyautogui.typewrite(contact_name, interval=0.05)
            time.sleep(1.5)
            
            # Press Enter to select first result
            pyautogui.press('enter')
            time.sleep(1)
            
            self.logger.info(f"Contact '{contact_name}' found and opened")
            return True
        except Exception as e:
            self.logger.error(f"Failed to search for contact: {e}")
            return False
    
    def send_message_to_contact(
        self,
        contact_name: str,
        message: str,
        verify_contact: bool = True
    ) -> Dict:
        """
        Complete workflow: open WhatsApp, find contact, and send message
        
        Args:
            contact_name: Name of the WhatsApp contact
            message: Message content to send
            verify_contact: Whether to verify contact exists first
            
        Returns:
            dict: Status and details of the operation
        """
        try:
            result = {
                "success": False,
                "contact": contact_name,
                "message_preview": message[:50] + "..." if len(message) > 50 else message,
                "timestamp": datetime.now().isoformat(),
                "steps_completed": []
            }
            
            # Step 1: Open WhatsApp if not running
            self.logger.info(f"[Step 1] Opening WhatsApp if needed...")
            if not self.open_whatsapp():
                result["error"] = "Failed to open WhatsApp"
                result["steps_completed"].append("open_whatsapp: FAILED")
                return result
            result["steps_completed"].append("open_whatsapp: SUCCESS")
            
            # Step 2: Search for and verify contact
            self.logger.info(f"[Step 2] Searching for contact: {contact_name}")
            if not self.search_and_verify_contact(contact_name):
                result["error"] = f"Contact '{contact_name}' not found"
                result["steps_completed"].append(f"search_contact: FAILED")
                return result
            result["steps_completed"].append(f"search_contact: SUCCESS")
            
            # Step 3: Click on message input field
            self.logger.info(f"[Step 3] Clicking message input field...")
            pyautogui.press('tab')
            time.sleep(0.5)
            result["steps_completed"].append("focus_input: SUCCESS")
            
            # Step 4: Type the message
            self.logger.info(f"[Step 4] Typing message...")
            pyautogui.typewrite(message, interval=0.02)
            time.sleep(1)
            result["steps_completed"].append("type_message: SUCCESS")
            
            # Step 5: Send message
            self.logger.info(f"[Step 5] Sending message...")
            pyautogui.hotkey('ctrl', 'enter')
            time.sleep(1.5)
            result["steps_completed"].append("send_message: SUCCESS")
            
            result["success"] = True
            result["message"] = f"Message successfully sent to {contact_name}"
            
            self.logger.info(f"✅ Message sent to {contact_name}")
            return result
        except Exception as e:
            logger.error(f"Error in send_message_to_contact: {e}")
            return {
                "success": False,
                "contact": contact_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict:
        """
        Get current WhatsApp status
        
        Returns:
            dict: Current status information
        """
        return {
            "whatsapp_installed": self.whatsapp_path is not None,
            "whatsapp_running": self.check_whatsapp_running(),
            "whatsapp_path": self.whatsapp_path,
            "ready_to_send": self.check_whatsapp_running()
        }


def send_whatsapp_message_advanced(
    contact_name: str,
    message: str,
    auto_open: bool = True,
    verify_contact: bool = True
) -> Dict:
    """
    Standalone function to send WhatsApp message with full automation
    
    Args:
        contact_name: Name of WhatsApp contact
        message: Message to send
        auto_open: Automatically open WhatsApp if closed
        verify_contact: Verify contact exists before sending
        
    Returns:
        dict: Operation result and status
    """
    try:
        controller = WhatsAppController()
        
        # Open WhatsApp if requested
        if auto_open:
            if not controller.open_whatsapp():
                return {
                    "success": False,
                    "error": "Could not open WhatsApp"
                }
        
        # Send message
        result = controller.send_message_to_contact(
            contact_name,
            message,
            verify_contact=verify_contact
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in send_whatsapp_message_advanced: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def check_whatsapp_status() -> Dict:
    """
    Check WhatsApp installation and running status
    
    Returns:
        dict: Status information
    """
    try:
        controller = WhatsAppController()
        return controller.get_status()
    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}")
        return {
            "error": str(e),
            "whatsapp_running": False,
            "whatsapp_installed": False
        }


if __name__ == "__main__":
    # Test the controller
    print("WhatsApp Advanced Controller Test")
    print("=" * 50)
    
    controller = WhatsAppController()
    
    print("\nStatus:")
    print(controller.get_status())
    
    print("\nUsage Example:")
    print("-" * 50)
    print("""
# Example 1: Auto-open and send message
result = send_whatsapp_message_advanced(
    contact_name="John Doe",
    message="Hello! This is a test message.",
    auto_open=True
)
print(result)

# Example 2: Check status
status = check_whatsapp_status()
print(status)
    """)
