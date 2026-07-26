# IRIS - Local AI Mode terminal
# Hosts the Hermes gateway (the "brain") running on a local Ollama model.
# Auto-detects whether Ollama is already serving; starts it if not, then
# starts (or restarts) the Hermes gateway pinned to the given local model.

param(
    [string]$ModelName = "",
    [string]$HermesExe = "",
    [string]$HermesDir = ""
)

$host.UI.RawUI.WindowTitle = "IRIS - Local AI Mode ($ModelName)"
Clear-Host
Write-Host ""
Write-Host "     #####################################" -ForegroundColor Magenta
Write-Host "     ###                                 ###" -ForegroundColor Magenta
Write-Host "     ###          I   R   I   S             ###" -ForegroundColor Magenta
Write-Host "     ###                                 ###" -ForegroundColor Magenta
Write-Host "     #####################################" -ForegroundColor Magenta
Write-Host ""
Write-Host "              LOCAL AI MODE - $ModelName" -ForegroundColor DarkMagenta
Write-Host "        running fully offline via Ollama - no cloud, no API cost" -ForegroundColor DarkGray
Write-Host ""

function Test-Ollama {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3
        return $r.StatusCode -eq 200
    } catch { return $false }
}

if (-not (Test-Ollama)) {
    Write-Host "Ollama not reachable - starting 'ollama serve'..." -ForegroundColor Yellow
    Start-Process -WindowStyle Hidden -FilePath "ollama" -ArgumentList "serve"
    $tries = 0
    while (-not (Test-Ollama) -and $tries -lt 20) {
        Start-Sleep -Milliseconds 500
        $tries++
    }
}
if (Test-Ollama) {
    Write-Host "Ollama is up." -ForegroundColor Green
} else {
    Write-Host "WARNING: Ollama still not reachable after waiting - Hermes may fail to connect." -ForegroundColor Red
}

Write-Host ""
Write-Host "Starting Hermes gateway on '$ModelName'..." -ForegroundColor Cyan
Set-Location -Path $HermesDir
& $HermesExe gateway run
