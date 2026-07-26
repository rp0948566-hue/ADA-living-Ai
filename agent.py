from dotenv import load_dotenv
import asyncio
import datetime
import time
import traceback
import os
import builtins
import subprocess
import sys



from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    google,
    silero,
    noise_cancellation,
)
from Iris_prompts import Reply_prompts
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool, type_text_tool, press_key_tool, swipe_gesture_tool, press_hotkey_tool, control_volume_tool
load_dotenv()

# Hermes Agent — the "brain". Reasoning, memory, skills, and desktop-control
# tools (via the iris-tools MCP server, see tools/iris_mcp_server.py)
# all live in Hermes now; this process only handles voice I/O.
HERMES_API_BASE_URL = os.getenv("HERMES_API_BASE_URL", "http://127.0.0.1:8642/v1")
HERMES_API_KEY = os.getenv("API_SERVER_KEY")
HERMES_SESSION_KEY = os.getenv("HERMES_SESSION_KEY", "vikash-jarvis-desktop")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            # Persona lives in Hermes's SOUL.md now. Keep this minimal —
            # Hermes builds its own system prompt and treats anything passed
            # here as an ephemeral override layered on top of SOUL.md.
            instructions="You are Iris. Speak concisely.",
            tools=[
                # Mouse/keyboard/volume stay local for instant response —
                # everything else (apps, files, email, YouTube, weather,
                # camera) is handled by Hermes via the iris-tools MCP
                # bridge, not by LiveKit's own tool-calling loop.
                move_cursor_tool,
                mouse_click_tool,
                scroll_cursor_tool,
                type_text_tool,
                press_key_tool,
                press_hotkey_tool,
                control_volume_tool,
                swipe_gesture_tool,
            ]
        )


async def entrypoint(ctx: agents.JobContext):
    if not HERMES_API_KEY:
        raise RuntimeError(
            "API_SERVER_KEY is not set in .env — Hermes's local API server "
            "key is required to reach the brain at " + HERMES_API_BASE_URL
        )

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(),  # requires OPENAI_API_KEY in .env
        llm=openai.LLM(
            model="hermes-agent",
            base_url=HERMES_API_BASE_URL,
            api_key=HERMES_API_KEY,
            # Ties Hermes's long-term memory/user model to this desktop,
            # independent of the ephemeral per-request session id.
            extra_headers={"X-Hermes-Session-Key": HERMES_SESSION_KEY},
        ),
        tts=openai.TTS(),  # requires OPENAI_API_KEY in .env
    )

    # --- GUI orb sync: touch iris_data/ai_speaking.flag while Iris talks
    # so the HUD orb switches to its "AI speaking" color/motion mode.
    def _touch_ai_flag():
        try:
            data_dir = os.path.join(os.getcwd(), 'iris_data')
            os.makedirs(data_dir, exist_ok=True)
            with builtins.open(os.path.join(data_dir, 'ai_speaking.flag'), 'w') as f:
                f.write(str(time.time()))
        except Exception:
            pass

    async def _pulse_ai_flag():
        # keep refreshing the flag (orb treats <1.5s-old flag as "speaking")
        while getattr(session, 'agent_state', None) == 'speaking':
            _touch_ai_flag()
            await asyncio.sleep(0.5)

    @session.on("agent_state_changed")
    def _on_agent_state(ev):
        try:
            if getattr(ev, 'new_state', None) == 'speaking':
                _touch_ai_flag()
                asyncio.create_task(_pulse_ai_flag())
        except Exception:
            pass

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
            video_enabled=True
        ),
    )

    await ctx.connect()

    async def safe_generate_reply(sess, instructions, retries: int = 3, base_wait: float = 1.0) -> bool:
        """Try to call sess.generate_reply with retries and log failures to iris_data/realtime_errors.log.

        Returns True on success, False if all retries failed.
        """
        logdir = os.path.join(os.getcwd(), 'iris_data')
        os.makedirs(logdir, exist_ok=True)
        logpath = os.path.join(logdir, 'realtime_errors.log')

        for attempt in range(1, retries + 1):
            try:
                await sess.generate_reply(instructions=instructions)
                return True
            except Exception as e:
                tb = traceback.format_exc()
                ts = datetime.datetime.now().isoformat()
                entry = f"[{ts}] generate_reply attempt={attempt} error={e}\n{tb}\n"
                try:
                    with builtins.open(logpath, 'a', encoding='utf-8') as lf:
                        lf.write(entry)
                except Exception:
                    # best-effort write
                    pass
                print(f"[agent] generate_reply attempt {attempt} failed: {e}")
                if attempt < retries:
                    await asyncio.sleep(base_wait * attempt)
        return False

    ok = await safe_generate_reply(session, Reply_prompts)
    if not ok:
        print("Failed to generate initial reply after retries. See iris_data/realtime_errors.log for details.")

if __name__ == "__main__":
    # Best-effort: start the GUI when the agent is launched so the user sees the interface.
    def start_gui_if_needed():
        try:
            data_dir = os.path.join(os.getcwd(), 'iris_data')
            os.makedirs(data_dir, exist_ok=True)
            lock_path = os.path.join(data_dir, 'gui_running.lock')
            log_path = os.path.join(data_dir, 'gui_launch.log')

            # If a lock exists, assume GUI already running
            if os.path.exists(lock_path):
                return

            # Prefer pythonw from venv, then system pythonw, else fallback to sys.executable
            pythonw = None
            venv_pythonw = os.path.join(os.getcwd(), '.venv', 'Scripts', 'pythonw.exe')
            if os.path.exists(venv_pythonw):
                pythonw = venv_pythonw
            else:
                sibling_pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
                if os.path.exists(sibling_pythonw):
                    pythonw = sibling_pythonw
                else:
                    pythonw = sys.executable

            gui_script = os.path.join(os.getcwd(), 'iris_gui.py')
            env = os.environ.copy()

            try:
                lf = builtins.open(log_path, 'a', encoding='utf-8', errors='replace')
            except Exception:
                lf = None

            creation_flags = 0
            try:
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            except Exception:
                creation_flags = 0

            try:
                if lf:
                    subprocess.Popen([pythonw, gui_script], cwd=os.getcwd(), env=env,
                                     stdout=lf, stderr=lf, close_fds=True, creationflags=creation_flags)
                else:
                    subprocess.Popen([pythonw, gui_script], cwd=os.getcwd(), env=env,
                                     close_fds=True, creationflags=creation_flags)
                # write a lock file so we don't spawn duplicates
                try:
                    with builtins.open(lock_path, 'w', encoding='utf-8') as lk:
                        lk.write(str(os.getpid()))
                except Exception:
                    pass
            except Exception as e:
                try:
                    if lf:
                        lf.write(f"Failed to spawn GUI: {e}\n")
                except Exception:
                    pass
        except Exception:
            pass

    try:
        start_gui_if_needed()
    except Exception:
        pass

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

