"""System power control tool for agent"""

import os
import subprocess
from livekit.agents import llm

def system_power_tool(action: str) -> str:
    """
    Control system power state
    
    Args:
        action: "lock" to lock screen, "shutdown" to shutdown, "restart" to restart
        
    Returns:
        Status message
    """
    try:
        if action.lower() == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "✓ System locked"
        
        elif action.lower() == "shutdown":
            os.system("shutdown /s /t 30")
            return "✓ System will shutdown in 30 seconds"
        
        elif action.lower() == "restart":
            os.system("shutdown /r /t 30")
            return "✓ System will restart in 30 seconds"
        
        elif action.lower() == "cancel":
            os.system("shutdown /a")
            return "✓ Shutdown cancelled"
        
        else:
            return "❌ Unknown action. Use: lock, shutdown, restart, or cancel"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Export tool for agent
__all__ = ["system_power_tool"]
