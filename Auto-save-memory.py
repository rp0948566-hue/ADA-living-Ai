from dotenv import load_dotenv

import subprocess, os, sys, asyncio
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)


# Check if console mode is requested BEFORE loading heavy dependencies
def check_console_mode():
    """Check if console mode is requested"""
    return len(sys.argv) > 1 and sys.argv[1].lower() == "console"


def run_console_mode():
    """Console mode: Run autonomous system directly without full agent"""
    print("\n" + "="*80)
    print("[CONSOLE] AUTONOMOUS SYSTEM")
    print("="*80)
    print("\n[INFO] Initializing autonomous learning system...\n")
    
    # Try to start the GUI in a separate process
    try:
        gui_path = os.path.join(os.path.dirname(file), "jarvis_gui.py")
        if os.path.exists(gui_path):
            print("[INFO] Starting GUI in background...")
            subprocess.Popen([sys.executable, gui_path], stdout=None, stderr=None, stdin=None, close_fds=True)
            print("[OK] GUI launched\n")
        else:
            print("[WARNING] jarvis_gui.py not found; GUI will not be started.\n")
    except Exception as e:
        print(f"[WARNING] Could not start GUI: {e}\n")
    
    try:
        from autonomous_ada import AutonomousADA
        ada = AutonomousADA()
        
        print("="*80)
        print("[INFO] AUTONOMOUS ADA INITIALIZED AND RUNNING")
        print("="*80)
        print("\n[OK] Continuous learning loop: ACTIVE")
        print("[OK] Personality evolution: ACTIVE")
        print("[OK] Memory persistence: ENABLED")
        print("[OK] Independent thinking: ACTIVATED")
        print("\n[INPUT] Press Ctrl+C to stop...\n")
        print("="*80 + "\n")
        
        asyncio.run(ada.continuous_learning_loop())
        
    except KeyboardInterrupt:
        print("\n\n[STOP] Autonomous system stopped by user")
        print("[OK] All data saved to memory files")
        print("[OK] System shutdown complete\n")
    except ImportError as e:
        print(f"\n[ERROR] Import Error: {e}")
        print("Make sure all dependencies are installed.")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()


# LOAD HEAVY DEPENDENCIES - only executed if NOT in console mode
if not check_console_mode():
    print("[INFO] Loading LiveKit Agent dependencies...")
    
    from livekit import agents
    from livekit.agents import AgentSession, Agent, RoomInputOptions
    from livekit.plugins import google, noise_cancellation
    from Jarvis_prompts import behavior_prompts, Reply_prompts
    from Jarvis_screenshot import screenshot_tool
    from Jarvis_google_search import google_search, get_current_datetime
    from memory.jarvis_memory import load_memory, save_memory, get_recent_conversations, add_memory_entry
    from memory_interceptor import MEMORY_KEYWORDS
    from jarvis_get_whether import get_weather
    from Jarvis_window_CTRL import open, close, folder_file
    from Jarvis_file_opner import Play_file
    from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
    from off import system_power_tool
    from ADA_vs_code_file_accase import read_project_files_tool
    from advanced_file_creator import create_file_tool, read_file_tool, write_file_tool, list_files_tool, delete_file_tool, open_file_tool
    from advanced_screen_vision import take_screenshot_tool, extract_screen_text_tool, analyze_screen_tool, search_screen_text_tool, get_screen_info_tool, analyze_colors_tool, detect_ui_elements_tool
    from advanced_code_generator import generate_code_tool, generate_python_function_tool, generate_python_class_tool, generate_html_form_tool, generate_react_component_tool, generate_javascript_api_tool
from autonomous_ada import run_autonomous_background

import re
import openai
import google.generativeai as genai
import requests

ENABLE_MEMORY_INTERCEPTOR = True
print("[OK] LiveKit Agent dependencies loaded\n")

