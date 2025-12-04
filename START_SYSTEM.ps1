# ═════════════════════════════════════════════════════════════════════════════
# 🚀 AUTONOMOUS ADA - COMPLETE STARTUP SCRIPT
# ═════════════════════════════════════════════════════════════════════════════
# This script launches the complete system with:
# 1. Backend Learning Engine (Terminal 1) - Independent intelligence
# 2. Memory Sync Bridge (Terminal 2) - Knowledge synchronization
# 3. Self-Update Memory Engine (Terminal 3) - Google search learning
# 4. Main Agent (Terminal 4) - User interaction
# ═════════════════════════════════════════════════════════════════════════════

param(
    [switch]$SkipBackend = $false,
    [switch]$SkipSync = $false,
    [switch]$SkipSelfUpdate = $false,
    [switch]$SkipAgent = $false
)

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                    ║" -ForegroundColor Cyan
Write-Host "║          🤖 AUTONOMOUS ADA AI - SYSTEM INITIALIZATION              ║" -ForegroundColor Cyan
Write-Host "║                                                                    ║" -ForegroundColor Cyan
Write-Host "║  • Backend Learning Engine (Terminal 1)                           ║" -ForegroundColor Cyan
Write-Host "║  • Memory Sync Bridge (Terminal 2)                                ║" -ForegroundColor Cyan
Write-Host "║  • Self-Update Memory (Terminal 3) - Google Search                ║" -ForegroundColor Cyan
Write-Host "║  • Main Agent (Terminal 4)                                        ║" -ForegroundColor Cyan
Write-Host "║                                                                    ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔗 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install requirements
Write-Host "📦 Installing/Verifying dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt 2>$null

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""

# Start Backend Learning Engine
if (-not $SkipBackend) {
    Write-Host "🧠 Starting Backend Learning Engine..." -ForegroundColor Green
    Write-Host "   (This will run independently and continuously learn)" -ForegroundColor Gray
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "
        Set-Location '$scriptDir'
        & '.\START_BACKEND.ps1'
    " -WindowStyle Normal
    
    Start-Sleep -Seconds 2
}

# Start Memory Sync Bridge
if (-not $SkipSync) {
    Write-Host "🔗 Starting Memory Sync Bridge..." -ForegroundColor Green
    Write-Host "   (Synchronizes backend learning with agent)" -ForegroundColor Gray
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "
        Set-Location '$scriptDir'
        & '.\START_SYNC_BRIDGE.ps1'
    " -WindowStyle Normal
    
    Start-Sleep -Seconds 2
}

# Start Self-Update Memory Engine (NEW)
if (-not $SkipSelfUpdate) {
    Write-Host "🔍 Starting Self-Update Memory Engine..." -ForegroundColor Green
    Write-Host "   (Searches Google endlessly, learns continuously)" -ForegroundColor Gray
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "
        Set-Location '$scriptDir'
        & '.\START_SELF_UPDATE_MEMORY.ps1'
    " -WindowStyle Normal
    
    Start-Sleep -Seconds 2
}

# Start Main Agent
if (-not $SkipAgent) {
    Write-Host "🎯 Starting Main Agent..." -ForegroundColor Magenta
    Write-Host "   (Ready for user interaction)" -ForegroundColor Gray
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "
        Set-Location '$scriptDir'
        & '.\START_AGENT.ps1'
    " -WindowStyle Normal
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ System startup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Status:" -ForegroundColor Cyan
Write-Host "   Backend Learning Engine:  $(if ($SkipBackend) { '❌ Disabled' } else { '✅ Running in Terminal 1' })" -ForegroundColor Gray
Write-Host "   Memory Sync Bridge:        $(if ($SkipSync) { '❌ Disabled' } else { '✅ Running in Terminal 2' })" -ForegroundColor Gray
Write-Host "   Self-Update Memory:        $(if ($SkipSelfUpdate) { '❌ Disabled' } else { '✅ Running in Terminal 3' })" -ForegroundColor Gray
Write-Host "   Main Agent:                $(if ($SkipAgent) { '❌ Disabled' } else { '✅ Running in Terminal 4' })" -ForegroundColor Gray
Write-Host ""
Write-Host "📁 Memory Locations:" -ForegroundColor Cyan
Write-Host "   - Backend Learning:    memory/backend_intelligence.json" -ForegroundColor Gray
Write-Host "   - Evolution Log:       memory/evolution_log.json (Google searches)" -ForegroundColor Gray
Write-Host "   - Search Knowledge:    memory/search_knowledge.json" -ForegroundColor Gray
Write-Host "   - Shared Knowledge:    memory/shared_knowledge.json" -ForegroundColor Gray
Write-Host "   - Agent Memory:        memory/memory.json" -ForegroundColor Gray
Write-Host "   - Power Operations:    memory/power_operations.json" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 Log Files:" -ForegroundColor Cyan
Write-Host "   - Backend:      memory/backend_learning.log" -ForegroundColor Gray
Write-Host "   - Sync:         memory/memory_sync.log" -ForegroundColor Gray
Write-Host "   - Self-Update:  memory/self_update_memory.log" -ForegroundColor Gray
Write-Host "   - Power:        memory/windows_power_ctrl.log" -ForegroundColor Gray
Write-Host "   - Agent:        Agent terminal output" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "   - Each component runs independently in its own terminal" -ForegroundColor Gray
Write-Host "   - Backend continuously scans files and learns automatically" -ForegroundColor Gray
Write-Host "   - Self-Update searches Google every 60 seconds for new knowledge" -ForegroundColor Gray
Write-Host "   - Sync bridge merges knowledge from all sources" -ForegroundColor Gray
Write-Host "   - Agent gets enhanced with learned knowledge automatically" -ForegroundColor Gray
Write-Host "   - All systems run endlessly until manually stopped" -ForegroundColor Gray
Write-Host ""
