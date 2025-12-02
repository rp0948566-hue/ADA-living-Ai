# 🤖 ADVANCED ADA AI SYSTEM v3.0

**The World's Most Intelligent & Powerful Personal AI Assistant**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Usage Examples](#usage-examples)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

ADA AI is an advanced, voice-activated intelligent assistant designed to provide complete control over your computer, generate code, analyze your screen, and manage files - all through natural language conversation.

Built on **LiveKit's Real-time AI Framework** and powered by **Google's Advanced LLM**, ADA combines:
- ✅ Real-time voice interaction
- ✅ Full computer control
- ✅ Advanced file management
- ✅ Screen vision & OCR
- ✅ Intelligent code generation
- ✅ Persistent memory system

---

## ✨ Key Features

### 1. 📁 **Advanced File Management**
```
✓ Create files (.py, .html, .js, .css, .json, .md, .sql, etc.)
✓ Read file contents
✓ Write/append to existing files
✓ List all created files
✓ Delete files
✓ Auto-open in VS Code
✓ Intelligent templates for each file type
```

**Commands:**
```
"Create a Python file called app.py"
"Write HTML form with email field"
"Generate React component for dashboard"
"Open file in VS Code"
```

### 2. 🎥 **Screen Vision & OCR Analysis**
```
✓ Real-time screenshot capture
✓ OCR text extraction (Tesseract)
✓ UI element detection
✓ Color analysis & detection
✓ Screen information retrieval
✓ Search for text on screen
✓ Screenshot comparison
```

**Commands:**
```
"Take a screenshot"
"What's written on my screen?"
"Find the login button"
"Extract all text from screen"
"Analyze screen colors"
```

### 3. 💻 **Intelligent Code Generation**

Supports: Python, HTML, JavaScript, React, SQL, Java, C++, Go, Rust

```python
# Example: Generate Python function
generate_code_tool(
    language='python',
    code_type='function',
    name='calculate_average',
    description='Calculate average of numbers'
)

# Example: Generate HTML Form
generate_code_tool(
    language='html',
    code_type='form',
    name='Contact Form',
    fields=['name', 'email', 'message']
)

# Example: Generate React Component
generate_code_tool(
    language='react',
    code_type='component',
    name='UserProfile',
    description='Display user profile information'
)
```

**Commands:**
```
"Generate Python function for sorting"
"Create HTML contact form"
"Write React component for dashboard"
"Generate JavaScript API service"
"Create SQL table for users"
```

### 4. 🖥️ **Full Computer Control**
```
✓ Open/Close applications
✓ Mouse control (move, click, double-click, scroll)
✓ Keyboard control (type, press keys, hotkeys)
✓ Window management
✓ System power control (restart, shutdown, lock)
✓ Volume control
✓ Gesture recognition
```

**Commands:**
```
"Open VS Code"
"Click on the button"
"Type my password"
"Press Alt+Tab"
"Restart the system"
"Scroll down"
"Take a screenshot"
```

### 5. 🧠 **Smart Memory System**
```
✓ Persistent conversation history
✓ Memory survives restarts
✓ Context-aware responses
✓ Conversation recall
✓ Automatic memory injection
✓ Smart context retrieval
```

**Commands:**
```
"Do you remember what I said?"
"What did we talk about yesterday?"
"Remember this password"
"Recall our last conversation"
```

### 6. 🌐 **Integration & Utilities**
```
✓ Google Search
✓ Weather Information
✓ Current Date/Time
✓ Web Browsing
✓ Project File Reading
✓ System Monitoring
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Windows 10/11 (or macOS/Linux)
- 4GB RAM minimum
- Internet connection

### Step 1: Clone/Download Project
```bash
cd C:\Users\YOUR_NAME\Desktop
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows PowerShell:**
```powershell
& .venv\Scripts\Activate.ps1
```

**Windows CMD:**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (choose default path)
3. Add to Python code if needed:
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Step 6: Configure Environment Variables

Create `.env` file in project root:
```env
LIVEKIT_URL=your_livekit_server_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret

GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
WEATHER_API_KEY=your_weather_api_key
```

### Step 7: Run Setup Script
```bash
python SETUP_ADVANCED_AI.py
```

---

## ⚡ Quick Start

### Start the System
```bash
python agent.py
```

### Basic Voice Commands

#### File Creation
```
"Create Python file calculator.py"
"Generate HTML form with email and password"
"Write React component for user dashboard"
"Create JavaScript API service"
```

#### Screen Analysis
```
"Take a screenshot"
"What's on my screen?"
"Extract text from screen"
"Find the login button"
"Analyze colors on screen"
```

#### Computer Control
```
"Open VS Code"
"Click at coordinates 500, 300"
"Type my name"
"Press Enter"
"Scroll down"
```

#### Memory
```
"Remember my name is John"
"What did I ask yesterday?"
"Show my conversation history"
```

---

## 📚 Usage Examples

