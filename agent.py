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

# 🔗 LINK TO USER TONE AI INTERACTION MODULE
# Edit user_tone_ai_interaction.py for advanced user tone handling and liveliness features
# This module adds dynamic responses to make the AI feel more alive and interactive
# Integration: Import and use handle_user_tone() in response generation

# 1. PROMPTS & BEHAVIOR
from Jarvis_prompts import behavior_prompts, get_reply_prompts

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

# 6A. RANDOMIZED TONE ADAPTER (v2.3 - Dynamic Abuse Randomizer)
try:
    from tone_adapter import ToneAdapter
except (ImportError, AttributeError, SyntaxError):
    ToneAdapter = None

# 7. WINDOWS POWER CONTROL
from windows_power_ctrl import shutdown_pc, restart_pc, lock_screen, sleep_pc, lock_pc

# 7A. WHATSAPP MESSAGING
try:
    from whatsapp_sender import send_whatsapp_message, WhatsAppSender
    from whatsapp_message_generator import generate_whatsapp_message, AIMessageGenerator
    from whatsapp_tools import send_whatsapp_tool, generate_whatsapp_message_tool, get_whatsapp_info_tool, WHATSAPP_TOOLS
except (ImportError, AttributeError, SyntaxError):
    send_whatsapp_message = None
    WhatsAppSender = None
    generate_whatsapp_message = None
    AIMessageGenerator = None
    send_whatsapp_tool = None
    generate_whatsapp_message_tool = None
    get_whatsapp_info_tool = None
    WHATSAPP_TOOLS = []

# 7B. ADVANCED WHATSAPP + SCREEN SHARING
try:
    from whatsapp_advanced_control import send_whatsapp_message_advanced, check_whatsapp_status
    from screen_sharing_system import (
        start_screen_share_voice,
        stop_screen_share_voice,
        get_screen_share_status,
        get_screen_share_summary
    )
    from whatsapp_screen_tools import (
        open_and_send_whatsapp_tool,
        check_whatsapp_status_tool,
        start_screen_share_tool,
        stop_screen_share_tool,
        get_screen_share_status_tool,
        get_screen_share_summary_tool,
        ALL_ADVANCED_TOOLS
    )
except (ImportError, AttributeError, SyntaxError):
    send_whatsapp_message_advanced = None
    check_whatsapp_status = None
    start_screen_share_voice = None
    stop_screen_share_voice = None
    get_screen_share_status = None
    get_screen_share_summary = None
    open_and_send_whatsapp_tool = None
    check_whatsapp_status_tool = None
    start_screen_share_tool = None
    stop_screen_share_tool = None
    get_screen_share_status_tool = None
    get_screen_share_summary_tool = None
    ALL_ADVANCED_TOOLS = []

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

# 8A. ORCHESTRATION SYSTEM - CONTINUOUS LEARNING IN BACKGROUND
try:
    from autonomous_orchestrator import run_orchestrator_async
    from agent_learning import AgentLearningTools
except (ImportError, AttributeError, SyntaxError):
    run_orchestrator_async = None
    AgentLearningTools = None

# 8B. RANDOM TOPIC MEMORY SYSTEM - Auto-save, auto-update
try:
    from random_topic_memory import (
        generate_random_topic, save_topic_to_memory, get_random_saved_topic,
        search_topics, get_memory_stats, auto_update_memory,
        MemoryEvolutionEngine, TOPIC_MEMORY_TOOLS
    )
except (ImportError, AttributeError, SyntaxError):
    generate_random_topic = None
    save_topic_to_memory = None
    get_random_saved_topic = None
    search_topics = None
    get_memory_stats = None
    auto_update_memory = None
    MemoryEvolutionEngine = None
    TOPIC_MEMORY_TOOLS = []

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

try:
    from diagnose_api import diagnose_system
except (ImportError, AttributeError, SyntaxError):
    diagnose_system = None

try:
    from ADA_vs_code_file_accase import access_ada_files
