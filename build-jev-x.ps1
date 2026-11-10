# Builds a standalone jev_x binary (dist\jev-x.exe) - no system Python needed to run it.
# Run on Windows (PyInstaller does not cross-compile); build-jev-x.sh does the Linux build.
$ErrorActionPreference = 'Stop'; Set-Location $PSScriptRoot
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { winget install -e --id Python.Python.3.12; Write-Host 'Reopen PowerShell, then run this again.'; exit 1 }
python -m pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) { python -m pip install --quiet pyinstaller pillow }
python -m PyInstaller --onefile --name jev-x --noconfirm `
  --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageGrab `
  jev_x/__main__.py
Write-Host 'Built: dist\jev-x.exe'