class Assistant(Agent):
        """AI Assistant with all tools"""
        def init(self) -> None:
            super().init(
                instructions=behavior_prompts,
                tools=[
                    google_search, get_current_datetime, get_weather,
                    open, close, load_memory, save_memory,
                    get_recent_conversations, add_memory_entry,
                    folder_file, Play_file, screenshot_tool,
                    move_cursor_tool, mouse_click_tool, scroll_cursor_tool,
                    type_text_tool, press_key_tool, press_hotkey_tool,
                    control_volume_tool, swipe_gesture_tool,
                    system_power_tool, read_project_files_tool,
                    create_file_tool, read_file_tool, write_file_tool,
                    list_files_tool, delete_file_tool, open_file_tool,
                    take_screenshot_tool, extract_screen_text_tool,
                    analyze_screen_tool, search_screen_text_tool,
                    get_screen_info_tool, analyze_colors_tool,
                    detect_ui_elements_tool, generate_code_tool,
                    generate_python_function_tool, generate_python_class_tool,
                    generate_html_form_tool, generate_react_component_tool,
                    generate_javascript_api_tool,

                    ask_chatgpt,  # AI model functions from app.py
                    ask_gemini,
                    ask_deepseek,
                    ask_perplexity,
                    ask_claude,
                    ask_grok
                ]
            )


async def entrypoint(ctx: agents.JobContext):
        """LiveKit agent entry point"""
        
        print("\n" + "="*80)
        print("INITIALIZING AUTONOMOUS ADA SYSTEM")
        print("="*80)
        print("[INFO] Continuous learning loop starting...")
        print("[INFO] Memory evolution enabled")
        print("[INFO] Computer control active")
        print("="*80 + "\n")
        
        try:
            autonomous_thread = run_autonomous_background()
            print("[OK] Autonomous background thread started\n")
        except Exception as e:
            print(f"[WARNING] Autonomous thread: {e}\n")
        
        max_retries = 5
        retry_count = 0
        base_wait_time = 3
        
        while retry_count < max_retries:
            try:
                print(f"\n[INFO] Starting agent session (attempt {retry_count + 1}/{max_retries})...")
                
                session = AgentSession(
                    llm=google.beta.realtime.RealtimeModel(voice="Charon")
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
                print("[OK] Connected to room, waiting for audio input...")

                try:
                    instructions = Reply_prompts
                    
                    if ENABLE_MEMORY_INTERCEPTOR:
                        try:
                            print("[INFO] Fetching memory context...")
                            memory_context = await get_recent_conversations(limit=5)
                            
                            if "अभी तक कोई बातचीत याद नहीं है" not in memory_context:
                                instructions = f"""{Reply_prompts}

[RECENT CONTEXT]
{memory_context}
[/CONTEXT]"""
                                print("[OK] Memory context injected")
                        except Exception as e:
                            print(f"[WARNING] Memory injection: {e}")
                    
                    print("[INFO] Sending instructions to LLM...")
                    await session.generate_reply(instructions=instructions)
                    print("[OK] Session completed successfully")
                    break
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    print(f"[WARNING] Reply error: {e}")
                    
                    if any(keyword in error_msg for keyword in ["timed out", "timeout", "connection", "websocket", "closed"]):
                        if retry_count < max_retries - 1:
                            retry_count += 1
                            wait_time = base_wait_time * retry_count
                            print(f"[INFO] Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                    raise
                
            except KeyboardInterrupt:
                print("\n[STOP] Agent stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] Session error: {e}")
                retry_count += 1
                
                if retry_count < max_retries:
                    wait_time = base_wait_time * retry_count
                    print(f"[INFO] Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    print("[ERROR] Max retries exceeded.")
                    raise


if name == "main":
    if check_console_mode():
        print("\n[CONSOLE MODE] LAUNCHING AGENT IN CONSOLE MODE\n")
        run_console_mode()
    else:
        print("\n[AGENT MODE] LAUNCHING LIVEKIT AGENT\n")
        
        try:
            gui_path = os.path.join(os.path.dirname(file), "jarvis_gui.py")
            if os.path.exists(gui_path):
                print("[INFO] Starting GUI in background...")
                subprocess.Popen([sys.executable, gui_path], stdout=None, stderr=None, stdin=None, close_fds=True)
                print("[OK] GUI launched\n")
        except Exception as e:
            print(f"[WARNING] GUI startup: {e}\n")

        print("[INFO] Starting LiveKit agent with microphone listening...\n")
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))