### Example 1: Create a Python Web Server
```
User: "ADA, create a Python file for a simple web server"

ADA Response:
✓ File created: server.py
✓ Opening in VS Code...

[Generated code with Flask/HTTP server template]
```

### Example 2: Generate HTML Form
```
User: "Create an HTML form with name, email, and message fields"

ADA Response:
✓ HTML file created: contact_form.html
✓ With styling and responsive design
✓ Auto-opened in VS Code

[Generated responsive HTML form with CSS]
```

### Example 3: Extract Screen Text
```
User: "What text is visible on my screen right now?"

ADA Response:
✓ Analyzing screen...
✓ Using Tesseract OCR...

[Lists all detected text with confidence scores]
```

### Example 4: Generate React Component
```
User: "Create a React component for displaying user profile"

ADA Response:
✓ React component generated
✓ File: user_profile.jsx

[Generated component with hooks and styling]
```

### Example 5: Control Computer
```
User: "Open VS Code and create a new file called app.py"

ADA Response:
✓ Opening VS Code...
✓ Creating new file...
✓ File created: app.py

[Both actions completed]
```

---

## 🏗️ Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────┐
│          Voice Input (Google STT)                    │
└────────────────┬────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────┐
│       LiveKit Real-time AI Agent (Agent.py)          │
│  - Processes voice input                             │
│  - Routes to appropriate tools                       │
│  - Manages context & memory                          │
└──────────┬─────────────────────────────────────────┬─┘
           │                                         │
    ┌──────▼────────┐                   ┌───────────▼──────┐
    │ Tool Router   │                   │ Memory System    │
    └──────┬────────┘                   └──────────────────┘
           │
    ┌──────┴──────────────────────────────────────┐
    │                                              │
┌───▼──────────┐  ┌──────────────┐  ┌────────────▼──┐
│ File Creator │  │Screen Vision │  │Code Generator │
│              │  │              │  │               │
│- Create      │  │- OCR         │  │- Python       │
│- Read        │  │- Screenshot  │  │- HTML         │
│- Write       │  │- Analyze     │  │- JavaScript   │
│- Delete      │  │- UI Detect   │  │- React        │
│- List        │  │- Colors      │  │- SQL          │
└───┬──────────┘  └──────────────┘  └────────────┬──┘
    │                                              │
    └──────────────────┬──────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    ┌───▼─────────────┐    ┌──────────▼────┐
    │ Computer Control│    │Other Utilities │
    │                 │    │                │
    │- Mouse          │    │- Google Search │
    │- Keyboard       │    │- Weather       │
    │- Windows        │    │- Date/Time     │
    │- System Power   │    │- Web Browse    │
    └───┬─────────────┘    └────────────────┘
        │
