#!/bin/bash
# Waits for the Kokoro downloads, then fetches Ollama and the model. Resumable (-C -).
cd "/home/claude/Desktop/my ai/jeb/models"
while pgrep -f "kokoro-v1.0.onnx|voices-v1.0.bin" >/dev/null; do sleep 20; done
[ -s voices-v1.0.bin ] || curl -sL -C - -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
mkdir -p ~/.local/ollama && cd ~/.local/ollama
until curl -sL -C - -o ollama.tar.zst https://github.com/ollama/ollama/releases/download/v0.40.13/ollama-linux-amd64.tar.zst; do sleep 10; done
zstd -dc ollama.tar.zst | tar x -C ~/.local/ollama && ln -sf ~/.local/ollama/bin/ollama ~/.local/bin/ollama
(~/.local/bin/ollama serve >/dev/null 2>&1 &) ; sleep 5
until ~/.local/bin/ollama pull llama3.1:8b; do sleep 10; done
echo done > ~/.local/ollama/READY
