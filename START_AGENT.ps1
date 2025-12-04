# ═════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN AGENT - INDEPENDENT TERMINAL
# ═════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  🎯 MAIN AGENT PROCESS - TERMINAL 3                   ║" -ForegroundColor Magenta
Write-Host "║                                                        ║" -ForegroundColor Magenta
Write-Host "║  • User interaction & chat interface                  ║" -ForegroundColor Magenta
Write-Host "║  • Integrated with all linked files                   ║" -ForegroundColor Magenta
Write-Host "║  • Accesses backend learned knowledge                 ║" -ForegroundColor Magenta
Write-Host "║  • Automatic memory injection                         ║" -ForegroundColor Magenta
Write-Host "║  • All tools available                                ║" -ForegroundColor Magenta
Write-Host "║                                                        ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
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
Write-Host "🚀 Starting Main Agent..." -ForegroundColor Green
Write-Host "   Endpoint: agent.py" -ForegroundColor Gray
Write-Host "   Mode: LiveKit Real-time Communication" -ForegroundColor Gray
Write-Host "   Backend: Connected (learning in Terminal 1)" -ForegroundColor Gray
Write-Host "   Sync: Active (Terminal 2)" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the agent" -ForegroundColor Yellow
Write-Host ""

python agent.py

Write-Host ""
Write-Host "🛑 Main Agent terminated." -ForegroundColor Red
Read-Host "Press Enter to close this window"
