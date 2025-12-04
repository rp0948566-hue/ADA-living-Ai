"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    INSTALLATION & USAGE CHECKLIST                           ║
║                         ADA AI System v3.0                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Follow this checklist to get ADA AI running on your system.

════════════════════════════════════════════════════════════════════════════════

PHASE 1: PREPARATION
═══════════════════════════════════════════════════════════════════════════════

☐ Check Python Installation
  ├─ Open PowerShell/CMD
  ├─ Run: python --version
  ├─ Should show: Python 3.8 or higher
  └─ If not found: Download from python.org

☐ Check Project Location
  ├─ Navigate to: C:\Users\HP\Desktop\ADA-ai
  ├─ Verify folders exist
  └─ Verify agent.py exists

════════════════════════════════════════════════════════════════════════════════

PHASE 2: PYTHON ENVIRONMENT SETUP
═══════════════════════════════════════════════════════════════════════════════

☐ Create Virtual Environment
  ├─ Open PowerShell as Administrator
  ├─ Navigate to project folder
  ├─ Run: python -m venv .venv
  ├─ Wait for completion (2-5 minutes)
  └─ Verify .venv folder created

☐ Activate Virtual Environment
  ├─ Run: & .venv\\Scripts\\Activate.ps1
  ├─ You should see (.venv) in prompt
  └─ Verify you're in virtual environment

☐ Upgrade pip/setuptools
  ├─ Run: python -m pip install --upgrade pip setuptools wheel
  ├─ This ensures latest package management
  └─ Wait for completion

════════════════════════════════════════════════════════════════════════════════

PHASE 3: INSTALL DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════════

☐ Install from requirements.txt
  ├─ Run: pip install -r requirements.txt
  ├─ This will install 20+ packages
  ├─ Takes 5-15 minutes (depends on internet)
  └─ Wait for "Successfully installed" message

☐ Handle Installation Issues
  ├─ If any package fails:
  ├─ Try: pip install package_name --no-cache-dir
  ├─ Or update setuptools: pip install --upgrade setuptools
  └─ Then retry: pip install -r requirements.txt

☐ Verify Installation
  ├─ Run: pip list
  ├─ Look for these key packages:
  │  ├─ livekit-agents
  │  ├─ livekit-plugins-google
  │  ├─ opencv-python
  │  ├─ pytesseract
  │  ├─ pyautogui
  │  └─ pynput
  └─ All should be listed

════════════════════════════════════════════════════════════════════════════════

PHASE 4: INSTALL EXTERNAL DEPENDENCIES
═══════════════════════════════════════════════════════════════════════════════

☐ Install Tesseract OCR (REQUIRED for screen vision)
  
  ✓ Windows Installation:
    1. Download from: 
       https://github.com/UB-Mannheim/tesseract/wiki
    2. Download: tesseract-ocr-w64-setup-v5.x.exe
    3. Run installer
    4. Choose: Install for all users
    5. Accept default path: C:\Program Files\Tesseract-OCR
    6. Click "Full Installation"
    7. Finish installation
    8. Restart computer (recommended)

  ✓ Verify Installation:
    ├─ Open PowerShell
    ├─ Run: tesseract --version
    ├─ Should show version number
    └─ If error, add path to pytesseract in code

☐ (Optional) Visual C++ Build Tools
  ├─ Some packages need compilation
  ├─ Download: Visual C++ Build Tools
  ├─ Install "Desktop development with C++"
  └─ Restart after installation

════════════════════════════════════════════════════════════════════════════════

PHASE 5: CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

☐ Create .env File
  ├─ In project root directory
  ├─ Create new file: .env
  ├─ Add following content:
  │
  │ LIVEKIT_URL=your_livekit_url
  │ LIVEKIT_API_KEY=your_api_key
  │ LIVEKIT_API_SECRET=your_api_secret
  │ GOOGLE_API_KEY=your_google_api_key
  │ OPENAI_API_KEY=your_openai_key
  │
  └─ Save file

☐ Get API Keys (if needed)
  ├─ Google Cloud:
  │  ├─ Visit: console.cloud.google.com
  │  ├─ Create project
  │  ├─ Enable Speech-to-Text API
  │  ├─ Enable Text-to-Speech API
  │  └─ Create API key
  │
  ├─ OpenAI (optional):
  │  ├─ Visit: openai.com
  │  ├─ Create account
  │  ├─ Get API key
  │  └─ Add to .env
  │
  └─ LiveKit (if using cloud):
     ├─ Visit: livekit.io
     ├─ Create account
     ├─ Get credentials
     └─ Add to .env

☐ Verify .env File
  ├─ Check file location (project root)
  ├─ Verify no .txt extension
  ├─ Check all required keys present
  └─ Verify no extra spaces

════════════════════════════════════════════════════════════════════════════════

PHASE 6: DIRECTORIES & PERMISSIONS
═══════════════════════════════════════════════════════════════════════════════

