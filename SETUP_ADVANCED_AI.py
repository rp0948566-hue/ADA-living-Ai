"""
🤖 ADVANCED ADA AI SYSTEM - SETUP & CONFIGURATION GUIDE
Created: 2024-12-02
Version: 3.0 (Ultra-Advanced Intelligent AI)

This system provides:
✓ Full Computer Control (Window, Application Control)
✓ Advanced File Management (Create, Read, Write, Delete files)
✓ Screen Vision & OCR (Read and analyze screen content)
✓ Intelligent Code Generation (Python, HTML, JS, React, SQL)
✓ Real-time Memory System (Persistent conversation history)
✓ Smart Control (Keyboard, Mouse, System commands)
✓ Weather, Search, Google Integration
✓ Screenshot & Screen Analysis
"""

import os
import subprocess
import sys
from pathlib import Path

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                  ADVANCED ADA AI SYSTEM - SETUP WIZARD                         ║
║                              v3.0 ULTRA                                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

# Get project root
PROJECT_ROOT = Path(__file__).parent
VENV_PATH = PROJECT_ROOT / ".venv"
CREATED_FILES = PROJECT_ROOT / "created_files"
SCREENSHOTS = PROJECT_ROOT / "screenshots"

def print_step(step_num, message):
    """Print formatted step message"""
    print(f"\n[STEP {step_num}] 🔧 {message}")
    print("─" * 80)

def check_and_create_dirs():
    """Create necessary directories"""
    print_step(1, "Creating necessary directories...")
    
    dirs_to_create = [CREATED_FILES, SCREENSHOTS]
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created/Verified: {dir_path}")

def check_python():
    """Check Python installation"""
    print_step(2, "Checking Python installation...")
    
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✓ Python found: {version}")
        return True
    except Exception as e:
        print(f"✗ Python not found: {e}")
        return False

def check_venv():
    """Check virtual environment"""
    print_step(3, "Checking virtual environment...")
    
    if VENV_PATH.exists():
        print(f"✓ Virtual environment exists at: {VENV_PATH}")
        return True
    else:
        print(f"⚠ Virtual environment not found at: {VENV_PATH}")
        response = input("Create virtual environment now? (y/n): ").lower()
        if response == 'y':
            try:
                subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)], check=True)
                print(f"✓ Virtual environment created")
                return True
            except Exception as e:
                print(f"✗ Failed to create venv: {e}")
                return False
        return False

