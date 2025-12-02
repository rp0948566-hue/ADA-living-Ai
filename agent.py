from dotenv import load_dotenv

import subprocess, os, sys, asyncio
import logging
import re

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)

# ═════════════════════════════════════════════════════════════════════════════
# 🔗 COMPLETE FILE LINKING - ALL 34+ WORKSPACE FILES
# ═════════════════════════════════════════════════════════════════════════════

# 1. PROMPTS & BEHAVIOR
from Jarvis_prompts import behavior_prompts, Reply_prompts

# 2. SCREENSHOT & SCREEN VISION
from Jarvis_screenshot import screenshot_tool
from advanced_screen_vision import analyze_screen_tool

# 3. SEARCH & INFORMATION
from Jarvis_google_search import google_search, get_current_datetime
from jarvis_get_whether import get_weather

# 4. WINDOW & FILE MANAGEMENT
from Jarvis_window_CTRL import open, close, folder_file
from Jarvis_file_opner import Play_file
from advanced_file_creator import create_file_tool

# 5. MEMORY MANAGEMENT
from memory.jarvis_memory import load_memory, save_memory, get_recent_conversations, add_memory_entry
from memory_interceptor import MEMORY_KEYWORDS
from memory_sync_bridge import get_backend_knowledge, get_merged_intelligence, apply_improvements_to_agent, get_shared_knowledge, MemorySyncBridge
from self_update_memory_ADA import get_search_knowledge, get_memory_evolution_status

# 6. INPUT CONTROLS
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool, 
    type_text_tool, press_key_tool, press_hotkey_tool, 
    control_volume_tool, swipe_gesture_tool
)

# 7. WINDOWS POWER CONTROL
from windows_power_ctrl import shutdown_pc, restart_pc, lock_screen, sleep_pc, lock_pc

# 8. AUTONOMOUS SYSTEMS & LEARNING
try:
    from autonomous_ada import AutonomousADA, run_autonomous_background
except (ImportError, AttributeError):
    AutonomousADA = None
    run_autonomous_background = None

try:
    from backend_learning_engine import BrainEngine, IntelligenceEngine, AutonomousBackend
except (ImportError, AttributeError):
    BrainEngine = None
    IntelligenceEngine = None
    AutonomousBackend = None

# 9. CODE GENERATION & ADVANCED FEATURES
try:
    from advanced_code_generator import generate_code_advanced
except (ImportError, AttributeError):
    generate_code_advanced = None

try:
    from jarvis_gui import start_gui_async
except (ImportError, AttributeError):
    start_gui_async = None

try:
    from screen_monitor import ScreenMonitor
except (ImportError, AttributeError):
    ScreenMonitor = None

# 10. TESTING & UTILITIES
from test_google_api import test_api_connection
from diagnose_api import diagnose_system
from ADA_vs_code_file_accase import access_ada_files
from verify_system import verify_system_setup

# 11. SETUP & CONFIGURATION
from SETUP_ADVANCED_AI import setup_system
from COMPLETE_FEATURE_GUIDE import FEATURE_GUIDE
from INSTALLATION_CHECKLIST import check_installation

# 12. OPTIONAL TOOLS (Import with fallback)
try:
    from off import shutdown_system
except ImportError:
    shutdown_system = None

try:
    from run_screenshot_test import run_screenshot_test
except ImportError:
    run_screenshot_test = None

try:
    from test_memory_direct import test_memory
except ImportError:
    test_memory = None

try:
    from test_memory_retrieve import retrieve_memory_test
except ImportError:
    retrieve_memory_test = None

try:
    from testing import run_tests
except ImportError:
    run_tests = None

try:
    # Handle file with hyphen in name using importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("window_lock", 
        os.path.join(os.path.dirname(__file__), "Window-laock-screen.py"))
    window_lock_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(window_lock_module)
    lock_window_screen = getattr(window_lock_module, 'lock_window_screen', None)
except (ImportError, AttributeError, FileNotFoundError):
    lock_window_screen = None

try:
    from ADA_SYSTEM_SUMMARY import SYSTEM_STATUS
except ImportError:
    SYSTEM_STATUS = None

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Memory interceptor flag - set to True to enable client-side memory injection
ENABLE_MEMORY_INTERCEPTOR = True


