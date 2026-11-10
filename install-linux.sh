#!/bin/bash
# Jev-X for Linux (also works on macOS). Installs helpers, writes config, runs --doctor.
# Needs no Python on this machine: uses the prebuilt dist/jev-x binary if present,
# otherwise falls back to `python3 -m jev_x` for a dev checkout that has Python.
set -e; cd "$(dirname "$0")"
if command -v apt-get >/dev/null; then PM="sudo apt-get install -y"; PK="xdotool wmctrl scrot xclip libnotify-bin"; [ -n "$WAYLAND_DISPLAY" ] && PK="$PK grim wl-clipboard ydotool"
elif command -v dnf >/dev/null; then PM="sudo dnf install -y"; PK="xdotool wmctrl scrot xclip libnotify"; [ -n "$WAYLAND_DISPLAY" ] && PK="$PK grim wl-clipboard ydotool"
elif command -v pacman >/dev/null; then PM="sudo pacman -S --needed --noconfirm"; PK="xdotool wmctrl scrot xclip libnotify"; [ -n "$WAYLAND_DISPLAY" ] && PK="$PK grim wl-clipboard ydotool"
fi
[ -n "$PM" ] && [ "$(uname)" = Linux ] && { echo "Installing: $PK"; $PM $PK || echo "Some helpers failed to install; --doctor shows what is missing."; }
C=~/.config/jev-x; mkdir -p "$C"
[ -f "$C/config.json" ] || echo '{"base_url": "http://127.0.0.1:8089/v1", "model": "local"}' > "$C/config.json"
if [ -x ./dist/jev-x ]; then RUN=./dist/jev-x
elif command -v python3 >/dev/null; then RUN="python3 -m jev_x"
else echo "No dist/jev-x binary and no python3 found. Run ./build-jev-x.sh first, or install Python 3."; exit 1
fi
$RUN --doctor
echo "Run: $RUN            (chat)   |   $RUN --serve   (web UI)"