except (ImportError, AttributeError, SyntaxError):
    access_ada_files = None

try:
    from verify_system import verify_system_setup
except (ImportError, AttributeError, SyntaxError):
    verify_system_setup = None

# 11. SETUP & CONFIGURATION
try:
    from SETUP_ADVANCED_AI import setup_system
except (ImportError, AttributeError, SyntaxError):
    setup_system = None

try:
    from COMPLETE_FEATURE_GUIDE import FEATURE_GUIDE
except (ImportError, AttributeError, SyntaxError):
    FEATURE_GUIDE = None

try:
    from INSTALLATION_CHECKLIST import check_installation
except (ImportError, AttributeError, SyntaxError):
    check_installation = None

# 12. OPTIONAL TOOLS (Import with fallback)
try:
    from off import shutdown_system
except (ImportError, SyntaxError):
    shutdown_system = None

try:
    from run_screenshot_test import run_screenshot_test
except (ImportError, SyntaxError):
    run_screenshot_test = None

try:
    from personality_enhancer import get_personality_prompt
except (ImportError, SyntaxError):
    get_personality_prompt = None

# 🔗 INTEGRATION: User Tone AI Interaction for enhanced liveliness
try:
    from user_tone_ai_interaction import handle_user_tone, add_liveliness, get_emotional_response
except (ImportError, SyntaxError):
    handle_user_tone = None
    add_liveliness = None
    get_emotional_response = None

try:
    from test_memory_direct import test_memory
except (ImportError, SyntaxError):
    test_memory = None

try:
    from test_memory_retrieve import retrieve_memory_test
except (ImportError, SyntaxError):
    retrieve_memory_test = None

try:
    from testing import run_tests
