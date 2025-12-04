# ═════════════════════════════════════════════════════════════════════════════
# 🧠 BACKEND LEARNING ENGINE - INDEPENDENT TERMINAL
# ═════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧠 BACKEND LEARNING ENGINE - TERMINAL 1             ║" -ForegroundColor Cyan
Write_Host "║                                                        ║" -ForegroundColor Cyan
Write-Host "║  • Runs independently in background                   ║" -ForegroundColor Cyan
Write-Host "║  • Scans random files and learns automatically        ║" -ForegroundColor Cyan
Write-Host "║  • Selects topics with AI brain                       ║" -ForegroundColor Cyan
Write-Host "║  • Saves improvements to permanent memory             ║" -ForegroundColor Cyan
Write-Host "║  • Runs endlessly until terminated                    ║" -ForegroundColor Cyan
Write-Host "║                                                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Activate virtual environment if not already active
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Please run START_SYSTEM.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if ($env:VIRTUAL_ENV -eq "") {
    Write-Host "🔗 Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "🚀 Starting Backend Learning Engine..." -ForegroundColor Green
Write-Host "   Endpoint: backend_learning_engine.py" -ForegroundColor Gray
Write-Host "   Interval: 30 seconds per learning cycle" -ForegroundColor Gray
Write-Host "   Max files: 10 files per scan" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the backend learning engine" -ForegroundColor Yellow
Write-Host ""

python backend_learning_engine.py

Write-Host ""
Write-Host "🛑 Backend Learning Engine terminated." -ForegroundColor Red
Read-Host "Press Enter to close this window"
