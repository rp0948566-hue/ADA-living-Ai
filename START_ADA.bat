@echo off
REM ╔══════════════════════════════════════════════════════════════════════════╗
REM ║              ADA AI SYSTEM - QUICK START LAUNCHER (Windows)              ║
REM ║                          v3.0 ULTRA                                      ║
REM ╚══════════════════════════════════════════════════════════════════════════╝

setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                  🤖 ADA AI SYSTEM - LAUNCHER                             ║
echo ║                      Version 3.0 ULTRA                                   ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo.
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✓ Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment activated

REM Check if requirements are installed
echo.
echo Checking dependencies...
pip list | findstr "livekit-agents" > nul
if errorlevel 1 (
    echo.
    echo ⚠️  Installing dependencies...
    echo This may take 5-15 minutes on first run...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installed
) else (
    echo ✓ Dependencies already installed
)

REM Check for Tesseract
echo.
echo Checking Tesseract OCR...
tesseract --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  Tesseract OCR not found!
    echo.
    echo Tesseract is required for screen vision features.
    echo.
    echo Please install from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo After installation, run this script again.
    echo.
    pause
) else (
    echo ✓ Tesseract OCR found
)

REM Check for .env file
echo.
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo.
    echo You need to create a .env file with API keys.
    echo.
    echo Create .env with:
    echo   LIVEKIT_URL=your_url
    echo   LIVEKIT_API_KEY=your_key
    echo   GOOGLE_API_KEY=your_key
    echo.
    pause
)

REM Display startup info
echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                      ✓ SETUP COMPLETE                                    ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo Starting ADA AI System...
echo.
echo Tips:
echo   • Speak clearly and naturally
echo   • Wait for response before speaking
echo   • Commands work in English and Hindi
echo   • Check console for feedback
echo.
echo Press Ctrl+C to stop the system
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Start the system
python agent.py

REM Handle exit
if errorlevel 1 (
    echo.
    echo ❌ ADA AI System encountered an error
    echo.
    echo Troubleshooting:
    echo   1. Check .env file configuration
    echo   2. Verify internet connection
    echo   3. Check API credentials
    echo   4. Review error messages above
    echo.
) else (
    echo.
    echo ✓ ADA AI System stopped successfully
    echo.
)

echo Press any key to exit...
pause > nul
