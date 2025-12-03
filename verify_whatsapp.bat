@echo off
REM WhatsApp Feature Installation Verification Script
REM This script verifies that everything is properly installed

echo.
echo ============================================================
echo  WhatsApp Feature - Installation Verification
echo ============================================================
echo.

setlocal enabledelayedexpansion

REM Track results
set total_checks=0
set passed_checks=0

REM Function to check file existence
:check_file
set /a total_checks+=1
if exist "%~1" (
    echo [PASS] %~2
    set /a passed_checks+=1
) else (
    echo [FAIL] %~2 - File not found: %~1
)
goto :eof

REM Check Python files
echo Checking Python Files:
echo ----------------------
call :check_file "whatsapp_sender.py" "whatsapp_sender.py"
call :check_file "whatsapp_message_generator.py" "whatsapp_message_generator.py"
call :check_file "whatsapp_tools.py" "whatsapp_tools.py"
call :check_file "test_whatsapp_feature.py" "test_whatsapp_feature.py"

REM Check documentation files
echo.
echo Checking Documentation:
echo -----------------------
call :check_file "WHATSAPP_FEATURE_GUIDE.md" "WHATSAPP_FEATURE_GUIDE.md"
call :check_file "WHATSAPP_QUICK_START.txt" "WHATSAPP_QUICK_START.txt"
call :check_file "WHATSAPP_SETUP_GUIDE.txt" "WHATSAPP_SETUP_GUIDE.txt"
call :check_file "WHATSAPP_IMPLEMENTATION_SUMMARY.txt" "WHATSAPP_IMPLEMENTATION_SUMMARY.txt"
call :check_file "README_WHATSAPP.txt" "README_WHATSAPP.txt"

REM Test Python syntax
echo.
echo Checking Python Syntax:
echo -----------------------
set /a total_checks+=1
python -m py_compile whatsapp_sender.py whatsapp_message_generator.py whatsapp_tools.py test_whatsapp_feature.py >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] All Python files have valid syntax
    set /a passed_checks+=1
) else (
    echo [FAIL] Python syntax errors detected
)

REM Check if agent.py was updated
echo.
echo Checking Agent Integration:
echo ---------------------------
set /a total_checks+=1
findstr /M "whatsapp_tools" agent.py >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] agent.py has WhatsApp integration
    set /a passed_checks+=1
) else (
    echo [FAIL] agent.py missing WhatsApp integration
)

REM Check for pyautogui
echo.
echo Checking Python Packages:
echo -------------------------
set /a total_checks+=1
python -c "import pyautogui" >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] pyautogui is installed
    set /a passed_checks+=1
) else (
    echo [FAIL] pyautogui not installed - Run: pip install pyautogui
)

REM Results summary
echo.
echo ============================================================
echo  Results Summary
echo ============================================================
echo.
echo Total Checks: %total_checks%
echo Passed: %passed_checks%
echo Failed: %total_checks%-%passed_checks%
echo.

if %passed_checks% equ %total_checks% (
    echo Status: ✅ ALL CHECKS PASSED - READY TO USE!
    echo.
    echo Next steps:
    echo 1. Make sure WhatsApp Desktop is installed
    echo 2. Start ADA Agent: python agent.py console
    echo 3. Try: "Send a WhatsApp to [name] saying hello"
    echo.
) else (
    echo Status: ⚠️ Some checks failed - See details above
    echo.
    echo Fix the issues and run this script again.
    echo.
)

echo For more help, read:
echo - README_WHATSAPP.txt (Overview)
echo - WHATSAPP_SETUP_GUIDE.txt (Installation)
echo - WHATSAPP_QUICK_START.txt (Usage)
echo.

pause