┌───────▼──────────────────────────────────────┐
│      Voice Output (Google TTS)                │
└───────────────────────────────────────────────┘
```

### Module Structure
```
ADA-ai/
├── agent.py                      (Main agent with all tools)
├── advanced_file_creator.py      (File management)
├── advanced_screen_vision.py     (OCR & vision)
├── advanced_code_generator.py    (Code generation)
├── Jarvis_prompts.py             (AI personality)
├── keyboard_mouse_CTRL.py        (Input control)
├── Jarvis_window_CTRL.py         (Window control)
├── memory/
│   └── jarvis_memory.py          (Persistent memory)
├── created_files/                (Generated files storage)
├── screenshots/                  (Screenshot storage)
└── requirements.txt              (Dependencies)
```

---

## 📖 API Reference

### File Creator Tools

#### `create_file_tool(filename, content="", auto_open=True)`
Create a new file with optional content.

**Parameters:**
- `filename` (str): Name of file with extension (e.g., "app.py", "index.html")
- `content` (str): File content (optional, uses template if empty)
- `auto_open` (bool): Auto-open in VS Code (default: True)

**Returns:**
```json
{
    "success": true,
    "path": "C:\\...\\created_files\\app.py",
    "filename": "app.py",
    "extension": "py",
    "size": 245,
    "message": "File created successfully"
}
```

**Example:**
```python
result = await create_file_tool(
    filename="calculator.py",
    content="def add(a, b):\n    return a + b"
)
```

#### `read_file_tool(file_path)`
Read content from a file.

**Parameters:**
- `file_path` (str): Full path to file

**Returns:**
```json
{
    "success": true,
    "content": "file contents here",
    "size": 1024,
    "lines": 45
}
```

#### `write_file_tool(file_path, content, append=False)`
Write content to a file.

**Parameters:**
- `file_path` (str): Full path to file
- `content` (str): Content to write
- `append` (bool): Append if True, overwrite if False

**Returns:**
```json
{
    "success": true,
    "path": "path/to/file.py",
    "size": 512,
    "message": "Content written to file"
}
```

#### `list_files_tool()`
List all created files.

**Returns:**
```json
{
    "success": true,
    "count": 5,
    "files": [
        {
            "name": "app.py",
            "path": "C:\\...\\created_files\\app.py",
            "size": 245,
            "created": "2024-12-02T10:30:00"
        }
    ]
}
```

#### `delete_file_tool(filename)`
Delete a created file.

**Parameters:**
- `filename` (str): Name of file to delete

**Returns:**
```json
{
    "success": true,
    "message": "File deleted: app.py"
}
```

### Screen Vision Tools

#### `take_screenshot_tool(save=True)`
Capture current screen.

**Parameters:**
- `save` (bool): Save to file or return data

**Returns:**
```json
{
    "success": true,
    "path": "C:\\...\\screenshots\\screen_20241202_103000.png",
    "timestamp": "20241202_103000",
    "width": 1920,
    "height": 1080
}
```

#### `extract_screen_text_tool()`
Extract all text from screen using OCR.

**Returns:**
```json
{
    "success": true,
    "text": "All extracted text from screen",
    "confidence": 87.5,
    "length": 1024
}
```

#### `analyze_screen_tool()`
Comprehensive screen analysis.

**Returns:**
```json
{
    "success": true,
    "text": "Extracted text",
    "colors": [
        {"rgb": [255, 0, 0], "hex": "#FF0000"}
    ],
    "ui_elements": [
        {"x": 100, "y": 200, "width": 50, "height": 30}
    ],
    "screen_info": {
        "resolution": {"width": 1920, "height": 1080},
        "brightness": 128,
        "average_color": {"r": 128, "g": 128, "b": 128}
    },
    "timestamp": "2024-12-02T10:30:00"
}
```

#### `search_screen_text_tool(search_text)`
Search for text on screen.

**Parameters:**
- `search_text` (str): Text to search for

**Returns:**
```json
{
    "success": true,
    "found": true,
    "occurrences": 3,
    "search_text": "example"
}
```

### Code Generator Tools

#### `generate_code_tool(language, code_type, name, description="", parameters="")`
Generate intelligent code.

**Parameters:**
- `language` (str): python, javascript, html, react, sql, java, cpp
- `code_type` (str): function, class, form, component, table, api, etc
- `name` (str): Name of code entity
- `description` (str): What it does
- `parameters` (str): Function parameters (Python)

**Returns:**
```json
{
    "success": true,
    "language": "python",
    "code_type": "function",
    "name": "calculate_average",
    "code": "def calculate_average(numbers):\n    ...",
    "length": 256,
    "timestamp": "2024-12-02T10:30:00"
}
```

**Examples:**

```python
# Generate Python function
result = await generate_code_tool(
    language='python',
    code_type='function',
    name='sum_numbers',
    description='Sum all numbers in a list'
)

# Generate HTML form
result = await generate_code_tool(
    language='html',
    code_type='form',
    name='Login',
    description='User login form'
)

# Generate React component
result = await generate_code_tool(
    language='react',
    code_type='component',
    name='Dashboard',
    description='Main dashboard component'
)

# Generate JavaScript API
result = await generate_code_tool(
    language='javascript',
    code_type='api',
    name='UserAPI',
    description='API for user operations'
)

# Generate SQL table
result = await generate_code_tool(
    language='sql',
    code_type='table',
    name='users',
    description='Users table'
)
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here

# Google API
GOOGLE_API_KEY=your_google_api_key

# OpenAI API (if using OpenAI instead of Google)
OPENAI_API_KEY=your_openai_key

# Optional
DEBUG=False
LOG_LEVEL=INFO
```

### Custom Prompts
Edit `Jarvis_prompts.py` to customize:
- AI personality
- Response tone
- Special behaviors
- Command triggers
- Memory injection

---

## ❓ Troubleshooting

### Issue: "Tesseract not found"
**Solution:**
1. Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Add path to Python (if needed):
```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "LiveKit connection failed"
**Solution:**
1. Check LIVEKIT_URL in .env
2. Verify API credentials
3. Check internet connection
4. Ensure server is running

### Issue: "Microphone not detected"
**Solution:**
1. Check Windows Sound settings
2. Test microphone independently
3. Check browser permissions
4. Restart audio service

### Issue: "File creation fails"
**Solution:**
1. Check file permissions
2. Verify path is writable
3. Ensure filename is valid
4. Check disk space

---

## 📝 License

This project is designed and created by **Rudra sir**.

---

## 🙏 Credits

Built with:
- **LiveKit** - Real-time AI framework
- **Google Cloud** - LLM and STT/TTS
- **Tesseract OCR** - Text extraction
- **OpenCV** - Computer vision
- **PyAutoGUI** - Desktop automation

---

## 📞 Support

For issues or feature requests:
1. Check the troubleshooting section
2. Review module documentation
3. Check console logs for errors
4. Contact development team

---

## 🎉 Enjoy!

You now have the most advanced personal AI assistant. Happy coding and exploring! 🚀

For more information, visit each module's docstring and inline documentation.

**Created: December 2024**  
**Version: 3.0 ULTRA**  
**Status: Production Ready** ✅
