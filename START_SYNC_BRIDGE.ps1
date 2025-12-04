# ═════════════════════════════════════════════════════════════════════════════
# 🔗 MEMORY SYNC BRIDGE - INDEPENDENT TERMINAL
# ═════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🔗 MEMORY SYNC BRIDGE - TERMINAL 2                   ║" -ForegroundColor Cyan
Write-Host "║                                                        ║" -ForegroundColor Cyan
Write-Host "║  • Syncs backend learning with agent memory           ║" -ForegroundColor Cyan
Write-Host "║  • Merges knowledge from both sources                 ║" -ForegroundColor Cyan
Write-Host "║  • Thread-safe memory access                          ║" -ForegroundColor Cyan
Write-Host "║  • Auto-applies backend improvements                  ║" -ForegroundColor Cyan
Write-Host "║  • Runs continuously (interval: 15 seconds)           ║" -ForegroundColor Cyan
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
Write-Host "🚀 Starting Memory Sync Bridge..." -ForegroundColor Green
Write-Host "   Endpoint: memory_sync_bridge.py" -ForegroundColor Gray
Write-Host "   Interval: 15 seconds per sync cycle" -ForegroundColor Gray
Write-Host "   Mode: Continuous synchronization" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the memory sync bridge" -ForegroundColor Yellow
Write-Host ""

python memory_sync_bridge.py

Write-Host ""
Write-Host "🛑 Memory Sync Bridge terminated." -ForegroundColor Red
Read-Host "Press Enter to close this window"