class Assistant(Agent):
    def __init__(self) -> None:
        # Build complete tool list with all linked files
        tools = [
            # Search & Information
            google_search,
            get_current_datetime,
            get_weather,
            
            # Memory Management (Core)
            load_memory,
            save_memory,
            get_recent_conversations,
            add_memory_entry,
            
            # Backend Knowledge Integration
            get_backend_knowledge,
            get_merged_intelligence,
            get_shared_knowledge,
            
            # Self-Update Memory & Evolution Learning
            get_search_knowledge,
            get_memory_evolution_status,
            
            # Window & File Management
            open,
            close,
            folder_file,
            Play_file,
            create_file_tool,
            
            # Screen & Vision
            screenshot_tool,
            analyze_screen_tool,
            
            # Input Controls
            move_cursor_tool,
            mouse_click_tool,
            scroll_cursor_tool,
            type_text_tool,
            press_key_tool,
            press_hotkey_tool,
            control_volume_tool,
            swipe_gesture_tool,
            
            # Power Control
            shutdown_pc,
            restart_pc,
            lock_screen,
            sleep_pc,
            lock_pc,
        ]
        
        # Add optional tools if available
        if generate_code_advanced is not None:
            tools.append(generate_code_advanced)
        
        if start_gui_async is not None:
            tools.append(start_gui_async)
        
        if shutdown_system is not None:
            tools.append(shutdown_system)
        
        if run_screenshot_test is not None:
            tools.append(run_screenshot_test)
        
        if test_memory is not None:
            tools.append(test_memory)
        
        if retrieve_memory_test is not None:
            tools.append(retrieve_memory_test)
        
        if run_tests is not None:
            tools.append(run_tests)
        
        if lock_window_screen is not None:
            tools.append(lock_window_screen)
        
        super().__init__(instructions=behavior_prompts, tools=tools)


async def entrypoint(ctx: agents.JobContext):
    """Entry point for LiveKit agent session with improved error handling"""
    max_retries = 5  # Increased from 3
    retry_count = 0
    base_wait_time = 3  # Increased from 2
    
    while retry_count < max_retries:
        try:
            print(f"\n🚀 Starting agent session (attempt {retry_count + 1}/{max_retries})...")
            
            session = AgentSession(
                llm=google.beta.realtime.RealtimeModel(
                    voice="Charon"
                )
            )
            
            await session.start(
                room=ctx.room,
                agent=Assistant(),
                room_input_options=RoomInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                    video_enabled=True 
                ),
            )

            await ctx.connect()
            print("✅ Connected to room, waiting for audio input...")

            # Generate reply with timeout handling
            try:
                # Try to inject memory context into the reply instructions
                instructions = Reply_prompts
                
                if ENABLE_MEMORY_INTERCEPTOR:
                    try:
                        print("🧠 Fetching memory context...")
                        # Fetch recent conversations to inject context
                        memory_context = await get_recent_conversations(limit=5)  # Reduced from 10
                        
                        # Only inject if there's actual memory, keep it brief
                        if "अभी तक कोई बातचीत याद नहीं है" not in memory_context:
                            instructions = f"""{Reply_prompts}

[RECENT CONTEXT]
{memory_context}
[/CONTEXT]"""
                            print("✅ Memory context injected")
                        else:
                            instructions = Reply_prompts
                            print("ℹ️ No previous conversations to inject")
                    except Exception as e:
                        print(f"⚠️ Memory injection skipped: {e}")
                        instructions = Reply_prompts
                
                print("📡 Sending instructions to LLM (this may take a moment)...")
                await session.generate_reply(
                    instructions=instructions
                )
                print("✅ Session completed successfully")
                break  # Success - exit retry loop
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ Reply generation error (attempt {retry_count + 1}/{max_retries}): {e}")
                
                # Check if it's a timeout/connection error worth retrying
                if any(keyword in error_msg for keyword in ["timed out", "timeout", "connection", "websocket", "closed"]):
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        wait_time = base_wait_time * retry_count  # Exponential backoff
                        print(f"🔄 Connection issue detected. Retrying in {wait_time}s... ({retry_count}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print("❌ Max retries exceeded after multiple timeouts")
                        raise
                else:
                    # Not a timeout - propagate error immediately
                    raise
            
        except KeyboardInterrupt:
            print("\n⛔ Agent stopped by user")
            break
        except Exception as e:
            print(f"❌ Session error (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            
            if retry_count < max_retries:
                wait_time = base_wait_time * retry_count  # Exponential backoff
                print(f"⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            else:
                print("❌ Max retries exceeded. Shutting down.")
                raise


if __name__ == "__main__":
    # Try to start the GUI alongside the agent (runs in a separate process)
    try:
        gui_path = os.path.join(os.path.dirname(__file__), "jarvis_gui.py")
        if os.path.exists(gui_path):
            # Start GUI as a detached subprocess so the agent can continue
            subprocess.Popen([sys.executable, gui_path], stdout=None, stderr=None, stdin=None, close_fds=True)
        else:
            print("jarvis_gui.py not found; GUI will not be started.")
    except Exception as e:
        print("Failed to start GUI subprocess:", e)

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))