def check_tesseract():
    """Check Tesseract OCR installation"""
    print_step(4, "Checking Tesseract OCR installation...")
    
    try:
        result = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        print(f"✓ Tesseract OCR found")
        return True
    except:
        print("""
⚠ Tesseract OCR not found!

Tesseract is required for screen text extraction (OCR).

Installation instructions:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

On Windows:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run: tesseract-ocr-w64-setup-v5.x.exe
3. Install to default location

On macOS:
brew install tesseract

On Linux:
sudo apt-get install tesseract-ocr

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        return False

def show_features():
    """Display system features"""
    print_step(5, "Advanced Features Available")
    
    features = """
┌──────────────────────────────────────────────────────────────────────────────┐
│ 📁 FILE MANAGEMENT                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Create files: .py, .html, .js, .css, .json, .md, .txt, .sql, .java, etc   │
│ • Read file contents                                                         │
│ • Write/append to files                                                      │
│ • List all created files                                                     │
│ • Delete files                                                               │
│ • Open files in VS Code automatically                                        │
│                                                                              │
│ Example Commands:                                                            │
│   "Create a Python file called calculator.py"                               │
│   "Write HTML form with email and password fields"                           │
│   "Create React component for dashboard"                                     │
│   "Generate JavaScript API service"                                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🎥 SCREEN VISION & ANALYSIS                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Real-time screenshot capture                                               │
│ • OCR text extraction from screen                                            │
│ • UI element detection                                                       │
│ • Color analysis                                                             │
│ • Screen information retrieval                                               │
│ • Search for text on screen                                                  │
│ • Compare screenshots                                                        │
│                                                                              │
│ Example Commands:                                                            │
│   "Dekho screen pe kya likha hai" (Extract text from screen)                │
│   "Take a screenshot"                                                        │
│   "Analyze screen colors"                                                    │
│   "Find where the button is"                                                 │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 💻 INTELLIGENT CODE GENERATION                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ Supported Languages:                                                         │
│ • Python (functions, classes, decorators)                                    │
│ • HTML (forms, dashboards, templates)                                        │
│ • JavaScript (classes, API services)                                         │
│ • React (components with hooks)                                              │
│ • SQL (table creation, queries)                                              │
│ • Java, C++, Ruby, PHP, Go, Rust (basic templates)                          │
│                                                                              │
│ Example Commands:                                                            │
│   "Generate a Python function for sorting"                                   │
│   "Create HTML contact form"                                                 │
│   "Write React component for user profile"                                   │
│   "Generate JavaScript async function"                                       │
│   "Create database table for users"                                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🖥️ COMPUTER CONTROL                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Open/Close applications                                                    │
│ • Mouse control (move, click, scroll)                                        │
│ • Keyboard control (type, press keys, hotkeys)                               │
│ • Window management                                                          │
│ • System power control (restart, shutdown, lock)                             │
│ • Volume control                                                             │
│ • Gesture recognition                                                        │
│                                                                              │
│ Example Commands:                                                            │
│   "Open VS Code"                                                             │
│   "Click on the button at coordinates 500,300"                               │
│   "Type my name"                                                             │
│   "Press Alt+Tab"                                                            │
│   "Restart the system"                                                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🧠 MEMORY & CONVERSATION                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Persistent conversation history                                            │
│ • Memory after restart/power-off                                             │
│ • Smart context awareness                                                    │
│ • Conversation recall                                                        │
│ • Memory injection for better responses                                      │
│                                                                              │
│ Example Commands:                                                            │
│   "Remember this information"                                                │
│   "What did I ask you yesterday?"                                            │
│   "Recall our last conversation"                                             │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🌐 INTEGRATION & UTILITIES                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ • Google Search Integration                                                  │
│ • Weather Information                                                        │
│ • Current Date/Time                                                          │
│ • Web Browsing                                                               │
│ • Email & Calendar Integration (optional)                                    │
│ • Project File Reading                                                       │
│                                                                              │
│ Example Commands:                                                            │
│   "What's the weather today?"                                                │
│   "Search for Python tutorials"                                              │
│   "What time is it?"                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
    """
    print(features)

def show_quick_start():
    """Show quick start guide"""
    print_step(6, "Quick Start Guide")
    
    guide = """
1️⃣  ACTIVATE ENVIRONMENT (Windows PowerShell):
    & .venv\\Scripts\\Activate.ps1

2️⃣  INSTALL DEPENDENCIES:
    pip install -r requirements.txt

3️⃣  SET UP ENVIRONMENT VARIABLES:
    Create .env file with:
    LIVEKIT_URL=your_livekit_url
    LIVEKIT_API_KEY=your_api_key
    GOOGLE_API_KEY=your_google_key
    OPENAI_API_KEY=your_openai_key

4️⃣  START THE SYSTEM:
    python agent.py

5️⃣  INTERACTIVE COMMANDS:
    💬 Voice Commands:
       "ADA, banao Python file calculate.py"
       "Create HTML form"
       "Extract text from screen"
       "What's on my screen?"
       "Open VS Code"
       "Take screenshot"

🎯 SPECIAL FEATURES:
   • "ADA bazakiya mode on karo" - Funny/Witty mode
   • "ADA screenshot lo" - Capture screen
   • "ADA dekho screen pe kya likha hai" - Extract text
   • "ADA create a file" - File creation assistant
   • "ADA code generate karo" - Code generation
   • "ADA memory dikho" - Show past conversations
    """
    print(guide)

def show_file_structure():
    """Show project file structure"""
    print_step(7, "Project Structure")
    
    structure = f"""
ADA-ai/
├── agent.py                          [Main AI Agent Entry Point]
├── advanced_file_creator.py           [File Management Module]
├── advanced_screen_vision.py          [OCR & Screen Analysis]
├── advanced_code_generator.py         [Code Generation Engine]
├── Jarvis_prompts.py                  [AI Behavior & Personality]
├── Jarvis_screenshot.py               [Screenshot Tool]
├── Jarvis_google_search.py            [Search Integration]
├── Jarvis_window_CTRL.py              [Window Management]
├── Jarvis_file_opner.py               [File Operations]
├── keyboard_mouse_CTRL.py             [Input Control]
├── memory_interceptor.py              [Memory System]
├── off.py                             [System Power Control]
├── requirements.txt                   [Dependencies]
├── .env                               [Configuration]
├── .venv/                             [Virtual Environment]
├── memory/
│   ├── jarvis_memory.py               [Memory Module]
│   └── memory.json                    [Persistent Storage]
├── created_files/                     [Generated Files Storage]
└── screenshots/                       [Screenshot Storage]

Key Modules:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 advanced_file_creator.py
   ├─ create_file_tool() - Create files with templates
   ├─ read_file_tool() - Read file contents
   ├─ write_file_tool() - Write to files
   ├─ list_files_tool() - List created files
   ├─ delete_file_tool() - Delete files
   └─ open_file_tool() - Open in VS Code

🎥 advanced_screen_vision.py
   ├─ take_screenshot_tool() - Capture screenshots
   ├─ extract_screen_text_tool() - OCR text extraction
   ├─ analyze_screen_tool() - Full analysis
   ├─ search_screen_text_tool() - Find text
   ├─ get_screen_info_tool() - Screen details
   ├─ analyze_colors_tool() - Color detection
   └─ detect_ui_elements_tool() - Find buttons/elements

💻 advanced_code_generator.py
   ├─ generate_code_tool() - Universal code generator
   ├─ generate_python_function_tool() - Python functions
   ├─ generate_python_class_tool() - Python classes
   ├─ generate_html_form_tool() - HTML forms
   ├─ generate_react_component_tool() - React components
   └─ generate_javascript_api_tool() - API services

    """
    print(structure)

def show_dependencies():
    """Show dependency information"""
    print_step(8, "Dependencies Information")
    
    deps = """
CORE DEPENDENCIES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 LiveKit Packages:
   ✓ livekit-agents              - Core AI agent framework
   ✓ livekit-plugins-google      - Google integration (STT, TTS)
   ✓ livekit-plugins-openai      - OpenAI integration
   ✓ livekit-plugins-silero      - Voice detection

🟠 Computer Control:
   ✓ pyautogui                   - Mouse and keyboard automation
   ✓ pynput                       - Low-level input control
   ✓ pywin32                      - Windows API access

🟡 Vision & OCR:
   ✓ opencv-python (cv2)         - Computer vision
   ✓ pytesseract                 - OCR engine
   ✓ pillow                       - Image processing

🟢 Utilities:
   ✓ python-dotenv               - Environment variables
   ✓ requests                     - HTTP requests
   ✓ duckduckgo-search           - Web search
   ✓ SpeechRecognition           - Speech to text
   ✓ pyttsx3                      - Text to speech
   ✓ PySide6                      - GUI framework

🔵 Data Processing:
   ✓ langchain-community         - LLM tools
   ✓ numpy                       - Numerical computing
   ✓ fuzzywuzzy                  - String matching
   ✓ python-Levenshtein          - String distance

SYSTEM REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Python 3.8 or higher
• Windows 10/11 (Primary), macOS, or Linux
• 4GB RAM minimum
• Tesseract OCR installation (for vision features)
• Internet connection for cloud services
• Microphone for voice input
    """
    print(deps)

def main():
    """Main setup function"""
    try:
        show_setup_wizard()
        check_and_create_dirs()
        check_python()
        check_venv()
        check_tesseract()
        show_features()
        show_quick_start()
        show_file_structure()
        show_dependencies()
        
        print("\n" + "="*80)
        print("✅ SETUP COMPLETE!")
        print("="*80)
        print("""
🚀 NEXT STEPS:

1. Activate virtual environment:
   & .venv\\Scripts\\Activate.ps1

2. Install/upgrade dependencies:
   pip install -r requirements.txt --upgrade

3. Configure .env file with your API keys

4. Start the system:
   python agent.py

5. Interact with ADA:
   • Use voice commands
   • Create and manage files
   • Analyze your screen
   • Generate code
   • Control your computer

📚 For detailed documentation, visit the README files in each module.

Happy coding! 🎉
        """)
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