☐ Create Required Directories
  ├─ created_files/ (auto-created)
  ├─ screenshots/ (auto-created)
  ├─ memory/ (should exist)
  └─ Run SETUP_ADVANCED_AI.py to auto-create

☐ Check File Permissions
  ├─ Right-click ADA-ai folder
  ├─ Properties → Security
  ├─ Verify you have Write permission
  ├─ If not, add your user account
  └─ Apply and OK

☐ Check Microphone Permissions
  ├─ Windows Settings → Privacy → Microphone
  ├─ Ensure microphone is enabled
  ├─ Allow apps to access microphone
  ├─ Test microphone in Sound Settings
  └─ Adjust microphone level if needed

════════════════════════════════════════════════════════════════════════════════

PHASE 7: PRE-LAUNCH CHECKS
═══════════════════════════════════════════════════════════════════════════════

☐ Final Verification Checklist
  ├─ (.venv) shown in PowerShell prompt? ✓
  ├─ All packages installed? ✓ (pip list)
  ├─ Tesseract installed? ✓ (tesseract --version)
  ├─ .env file created and filled? ✓
  ├─ API keys valid and present? ✓
  ├─ Directories created? ✓ (created_files/, screenshots/)
  ├─ Microphone working? ✓ (test in Sound Settings)
  ├─ Python version correct? ✓ (python --version)
  └─ Internet connection active? ✓

☐ Run Setup Wizard
  ├─ Run: python SETUP_ADVANCED_AI.py
  ├─ Review all checks
  ├─ Fix any warnings
  └─ Note recommendations

════════════════════════════════════════════════════════════════════════════════

PHASE 8: LAUNCH ADA
═══════════════════════════════════════════════════════════════════════════════

☐ Start the System
  ├─ Open PowerShell
  ├─ Navigate to project folder
  ├─ Ensure (.venv) is active
  ├─ Run: python agent.py
  ├─ Wait for "Ready for input" message
  └─ System is now running!

☐ First Run Status
  ├─ ✓ Shows: "Starting agent session"
  ├─ ✓ Shows: "Connected to room"
  ├─ ✓ Shows: "Waiting for audio input"
  ├─ ✓ You should see console messages
  └─ If errors, check troubleshooting section

════════════════════════════════════════════════════════════════════════════════

PHASE 9: INITIAL TESTING
═══════════════════════════════════════════════════════════════════════════════

☐ Test Basic Features
  
  1. Test Voice Recognition:
     ├─ Speak: "Hello ADA"
     ├─ Listen for response
     └─ Should respond with greeting
  
  2. Test File Creation:
     ├─ Say: "Create a Python file called test.py"
     ├─ Check: created_files/ folder
     ├─ Verify: test.py exists
     └─ Should auto-open in VS Code
  
  3. Test Screenshot:
     ├─ Say: "Take a screenshot"
     ├─ Check: screenshots/ folder
     ├─ Verify: new screenshot.png exists
     └─ File should be timestamped
  
  4. Test Memory:
     ├─ Say: "Remember my name is [Your Name]"
     ├─ Wait for confirmation
     ├─ Ask: "What's my name?"
     └─ Should recall your name
  
  5. Test Computer Control:
     ├─ Say: "Open VS Code"
     ├─ VS Code should launch
     ├─ Say: "Click at 100, 100"
     └─ Mouse should move to that position

☐ Check Console Output
  ├─ Look for: "✅ Connected to room"
  ├─ Look for: Tool execution logs
  ├─ Look for: No errors or exceptions
  ├─ Look for: Response confirmations
  └─ All should indicate success

════════════════════════════════════════════════════════════════════════════════

PHASE 10: ADVANCED TESTING
═══════════════════════════════════════════════════════════════════════════════

☐ Test Code Generation
  └─ Say: "Generate a Python function to add two numbers"
     ├─ Should create file
     ├─ Should contain function code
     ├─ Should have docstrings
     └─ Should be properly formatted

☐ Test Screen Vision
  └─ Say: "What text is on my screen?"
     ├─ Should capture screenshot
     ├─ Should extract text
     ├─ Should show results
     └─ Should have confidence score

☐ Test Advanced Features
  └─ Try combinations:
     ├─ "Create file then open it"
     ├─ "Take screenshot and extract text"
     ├─ "Generate code and save to file"
     ├─ "Read file and show me content"
     └─ All should work seamlessly

════════════════════════════════════════════════════════════════════════════════

PHASE 11: TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

If you encounter issues:

☐ Virtual Environment Problems
  ├─ Error: "No module named 'venv'"
  ├─ Solution: python -m pip install virtualenv
  ├─ Then: python -m virtualenv .venv
  └─ Reactivate

☐ Package Installation Fails
  ├─ Error: "ModuleNotFoundError"
  ├─ Solution: pip install -r requirements.txt --upgrade
  ├─ Try: pip install package --no-cache-dir
  └─ Or reinstall entire venv

