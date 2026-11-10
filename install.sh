#!/bin/bash
# Jev installer. Paste in Terminal:
#   curl -fsSL https://raw.githubusercontent.com/SaarthurR/atticus-mac/main/install.sh | bash
# Downloads the source to ~/.jev (Jev updates itself from there), builds the app, opens it.
set -e
DIR="${JEV_DIR:-$HOME/.jev}"
echo "Installing Jev…"
[ "$(sw_vers -productVersion | cut -d. -f1)" -ge 26 ] || { echo "Jev needs macOS 26 or later."; exit 1; }
if ! xcode-select -p >/dev/null 2>&1; then
  echo "First, Apple's command line tools. A macOS window will open: click Install."
  echo "When it finishes, paste the install line again."
  xcode-select --install 2>/dev/null || true
  exit 1
fi
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull -q --ff-only || { echo "Could not update $DIR. Delete that folder, then paste the install line again."; exit 1; }
else
  git clone -q --depth 1 https://github.com/SaarthurR/atticus-mac.git "$DIR"
fi
"$DIR/build.sh"
open "$HOME/Applications/Jev.app"
echo "Done. The Jev setup window walks you through the rest."
