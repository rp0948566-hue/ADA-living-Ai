# IRIS - Colibri AI Mode terminal
# Hosts colibri's OpenAI-compatible API + web dashboard (coli web) on one
# port — GLM-5.2 744B MoE running locally, streaming experts from disk.
# `coli web` serves the same API `coli serve` would, plus the live-metrics
# dashboard (hardware panel, expert atlas) at http://localhost:<port>/.

param(
    [string]$PythonExe = "",
    [string]$ColibriDir = "",
    [string]$ModelPath = "",
    [int]$Port = 8765
)

$host.UI.RawUI.WindowTitle = "IRIS - Colibri AI Mode (GLM-5.2)"
Clear-Host
Write-Host ""
Write-Host "     #####################################" -ForegroundColor Yellow
Write-Host "     ###                                 ###" -ForegroundColor Yellow
Write-Host "     ###          I   R   I   S             ###" -ForegroundColor Yellow
Write-Host "     ###                                 ###" -ForegroundColor Yellow
Write-Host "     #####################################" -ForegroundColor Yellow
Write-Host ""
Write-Host "         COLIBRI MODE - GLM-5.2 (744B MoE)" -ForegroundColor DarkYellow
Write-Host "   streaming experts from disk - first replies can be very slow" -ForegroundColor DarkGray
Write-Host ""

Set-Location -Path $ColibriDir
& $PythonExe coli web --no-browser --model $ModelPath --auto-tier --host 127.0.0.1 --port $Port --model-id glm-5.2-colibri