☐ Tesseract Not Found
  ├─ Error: "tesseract is not installed"
  ├─ Check: Is Tesseract installed?
  ├─ Run: tesseract --version
  ├─ If not found: Reinstall from GitHub
  └─ Restart Python after installation

☐ Microphone Not Detected
  ├─ Check: Windows Sound Settings
  ├─ Check: App has microphone permission
  ├─ Test: Record audio in Sound Recorder
  ├─ Try: Restart audio service
  └─ Last: Restart computer

☐ API Connection Failed
  ├─ Check: .env file has correct keys
  ├─ Check: Internet connection active
  ├─ Check: API keys are valid
  ├─ Try: Restart the script
  └─ Debug: Check console for error messages

☐ File Creation Failed
  ├─ Check: Directory permissions
  ├─ Check: Disk space available
  ├─ Check: Filename is valid
  ├─ Try: Create file manually first
  └─ Check: created_files/ folder writable

☐ Screen Vision Not Working
  ├─ Check: Tesseract installed
  ├─ Check: System has OpenCV (cv2)
  ├─ Try: python -c "import cv2; print(cv2.__version__)"
  ├─ Reinstall: pip install opencv-python
  └─ Restart script

════════════════════════════════════════════════════════════════════════════════

PHASE 12: OPTIMIZATION
═══════════════════════════════════════════════════════════════════════════════

☐ System Performance
  ├─ Close unnecessary programs
  ├─ Disable browser extensions
  ├─ Close background apps
  ├─ Check: 4GB+ RAM available
  └─ Monitor: Task Manager while running

☐ Audio Quality
  ├─ Test microphone volume
  ├─ Reduce background noise
  ├─ Use headphones with microphone
  ├─ Position microphone 6-12 inches away
  └─ Test: Record yourself first

☐ Network Speed
  ├─ Check: Internet speed (speedtest.net)
  ├─ Requires: 5+ Mbps for good performance
  ├─ Use: Wired connection if possible
  ├─ Test: Move closer to router
  └─ Check: No other large downloads

════════════════════════════════════════════════════════════════════════════════

PHASE 13: DAILY USAGE
═══════════════════════════════════════════════════════════════════════════════

☐ Daily Startup Procedure
  1. Open PowerShell
  2. Navigate to project: cd C:\Users\HP\Desktop\ADA-ai
  3. Activate: & .venv\\Scripts\\Activate.ps1
  4. Start: python agent.py
  5. Wait for "Ready for input" message
  6. Start speaking commands

☐ Best Practices
  ├─ Speak clearly and naturally
  ├─ Give complete commands
  ├─ Wait for response before speaking
  ├─ Use proper file extensions
  ├─ Check file was created before closing
  ├─ Save important files to backup
  └─ Review generated code before using

☐ Shutdown Procedure
  ├─ Close all open files in VS Code
  ├─ Stop the script: Ctrl+C
  ├─ Wait for cleanup
  ├─ Deactivate venv: deactivate
  ├─ Close PowerShell
  └─ Done!

════════════════════════════════════════════════════════════════════════════════

PHASE 14: ADVANCED CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

☐ Customize Prompts
  ├─ Edit: Jarvis_prompts.py
  ├─ Modify: behavior_prompts variable
  ├─ Change: AI personality
  ├─ Add: Custom commands
  └─ Save and restart

☐ Configure File Templates
  ├─ Edit: advanced_file_creator.py
  ├─ Modify: FILE_TEMPLATES dictionary
  ├─ Add: New file types
  ├─ Change: Default content
  └─ Save and restart

☐ Adjust Screen Vision
  ├─ Edit: advanced_screen_vision.py
  ├─ Modify: OCR parameters
  ├─ Change: Detection sensitivity
  ├─ Add: New analysis types
  └─ Save and restart

════════════════════════════════════════════════════════════════════════════════

PHASE 15: SUCCESS CONFIRMATION
═══════════════════════════════════════════════════════════════════════════════

✅ Installation Complete When:

☐ Virtual environment activated
☐ All packages installed
☐ Tesseract OCR installed
☐ .env file configured
☐ Directories created
☐ Microphone working
☐ Script starts without errors
☐ Can take screenshots
☐ Can create files
☐ Can generate code
☐ Memory system working
☐ Voice recognition active
☐ All tests passing

🎉 CONGRATULATIONS! 🎉

You now have a fully functional ADA AI System!

════════════════════════════════════════════════════════════════════════════════

📞 SUPPORT & HELP

If you encounter issues:
1. Check TROUBLESHOOTING.md
2. Review console error messages
3. Run setup wizard again
4. Check API credentials
5. Verify all dependencies installed

════════════════════════════════════════════════════════════════════════════════

📚 NEXT STEPS

1. Explore all features
2. Create sample files
3. Test all commands
4. Customize prompts
5. Build your workflow
6. Enjoy your AI assistant!

════════════════════════════════════════════════════════════════════════════════

Happy Computing! 🚀

Version: 3.0 ULTRA
Created: December 2024
Status: Production Ready ✅

════════════════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
