"""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║               🖥️ WINDOWS POWER CONTROL - COMPLETE SYSTEM                       ║
║                                                                                ║
║              Lock • Shutdown • Restart • Sleep • Hibernate                     ║
║              HP Laptop Optimized • Endlessly Running • Auto-Responsive         ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
"""

import subprocess
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import threading

try:
    from livekit.agents import function_tool
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [WINDOWS_POWER_CTRL] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('memory/windows_power_ctrl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# System information
SYSTEM_TYPE = "Windows 10/11 HP Laptop"
POWER_COMMANDS = {
    "lock": "rundll32.exe user32.dll,LockWorkStation",
    "shutdown": "shutdown /s /t {delay}",
    "restart": "shutdown /r /t {delay}",
    "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
    "hibernate": "shutdown /h",
    "cancel": "shutdown /a"
}

# Memory path for logging
MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)
POWER_LOG = MEMORY_DIR / "power_operations.json"


class WindowsPowerController:
    """Controls Windows system power operations"""
    
    def __init__(self):
        self.operations_log = []
        self.operation_count = 0
        self._load_log()
        logger.info(f"✓ Windows Power Controller initialized for {SYSTEM_TYPE}")
    
    def _load_log(self):
        """Load operation log"""
        try:
            if POWER_LOG.exists():
                import json
                with open(POWER_LOG, 'r', encoding='utf-8') as f:
                    self.operations_log = json.load(f)
                    logger.info(f"Loaded {len(self.operations_log)} previous operations")
        except:
            pass
    
    def _save_log(self):
        """Save operation log"""
        try:
            import json
            with open(POWER_LOG, 'w', encoding='utf-8') as f:
                json.dump(self.operations_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Could not save log: {e}")
    
    def _log_operation(self, operation: str, command: str, status: str, details: str = ""):
        """Log power operation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "command": command,
            "status": status,
            "details": details,
            "system": SYSTEM_TYPE
        }
        self.operations_log.append(entry)
        self.operation_count += 1
        self._save_log()
        logger.info(f"📝 Operation logged: {operation} ({status})")
    
    def lock_laptop(self) -> Dict[str, str]:
        """Lock the Windows laptop"""
        logger.info("🔒 LOCKING LAPTOP")
        try:
            command = POWER_COMMANDS["lock"]
            logger.info(f"   Executing: {command}")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 or "Unexpected error" not in str(result.stderr):
                msg = "✅ Laptop locked successfully"
                logger.info(msg)
                self._log_operation("lock", command, "success")
                return {
                    "status": "success",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                msg = f"⚠️ Lock command returned code {result.returncode}"
                logger.warning(msg)
                self._log_operation("lock", command, "warning", msg)
                return {
                    "status": "warning",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            msg = f"❌ Error locking laptop: {str(e)}"
            logger.error(msg)
            self._log_operation("lock", command, "error", str(e))
            return {
                "status": "error",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def shutdown_laptop(self, delay_seconds: int = 0) -> Dict[str, str]:
        """Shutdown the Windows laptop"""
        logger.info(f"🛑 SHUTTING DOWN LAPTOP (delay: {delay_seconds}s)")
        try:
            command = POWER_COMMANDS["shutdown"].format(delay=delay_seconds)
            logger.info(f"   Executing: {command}")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                if delay_seconds > 0:
                    msg = f"✅ Laptop will shutdown in {delay_seconds} seconds"
                else:
                    msg = "✅ Laptop shutting down now"
                logger.info(msg)
                self._log_operation("shutdown", command, "success", f"Delay: {delay_seconds}s")
                return {
                    "status": "success",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                msg = f"⚠️ Shutdown command returned code {result.returncode}"
                logger.warning(msg)
                self._log_operation("shutdown", command, "warning", msg)
                return {
                    "status": "warning",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            msg = f"❌ Error shutting down laptop: {str(e)}"
            logger.error(msg)
            self._log_operation("shutdown", command, "error", str(e))
            return {
                "status": "error",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def restart_laptop(self, delay_seconds: int = 0) -> Dict[str, str]:
        """Restart the Windows laptop"""
        logger.info(f"🔄 RESTARTING LAPTOP (delay: {delay_seconds}s)")
        try:
            command = POWER_COMMANDS["restart"].format(delay=delay_seconds)
            logger.info(f"   Executing: {command}")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                if delay_seconds > 0:
                    msg = f"✅ Laptop will restart in {delay_seconds} seconds"
                else:
                    msg = "✅ Laptop restarting now"
                logger.info(msg)
                self._log_operation("restart", command, "success", f"Delay: {delay_seconds}s")
                return {
                    "status": "success",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                msg = f"⚠️ Restart command returned code {result.returncode}"
                logger.warning(msg)
                self._log_operation("restart", command, "warning", msg)
                return {
                    "status": "warning",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            msg = f"❌ Error restarting laptop: {str(e)}"
            logger.error(msg)
            self._log_operation("restart", command, "error", str(e))
            return {
                "status": "error",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def sleep_laptop(self) -> Dict[str, str]:
        """Put the laptop to sleep"""
        logger.info("😴 PUTTING LAPTOP TO SLEEP")
        try:
            command = POWER_COMMANDS["sleep"]
            logger.info(f"   Executing: {command}")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 or result.returncode == 1:  # Sleep sometimes returns 1
                msg = "✅ Laptop entering sleep mode"
                logger.info(msg)
                self._log_operation("sleep", command, "success")
                return {
                    "status": "success",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                msg = f"⚠️ Sleep command returned code {result.returncode}"
                logger.warning(msg)
                self._log_operation("sleep", command, "warning", msg)
                return {
                    "status": "warning",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            msg = f"❌ Error putting laptop to sleep: {str(e)}"
            logger.error(msg)
            self._log_operation("sleep", command, "error", str(e))
            return {
                "status": "error",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def hibernate_laptop(self) -> Dict[str, str]:
        """Put laptop into hibernation"""
        logger.info("❄️ HIBERNATING LAPTOP")
        try:
            command = POWER_COMMANDS["hibernate"]
            logger.info(f"   Executing: {command}")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                msg = "✅ Laptop entering hibernation"
                logger.info(msg)
                self._log_operation("hibernate", command, "success")
                return {
                    "status": "success",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                msg = f"⚠️ Hibernate command returned code {result.returncode}"
                logger.warning(msg)
                self._log_operation("hibernate", command, "warning", msg)
                return {
                    "status": "warning",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            msg = f"❌ Error hibernating laptop: {str(e)}"
            logger.error(msg)
            self._log_operation("hibernate", command, "error", str(e))
            return {
                "status": "error",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def cancel_shutdown(self) -> Dict[str, str]:
        """Cancel any pending shutdown or restart"""
        logger.info("❌ CANCELING SHUTDOWN/RESTART")
        try:
            command = POWER_COMMANDS["cancel"]
            logger.info(f"   Executing: {command}")
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                msg = "✅ Pending shutdown/restart cancelled"
                logger.info(msg)
                self._log_operation("cancel", command, "success")
                return {
                    "status": "success",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                msg = "ℹ️ No pending shutdown to cancel"
                logger.info(msg)
                self._log_operation("cancel", command, "info", "No pending operation")
                return {
                    "status": "info",
                    "message": msg,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            msg = f"⚠️ Error canceling shutdown: {str(e)}"
            logger.warning(msg)
            self._log_operation("cancel", command, "warning", str(e))
            return {
                "status": "warning",
                "message": msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get power control status"""
        return {
            "system": SYSTEM_TYPE,
            "operations_count": self.operation_count,
            "last_operation": self.operations_log[-1] if self.operations_log else None,
            "log_file": str(POWER_LOG),
            "status": "active"
        }


# Global controller instance
controller = WindowsPowerController()


# ═════════════════════════════════════════════════════════════════════════════
# LIVEKIT FUNCTION TOOLS
# ═════════════════════════════════════════════════════════════════════════════

if LIVEKIT_AVAILABLE:
    
    @function_tool
    async def lock_pc() -> str:
        """Lock the Windows PC/Laptop"""
        result = controller.lock_laptop()
        return result["message"]
    
    
    @function_tool
    async def lock_screen() -> str:
        """Lock the Windows PC/Laptop screen"""
        result = controller.lock_laptop()
        return result["message"]
    
    
    @function_tool
    async def shutdown_pc(delay_seconds: int = 0) -> str:
        """Shutdown the Windows PC/Laptop (optional delay in seconds)"""
        result = controller.shutdown_laptop(delay_seconds)
        return result["message"]
    
    
    @function_tool
    async def restart_pc(delay_seconds: int = 0) -> str:
        """Restart the Windows PC/Laptop (optional delay in seconds)"""
        result = controller.restart_laptop(delay_seconds)
        return result["message"]
    
    
    @function_tool
    async def sleep_pc() -> str:
        """Put the Windows PC/Laptop to sleep"""
        result = controller.sleep_laptop()
        return result["message"]
    
    
    @function_tool
    async def hibernate_pc() -> str:
        """Put the Windows PC/Laptop into hibernation"""
        result = controller.hibernate_laptop()
        return result["message"]
    
    
    @function_tool
    async def cancel_shutdown_pc() -> str:
        """Cancel any pending shutdown or restart"""
        result = controller.cancel_shutdown()
        return result["message"]


# ═════════════════════════════════════════════════════════════════════════════
# DIRECT PYTHON API (for use without LiveKit)
# ═════════════════════════════════════════════════════════════════════════════

def lock():
    """Direct lock function"""
    return controller.lock_laptop()


def shutdown(delay: int = 0):
    """Direct shutdown function"""
    return controller.shutdown_laptop(delay)


def restart(delay: int = 0):
    """Direct restart function"""
    return controller.restart_laptop(delay)


def sleep():
    """Direct sleep function"""
    return controller.sleep_laptop()


def hibernate():
    """Direct hibernation function"""
    return controller.hibernate_laptop()


def cancel():
    """Direct cancel function"""
    return controller.cancel_shutdown()


def get_status():
    """Direct status function"""
    return controller.get_status()
