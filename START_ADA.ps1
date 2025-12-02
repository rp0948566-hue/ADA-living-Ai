# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ADA AI SYSTEM - QUICK START LAUNCHER (PowerShell)             ║
# ║                          v3.0 ULTRA                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  🤖 ADA AI SYSTEM - LAUNCHER                             ║" -ForegroundColor Cyan
Write-Host "║                      Version 3.0 ULTRA                                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Set location to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    
    try {
        python -m venv .venv
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

try {
    & ".venv\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$pipList = pip list 2>$null
if ($pipList -notmatch "livekit-agents") {
    Write-Host ""
    Write-Host "⚠️  Installing dependencies..." -ForegroundColor Yellow
    Write-Host "This may take 5-15 minutes on first run..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        pip install -r requirements.txt
        Write-Host "✓ Dependencies installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

# Check for Tesseract
Write-Host ""
Write-Host "Checking Tesseract OCR..." -ForegroundColor Yellow

try {
    $tesseractCheck = tesseract --version 2>$null
    Write-Host "✓ Tesseract OCR found" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "⚠️  Tesseract OCR not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Tesseract is required for screen vision features." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install from:" -ForegroundColor Yellow
    Write-Host "https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
}

# Check for .env file
Write-Host ""
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You need to create a .env file with API keys." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Create .env with:" -ForegroundColor Cyan
    Write-Host "  LIVEKIT_URL=your_url" -ForegroundColor Cyan
    Write-Host "  LIVEKIT_API_KEY=your_key" -ForegroundColor Cyan
    Write-Host "  GOOGLE_API_KEY=your_key" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue"
}

# Display startup info
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                      ✓ SETUP COMPLETE                                    ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Starting ADA AI System..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  • Speak clearly and naturally" -ForegroundColor Gray
Write-Host "  • Wait for response before speaking" -ForegroundColor Gray
Write-Host "  • Commands work in English and Hindi" -ForegroundColor Gray
Write-Host "  • Check console for feedback" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the system" -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Start the system
try {
    python agent.py
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host ""
    Write-Host "❌ Failed to start ADA AI System" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    $exitCode = 1
}

# Handle exit
Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✓ ADA AI System stopped successfully" -ForegroundColor Green
} else {
    Write-Host "❌ ADA AI System encountered an error (Exit Code: $exitCode)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check .env file configuration" -ForegroundColor Gray
    Write-Host "  2. Verify internet connection" -ForegroundColor Gray
    Write-Host "  3. Check API credentials" -ForegroundColor Gray
    Write-Host "  4. Review error messages above" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host | Out-Null
