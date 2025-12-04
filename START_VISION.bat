@echo off
REM ═══════════════════════════════════════════════════════════════
REM JARVIS ADVANCED VISION SYSTEM - QUICK LAUNCHER
REM Object Detection + Screen Sharing + Hand Recognition
REM ═══════════════════════════════════════════════════════════════

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🎯 JARVIS ADVANCED VISION SYSTEM LAUNCHER                   ║
echo ║     Choose what to start                                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 1 - Start Advanced Vision GUI only (Camera + Detection)
echo 2 - Start Full AI Agent (with GUI + Voice)
echo 3 - Run Setup (Install packages + verify)
echo 4 - View Detection Data
echo 5 - Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🖥️  Starting Advanced Vision GUI...
    python jarvis_advanced_vision.py
    goto end
)

if "%choice%"=="2" (
    echo.
    echo 🚀 Starting Full JARVIS AI Agent...
    python agent.py
    goto end
)

if "%choice%"=="3" (
    echo.
    echo 🔧 Running Setup...
    python setup_object_detection.py
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo 📊 Detection Data Files:
    echo.
    if exist detection_data (
        dir detection_data /B
    ) else (
        echo No detection_data folder yet.
    )
    pause
    goto end
)

if "%choice%"=="5" (
    echo.
    echo 👋 Exiting...
    goto end
)

echo.
echo ❌ Invalid choice
pause

:end
echo.
