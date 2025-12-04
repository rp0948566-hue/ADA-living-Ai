@echo off
REM ==============================================================================
REM  ADA AI - Random Topic Memory System Launcher
REM  Run this batch file to start the complete system
REM ==============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════╗
echo ║                     🧠 ADA AI - TOPIC MEMORY SYSTEM                      ║
echo ║                          Launcher Script v1.0                            ║
echo ╚══════════════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Display menu
echo Select what to run:
echo.
echo   1) Run Agent with Topic Memory (MAIN)
echo   2) Run Backend Service (BACKGROUND)
echo   3) Run Quick Demo
echo   4) View Topic Memory Statistics
echo   5) Open Documentation
echo   6) Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting Agent with Topic Memory System...
    echo.
    python agent.py console
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🚀 Starting Backend Topic Service (Runs Continuously)...
    echo.
    echo Press Ctrl+C to stop the service
    echo.
    python backend_topic_service.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🚀 Running Quick Demo...
    echo.
    python quickstart_topic_memory.py
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 📊 Topic Memory Statistics
    echo ────────────────────────────────────────────────────────────────
    echo.
    python -c "from random_topic_memory import get_memory_stats; import json; stats = get_memory_stats(); print(json.dumps(stats, indent=2))"
    echo.
    echo ────────────────────────────────────────────────────────────────
    echo.
    pause
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 📖 Opening Documentation...
    echo.
    if exist RANDOM_TOPIC_MEMORY_GUIDE.md (
        start RANDOM_TOPIC_MEMORY_GUIDE.md
    ) else (
        echo ❌ Documentation file not found
    )
    echo.
    pause
    goto end
)

if "%choice%"=="6" (
    echo.
    echo 👋 Goodbye!
    echo.
    exit /b 0
)

echo.
echo ❌ Invalid choice. Please try again.
echo.
pause
goto :eof

:end
echo.
pause
