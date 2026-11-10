#!/bin/sh
# Jev for Linux: the hotkey (⌃⌥Space, as on the Mac), start at login, and first settings. Safe to run again.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
HOST="$HERE/host.py"
CFG="${JEV_DIR:-$HOME/.config/jev}"

# first settings only: never overwrite the user's own
mkdir -p "$CFG"
if [ ! -f "$CFG/settings.json" ]; then
  if curl -s -m 2 http://127.0.0.1:8089/v1/models >/dev/null 2>&1; then   # a local llama.cpp server is up: use it
    echo '{"client":"local","apiBase":"http://127.0.0.1:8089","input":"voice","speak":true}' > "$CFG/settings.json"
  else
    echo '{"input":"voice","speak":true}' > "$CFG/settings.json"
  fi
  chmod 600 "$CFG/settings.json"
fi

# speech in: faster-whisper in Jev's own folder (the system Python is externally managed)
PY="$HOME/.local/share/jev/py"
PYTHONPATH="$PY" python3 -c 'import faster_whisper' 2>/dev/null || pip install -q --target "$PY" faster-whisper
# browser agent + live system info
PYTHONPATH="$PY" python3 -c 'import playwright' 2>/dev/null || pip install -q --target "$PY" playwright
python3 -c 'import psutil' 2>/dev/null || pip install -q --target "$PY" psutil
# neural voice out (free, offline): Piper + a deep natural male voice
PYTHONPATH="$PY" python3 -c 'import piper' 2>/dev/null || pip install -q --target "$PY" piper-tts
VOICES="$HOME/.local/share/jev/voices"; mkdir -p "$VOICES"
if [ ! -s "$VOICES/en_US-ryan-medium.onnx" ]; then
  B=https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium
  curl -sL -o "$VOICES/en_US-ryan-medium.onnx" "$B/en_US-ryan-medium.onnx?download=true"
  curl -sL -o "$VOICES/en_US-ryan-medium.onnx.json" "$B/en_US-ryan-medium.onnx.json?download=true"
fi
if [ ! -s "$VOICES/hi_IN-pratham-medium.onnx" ]; then   # the Hindi voice: used by itself whenever the answer is in Hindi
  B=https://huggingface.co/rhasspy/piper-voices/resolve/main/hi/hi_IN/pratham/medium
  curl -sL -o "$VOICES/hi_IN-pratham-medium.onnx" "$B/hi_IN-pratham-medium.onnx?download=true"
  curl -sL -o "$VOICES/hi_IN-pratham-medium.onnx.json" "$B/hi_IN-pratham-medium.onnx.json?download=true"
fi

# the app in the app grid and the dock: clicking it opens the box, like the Mac menu-bar icon
# the native launcher (Rust): this binary is what the task manager and dock show as Jev
if command -v cargo >/dev/null; then
  (cd "$HERE/../launcher" && cargo build --release -q) && mkdir -p "$HOME/.local/bin" && cp "$HERE/../launcher/target/release/jev" "$HOME/.local/bin/jev"
fi
if [ -x "$HOME/.local/bin/jev" ]; then LAUNCH="env JEV_HOME='$HERE/..' '$HOME/.local/bin/jev'"; else LAUNCH="python3 '$HOST'"; fi
mkdir -p "$HOME/.local/share/applications"
rm -f "$HOME/.local/share/applications/atticus.desktop"
cat > "$HOME/.local/share/applications/jev.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Jev
Comment=Talk or type; Jev answers and acts on your computer
Exec=$LAUNCH
StartupNotify=false
Icon=$HERE/jev.png
StartupWMClass=Jev
Categories=Utility;
EOF
if command -v gsettings >/dev/null && gsettings list-schemas | grep -q '^org.gnome.shell$'; then
  FAV=$(gsettings get org.gnome.shell favorite-apps)
  case "$FAV" in *jev.desktop*) ;; "@as []"|"[]") gsettings set org.gnome.shell favorite-apps "['jev.desktop']" ;;
    *) gsettings set org.gnome.shell favorite-apps "${FAV%]}, 'jev.desktop']" ;; esac
fi

# GNOME: a custom shortcut runs `host.py --toggle` (Wayland lets no app grab a global key itself)
if command -v gsettings >/dev/null && gsettings list-schemas | grep -q org.gnome.settings-daemon.plugins.media-keys; then
  KEY=/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/jev/
  LIST=$(gsettings get org.gnome.settings-daemon.plugins.media-keys custom-keybindings)
  case "$LIST" in
    *"$KEY"*) ;;
    "@as []"|"[]") gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['$KEY']" ;;
    *) gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "${LIST%]}, '$KEY']" ;;
  esac
  S="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:$KEY"
  gsettings set "$S" name 'Jev'
  gsettings set "$S" command "env JEV_HOME='$(dirname "$HERE")' $HOME/.local/bin/jev --toggle"
  gsettings set "$S" binding '<Control><Alt>space'
else
  echo "Not GNOME: bind Ctrl+Alt+Space to: python3 '$HOST' --toggle"
fi

# start at login (Prefs "login": true on the Mac)
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/jev.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Jev
Exec=python3 '$HOST'
Icon=$HERE/jev.png
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF
echo "Jev installed. Press Ctrl+Alt+Space (or click Jev in the dock), talk, pause to send. Press again to send early."

# optional: let the AI run `sudo` for installs/services without re-asking each time.
# The system (not the AI) asks for your password once per terminal and caches it; the AI never sees it. Run with: sh install.sh --sudo
if [ "$1" = "--sudo" ]; then
  printf 'Defaults timestamp_timeout=240\n' | sudo tee /etc/sudoers.d/jev-timeout >/dev/null && sudo chmod 440 /etc/sudoers.d/jev-timeout
  python3 - "$CFG/settings.json" <<'PY'
import json,sys
p=sys.argv[1]
try: c=json.load(open(p))
except Exception: c={}
c['sudo']=True; json.dump(c,open(p,'w'))
PY
  echo "sudo caching on: the system asks for your password once per terminal, then remembers it for 4 hours. The AI never sees it."
fi

# Wayland window control: GNOME Shell extension (needs one log out/in to load, then it is on)
if command -v gnome-extensions >/dev/null; then
  mkdir -p ~/.local/share/gnome-shell/extensions && rm -rf ~/.local/share/gnome-shell/extensions/jev-windows@jev.local \
    && cp -r "$(dirname "$0")/ext/jev-windows@jev.local" ~/.local/share/gnome-shell/extensions/
  gnome-extensions enable jev-windows@jev.local 2>/dev/null || true
fi
