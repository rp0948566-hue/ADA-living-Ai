# Jev-X for Windows. Run in PowerShell: .\install-windows.ps1
# Needs no Python on this machine: uses the prebuilt dist\jev-x.exe binary if present,
# otherwise falls back to `python -m jev_x` for a dev checkout that has Python.
$ErrorActionPreference = 'Stop'; Set-Location $PSScriptRoot
$c = Join-Path $env:USERPROFILE '.config\jev-x'; New-Item -ItemType Directory -Force $c | Out-Null
$f = Join-Path $c 'config.json'
if (-not (Test-Path $f)) { '{"base_url": "http://127.0.0.1:8089/v1", "model": "local"}' | Set-Content $f }
if (Test-Path .\dist\jev-x.exe) { $run = '.\dist\jev-x.exe' }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $run = 'python -m jev_x' }
else { winget install -e --id Python.Python.3.12; Write-Host 'No dist\jev-x.exe and no python found. Reopen PowerShell and run this again, or run .\build-jev-x.ps1 first.'; exit 1 }
Invoke-Expression "$run --doctor"
Write-Host "Run: $run   |   $run --serve"