except (ImportError, SyntaxError):
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
        # Build complete tool list - only include tools that are proper LiveKit agent tools
        # Filter tools to only include instances of agents.Tool or properly decorated functions
        tools = []

        # Helper function to check if something is a valid LiveKit tool
        def is_valid_tool(obj):
            """Check if object is a valid LiveKit agent tool"""
            if obj is None:
                return False
            # Check if it's an instance of agents.Tool or has agent metadata
            return hasattr(obj, '__self__') and hasattr(obj.__self__, '_tool') or \
                   isinstance(obj, agents.Tool) or \
                   hasattr(obj, '__call__') and hasattr(obj, 'metadata')

        # Add core tools (must verify these are properly decorated in their modules)
        # For now, we'll use a minimal tool set to fix the "unknown tool type" error
        # and gradually add tools as we verify they're properly decorated

        # Start with search and information tools
        if google_search is not None:
            try:
                tools.append(google_search)
            except Exception as e:
                print(f"⚠️ Could not add google_search: {e}")

        if get_current_datetime is not None:
            try:
                tools.append(get_current_datetime)
            except Exception as e:
                print(f"⚠️ Could not add get_current_datetime: {e}")

        if get_weather is not None:
            try:
                tools.append(get_weather)
            except Exception as e:
                print(f"⚠️ Could not add get_weather: {e}")

        # Add memory tools if available
        if get_recent_conversations is not None:
            try:
                tools.append(get_recent_conversations)
            except Exception as e:
                print(f"⚠️ Could not add get_recent_conversations: {e}")

        # Add backend knowledge tools
        if get_backend_knowledge is not None:
            try:
                tools.append(get_backend_knowledge)
            except Exception as e:
                print(f"⚠️ Could not add get_backend_knowledge: {e}")

        if get_search_knowledge is not None:
            try:
                tools.append(get_search_knowledge)
            except Exception as e:
                print(f"⚠️ Could not add get_search_knowledge: {e}")

        # Add file management tools
        if create_file_tool is not None:
            try:
                tools.append(create_file_tool)
            except Exception as e:
                print(f"⚠️ Could not add create_file_tool: {e}")

        if screenshot_tool is not None:
            try:
                tools.append(screenshot_tool)
            except Exception as e:
                print(f"⚠️ Could not add screenshot_tool: {e}")

        # Add input control tools
        if type_text_tool is not None:
            try:
                tools.append(type_text_tool)
            except Exception as e:
                print(f"⚠️ Could not add type_text_tool: {e}")

        if press_key_tool is not None:
            try:
                tools.append(press_key_tool)
            except Exception as e:
                print(f"⚠️ Could not add press_key_tool: {e}")

        # Add power control tools - these are critical
        if shutdown_pc is not None:
            try:
                tools.append(shutdown_pc)
            except Exception as e:
                print(f"⚠️ Could not add shutdown_pc: {e}")

        if restart_pc is not None:
            try:
                tools.append(restart_pc)
            except Exception as e:
                print(f"⚠️ Could not add restart_pc: {e}")

        if lock_screen is not None:
            try:
                tools.append(lock_screen)
            except Exception as e:
                print(f"⚠️ Could not add lock_screen: {e}")

        if sleep_pc is not None:
            try:
                tools.append(sleep_pc)
            except Exception as e:
                print(f"⚠️ Could not add sleep_pc: {e}")

        # Add WhatsApp messaging tools
        if send_whatsapp_tool is not None:
            try:
                tools.append(send_whatsapp_tool)
            except Exception as e:
                print(f"⚠️ Could not add send_whatsapp_tool: {e}")

        if generate_whatsapp_message_tool is not None:
            try:
                tools.append(generate_whatsapp_message_tool)
            except Exception as e:
                print(f"⚠️ Could not add generate_whatsapp_message_tool: {e}")

        if get_whatsapp_info_tool is not None:
            try:
                tools.append(get_whatsapp_info_tool)
            except Exception as e:
                print(f"⚠️ Could not add get_whatsapp_info_tool: {e}")

        # Add Advanced WhatsApp + Screen Sharing tools
        if open_and_send_whatsapp_tool is not None:
            try:
                tools.append(open_and_send_whatsapp_tool)
            except Exception as e:
                print(f"⚠️ Could not add open_and_send_whatsapp_tool: {e}")

        if check_whatsapp_status_tool is not None:
            try:
                tools.append(check_whatsapp_status_tool)
            except Exception as e:
                print(f"⚠️ Could not add check_whatsapp_status_tool: {e}")

        if start_screen_share_tool is not None:
            try:
                tools.append(start_screen_share_tool)
            except Exception as e:
                print(f"⚠️ Could not add start_screen_share_tool: {e}")

        if stop_screen_share_tool is not None:
            try:
                tools.append(stop_screen_share_tool)
            except Exception as e:
                print(f"⚠️ Could not add stop_screen_share_tool: {e}")

        if get_screen_share_status_tool is not None:
            try:
                tools.append(get_screen_share_status_tool)
            except Exception as e:
                print(f"⚠️ Could not add get_screen_share_status_tool: {e}")

        if get_screen_share_summary_tool is not None:
            try:
                tools.append(get_screen_share_summary_tool)
            except Exception as e:
                print(f"⚠️ Could not add get_screen_share_summary_tool: {e}")

        # Add Topic Memory tools
        if TOPIC_MEMORY_TOOLS:
            for tool in TOPIC_MEMORY_TOOLS:
                try:
                    tools.append(tool)
                except Exception as e:
                    print(f"⚠️ Could not add topic memory tool: {e}")

        # Initialize Randomized Tone Adapter (v2.3)
        self.tone_adapter = None
        if ToneAdapter is not None:
            try:
                self.tone_adapter = ToneAdapter(model='llama3.1')
                print("✅ Loaded Randomized Adaptive Tone Module v2.3 – Fresh Abuse Every Time! 🎲")
            except Exception as e:
                print(f"⚠️ Could not initialize ToneAdapter: {e}")
                self.tone_adapter = None

        print(f"✅ Loaded {len(tools)} tools for ADA Agent")

        super().__init__(instructions=behavior_prompts, tools=tools)

    async def on_message(self, message: str, session: AgentSession) -> None:
        """Handle incoming messages and apply tone handling for abusive responses"""
        # Apply tone handling to each message for realtime abusive responses
        if handle_user_tone:
            try:
                tone_response = handle_user_tone(message)
                # Inject the tone response into the session instructions for this message
                enhanced_instructions = f"{self.instructions}\n\n[TONE RESPONSE]\n{tone_response}\n[/TONE RESPONSE]"
                # Update the session's instructions temporarily for this response
                session.llm.instructions = enhanced_instructions
                print(f"🎭 Applied tone response for message: {message[:50]}...")
            except Exception as e:
                print(f"⚠️ Tone handling failed for message: {e}")
                # Fall back to original instructions
                session.llm.instructions = self.instructions
        else:
            session.llm.instructions = self.instructions


