    """
Agent Brain - Master Mind Voice Control System
==============================================

AI brain that controls voice physics in real-time based on context.
Simulates intelligent voice modulation for different emotional states.

Features:
- Context-aware voice physics selection
- Internal thoughts vs spoken text display
- Real-time voice synthesis control
- Windows terminal color output

Author: Senior Python Developer
Target: Windows 10/11
"""

import time
import random
from colorama import init, Fore, Back, Style
from neuro_voice import NeuroVoiceEngine

# Initialize colorama for Windows terminal colors
init(autoreset=True)

class AgentBrain:
    """
    Master Mind AI brain with voice physics control.
    """

    def __init__(self):
        """Initialize the AI brain with voice engine."""
        self.voice_engine = NeuroVoiceEngine()
        self.context_history = []

    def think_and_speak(self, context: str, message: str):
        """
        Process context and generate appropriate voice response.

        Args:
            context (str): Emotional/context state (e.g., 'secret', 'angry', 'happy')
            message (str): Text to speak
        """
        # Determine voice physics based on context
        physics = self._get_physics_for_context(context)

        # Display internal thoughts (AI processing)
        self._display_internal_thoughts(context, physics, message)

        # Speak with physics
        self.voice_engine.generate_and_play(message, physics)

        # Update context history
        self.context_history.append({
            'context': context,
            'message': message,
            'physics': physics,
            'timestamp': time.time()
        })

    def _get_physics_for_context(self, context: str) -> dict:
        """
        Determine voice physics parameters based on context.

        Returns:
            dict: Physics parameters (pitch, softness, gain)
        """
        context = context.lower()

        # Base physics configurations
        physics_configs = {
            'normal': {'pitch': 1.0, 'softness': 10000, 'gain': 0},
            'secret': {'pitch': 1.1, 'softness': 3000, 'gain': -5},  # Whisper effect
            'angry': {'pitch': 0.8, 'softness': 15000, 'gain': 5},  # Demonic/hard
            'happy': {'pitch': 1.2, 'softness': 12000, 'gain': 2},  # Cheerful
            'sad': {'pitch': 0.9, 'softness': 6000, 'gain': -3},  # Muffled
            'excited': {'pitch': 1.3, 'softness': 14000, 'gain': 3},  # Energetic
            'calm': {'pitch': 0.95, 'softness': 8000, 'gain': -2},  # Soft
            'mysterious': {'pitch': 0.85, 'softness': 4000, 'gain': -1},  # Deep whisper
            'confident': {'pitch': 0.95, 'softness': 11000, 'gain': 1},  # Strong
            'scared': {'pitch': 1.4, 'softness': 5000, 'gain': -4},  # High and soft
        }

        # Get base config or default to normal
        base_physics = physics_configs.get(context, physics_configs['normal'])

        # Add slight randomization for natural variation
        physics = {
            'pitch': base_physics['pitch'] * random.uniform(0.95, 1.05),
            'softness': int(base_physics['softness'] * random.uniform(0.9, 1.1)),
            'gain': base_physics['gain'] + random.randint(-1, 1)
        }

        # Ensure bounds
        physics['pitch'] = max(0.5, min(2.0, physics['pitch']))
        physics['softness'] = max(100, min(20000, physics['softness']))
        physics['gain'] = max(-20, min(20, physics['gain']))

        return physics

    def _display_internal_thoughts(self, context: str, physics: dict, message: str):
        """
        Display AI's internal processing in colored terminal output.
        """
        print(f"\n{Fore.CYAN}🧠 MASTER MIND INTERNAL PROCESSING:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Context: {context.upper()}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Physics: Pitch={physics['pitch']:.2f}, Softness={physics['softness']}, Gain={physics['gain']}dB{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Planning to speak: \"{message}\"{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Initiating voice synthesis...{Style.RESET_ALL}\n")

        # Show spoken text in different color
        print(f"{Fore.RED}🎤 SPEAKING:{Style.RESET_ALL} {Back.WHITE}{Fore.BLACK}\"{message}\"{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Voice physics applied. Listening for response...{Style.RESET_ALL}\n")

def run_simulation():
    """
    Run a simulation of the Master Mind voice system.
    """
    brain = AgentBrain()

    # Simulation scenarios
    scenarios = [
        ("normal", "Hello, I am the Master Mind AI."),
        ("secret", "I have a secret to tell you..."),
        ("angry", "You have angered the system!"),
        ("happy", "I'm so excited to meet you!"),
        ("sad", "This makes me feel very sad..."),
        ("excited", "This is absolutely incredible!"),
        ("calm", "Let us proceed calmly and rationally."),
        ("mysterious", "The shadows hold many secrets..."),
        ("confident", "I am completely confident in this decision."),
        ("scared", "I'm frightened by this development..."),
    ]

    print(f"{Fore.GREEN}🎭 MASTER MIND VOICE SYNTHESIS SIMULATION{Style.RESET_ALL}")
    print(f"{Fore.GREEN}=========================================={Style.RESET_ALL}\n")

    for context, message in scenarios:
        brain.think_and_speak(context, message)
        time.sleep(2)  # Pause between scenarios

    print(f"\n{Fore.GREEN}Simulation complete. Master Mind voice control demonstrated.{Style.RESET_ALL}")

if __name__ == "__main__":
    run_simulation()
