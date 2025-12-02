# ═════════════════════════════════════════════════════════════════════════════
# 🔍 SELF-UPDATE MEMORY ENGINE LAUNCHER
# ═════════════════════════════════════════════════════════════════════════════
# Purpose: Launch the self-update memory engine for endless Google search learning
# The engine:
# - Generates random learning topics (30 different categories)
# - Searches Google every 60 seconds for new knowledge
# - Stores all learned knowledge in memory/evolution_log.json
# - Syncs to agent memory every 5 cycles
# - Runs endlessly in background
# ═════════════════════════════════════════════════════════════════════════════

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Display banner
Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                   ║" -ForegroundColor Cyan
Write-Host "║  🔍  SELF-UPDATE MEMORY ENGINE LAUNCHER (Google Search)          ║" -ForegroundColor Cyan
Write-Host "║                                                                   ║" -ForegroundColor Cyan
Write-Host "║  Endless Learning System - AI Evolution Mode                     ║" -ForegroundColor Cyan
Write-Host "║                                                                   ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonExists = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
if (-not $pythonExists) {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and ensure it's added to your system PATH" -ForegroundColor Red
    Write-Host ""
    Pause
    exit 1
}

Write-Host "✅ Python found: $(python --version)" -ForegroundColor Green
Write-Host ""

# Check if self_update_memory_ADA.py exists
if (-not (Test-Path "self_update_memory_ADA.py")) {
    Write-Host "❌ ERROR: self_update_memory_ADA.py not found in current directory" -ForegroundColor Red
    Write-Host "Location: $scriptPath" -ForegroundColor Red
    Write-Host ""
    Pause
    exit 1
}

Write-Host "✅ self_update_memory_ADA.py found" -ForegroundColor Green
Write-Host ""

# Check if memory folder exists, create if not
if (-not (Test-Path "memory")) {
    Write-Host "📁 Creating memory folder..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "memory" | Out-Null
    Write-Host "✅ Memory folder created" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 LAUNCHING SELF-UPDATE MEMORY ENGINE                          ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 Engine Configuration:" -ForegroundColor Yellow
Write-Host "   🎯 Search Interval: 60 seconds" -ForegroundColor Cyan
Write-Host "   🔍 Search Topics: 30 random categories" -ForegroundColor Cyan
Write-Host "   💾 Storage: memory/evolution_log.json" -ForegroundColor Cyan
Write-Host "   🔄 Sync Interval: Every 5 cycles (5 minutes)" -ForegroundColor Cyan
Write-Host "   🌐 Search Engine: Google (via DuckDuckGo API)" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Topics Covered:" -ForegroundColor Yellow
Write-Host "   • Python Programming, Machine Learning, AI" -ForegroundColor Cyan
Write-Host "   • Windows System, Security, Performance" -ForegroundColor Cyan
Write-Host "   • Software Development, Testing, Debugging" -ForegroundColor Cyan
Write-Host "   • Cloud Computing, DevOps, Databases" -ForegroundColor Cyan
Write-Host "   • Networking, Cybersecurity, and more..." -ForegroundColor Cyan
Write-Host ""

Write-Host "⏱️  Starting Self-Update Memory Engine..." -ForegroundColor Yellow
Write-Host "   (Press Ctrl+C to stop)" -ForegroundColor Yellow
Write-Host ""

# Run the self-update memory engine
try {
    python self_update_memory_ADA.py
}
catch {
    Write-Host "❌ ERROR: Failed to launch self-update memory engine" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
    Write-Host ""
    Pause
    exit 1
}