async def entrypoint(ctx: agents.JobContext):
    """Entry point for LiveKit agent session with improved error handling"""
    
    # ═════════════════════════════════════════════════════════════════════════════════
    # 🧠 START RANDOM TOPIC MEMORY EVOLUTION ENGINE
    # ═════════════════════════════════════════════════════════════════════════════════
    evolution_engine = None
    memory_process = None
    if MemoryEvolutionEngine is not None:
        try:
            print("\n🧠 Launching Random Topic Memory Evolution Engine...")
            evolution_engine = MemoryEvolutionEngine(auto_upgrade_interval=1800)  # Update every 30 minutes
            evolution_engine.start_background_evolution()
            print("✓ Memory evolution engine active - Auto-update running")

            # Also start random_topic_memory.py in a new process
            print("\n🧠 Starting Random Topic Memory System in new terminal...")
            memory_process = subprocess.Popen([sys.executable, "random_topic_memory.py"], stdout=None, stderr=None, stdin=None, close_fds=True)
            print("✓ Random Topic Memory System started in background")
        except Exception as e:
            print(f"⚠️  Could not start memory evolution engine: {e}")
            evolution_engine = None
            memory_process = None
    
    # ═════════════════════════════════════════════════════════════════════════════════
    # 🎯 START ORCHESTRATION SYSTEM - Continuous Learning in Background
    # ═════════════════════════════════════════════════════════════════════════════════
    orchestrator_thread = None
    orchestrator_obj = None
    
    if run_orchestrator_async is not None:
        try:
            print("\n📚 Launching Autonomous Orchestrator System...")
            print("   ├─ Initializing learning systems")
            print("   ├─ Starting background threads")
            print("   └─ Entering endless learning loop")
            orchestrator_thread, orchestrator_obj = run_orchestrator_async(daemon=True)
            print("✓ Orchestrator active - All learning systems running in background")
            print("  → Learning will continue automatically until agent stops\n")
        except Exception as e:
            print(f"⚠️  Could not start orchestrator: {e}")
            orchestrator_thread = None
            orchestrator_obj = None
    
    # ═════════════════════════════════════════════════════════════════════════════════
    
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
                instructions = get_reply_prompts()

                if ENABLE_MEMORY_INTERCEPTOR:
                    try:
                        print("🧠 Fetching memory context...")
                        # Fetch recent conversations to inject context
                        memory_context = await get_recent_conversations(limit=5)  # Reduced from 10

                        # Only inject if there's actual memory, keep it brief
                        if "अभी तक कोई बातचीत याद नहीं है" not in memory_context:
                            instructions = f"""{get_reply_prompts()}

[RECENT CONTEXT]
{memory_context}
[/CONTEXT]"""
                            print("✅ Memory context injected")
                        else:
                            instructions = get_reply_prompts()
                            print("ℹ️ No previous conversations to inject")
                    except Exception as e:
                        print(f"⚠️ Memory injection skipped: {e}")
                        instructions = get_reply_prompts()
                
                # ✨ Inject a bit of personality to feel more alive
                if get_personality_prompt:
                    try:
                        personality_injection = get_personality_prompt()
                        instructions = f"{instructions}\n\n[PERSONALITY INSTRUCTION]\n{personality_injection}\n[/PERSONALITY INSTRUCTION]"
                        print(f"✨ Personality injected: {personality_injection}")
                    except Exception as e:
                        print(f"⚠️ Personality injection failed: {e}")

                # 🔗 INTEGRATION: Enhanced liveliness from user_tone_ai_interaction
                if add_liveliness:
                    try:
                        liveliness_boost = add_liveliness()
                        instructions = f"{instructions}\n\n[LIVELINESS BOOST]\n{liveliness_boost}\n[/LIVELINESS BOOST]"
                        print(f"🚀 Liveliness boosted: {liveliness_boost}")
                    except Exception as e:
                        print(f"⚠️ Liveliness boost failed: {e}")

                # 🔗 INTEGRATION: User tone handling with abusive responses
                if handle_user_tone:
                    try:
                        # Get user input from context (assuming it's available)
                        user_input = getattr(ctx, 'user_input', '') or getattr(ctx.room, 'last_message', '')
                        if user_input:
                            tone_response = handle_user_tone(user_input)
                            instructions = f"{instructions}\n\n[TONE RESPONSE]\n{tone_response}\n[/TONE RESPONSE]"
                            print(f"🎭 Tone response added: {tone_response}")
                    except Exception as e:
                        print(f"⚠️ Tone response failed: {e}")

                print("📡 Sending instructions to LLM (this may take a moment)...")
                
                # ═════════════════════════════════════════════════════════════════════════════════
                # 🎯 ADVANCED RANDOMIZED TONE ADAPTATION (v2.3) - Always On for All Features!
                # ═════════════════════════════════════════════════════════════════════════════════
                if hasattr(ctx, 'agent') and hasattr(ctx.agent, 'tone_adapter') and ctx.agent.tone_adapter:
                    try:
                        # Enhanced: Always apply tone adaptation to ALL responses for richer interactions
                        print("🎲 Applying Advanced Tone Adaptation to ALL Features...")
                        tone_result = ctx.agent.tone_adapter.adaptive_chat(
                            user_input=user_input or "Generate response with advanced randomized tone",
                            conversation_history=[]
                        )

                        # Advanced logging for all tones, not just playful_abuse
                        if tone_result.get('roast_level'):
                            import random
                            random_sass = random.choice(['Banchod wild!', 'Mader chode fresh!', 'Had may rahana random!', 'Global sass unleashed!'])
                            print(f"   🔥 Advanced Tone Activated: {tone_result['tone']} ({tone_result['roast_level']}) – {random_sass}")
                            print(f"   📊 Freedom Score: {tone_result.get('freedom_score', 0):.2f}/1.0")
                            print(f"   🎨 Creativity Score: {tone_result.get('creativity_score', 0):.2f}/1.0")
                            print(f"   🔄 Adaptability Score: {tone_result.get('adaptability_score', 0):.2f}/1.0")
                            print(f"   🌍 Global Tone Mix: {tone_result.get('global_tone_mix', 'Active')}")
                    except Exception as e:
                        print(f"   ⚠️ Advanced Tone adaptation skipped: {e}")
                
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
    
    # ═════════════════════════════════════════════════════════════════════════════════
    # 🛑 CLEANUP - Save learning memory and stop evolution on shutdown
    # ═════════════════════════════════════════════════════════════════════════════════
    
    # Stop evolution engine
    if evolution_engine is not None:
        try:
            evolution_engine.stop_background_evolution()
            print("✓ Memory evolution engine stopped")
        except Exception as e:
            print(f"⚠️ Could not stop evolution engine: {e}")
    
    if AgentLearningTools is not None:
        try:
            print("\n💾 Saving learning memory before shutdown...")
            AgentLearningTools.save_learning_memory()
            print("✓ Learning memory saved successfully")
        except Exception as e:
            print(f"⚠️ Could not save learning memory: {e}")
    
    # ═════════════════════════════════════════════════════════════════════════════════


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