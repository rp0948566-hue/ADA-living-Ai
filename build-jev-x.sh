#!/bin/bash
# Builds a standalone jev_x binary (dist/jev-x) — no system Python needed to run it.
# Run on each target OS (PyInstaller does not cross-compile): Linux here, build-jev-x.ps1 on Windows.
set -e; cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "Need python3 to BUILD (not to run the result). Install it, then retry."; exit 1; }
python3 -m pip show pyinstaller >/dev/null 2>&1 || python3 -m pip install --quiet pyinstaller pillow
python3 -m PyInstaller --onefile --name jev-x --noconfirm \
  --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageGrab \
  jev_x/__main__.py
echo "Built: dist/jev-x"
