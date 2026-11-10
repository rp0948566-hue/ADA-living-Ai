#!/bin/bash
# Starts llama-server on the local GGUF. Override with LLAMA_SERVER, MODEL, NGL, CTX, PORT.
LLAMA_SERVER="${LLAMA_SERVER:-$(command -v llama-server || echo "$HOME/Desktop/big model/llama.cpp/llama-b12198/llama-server")}"
MODEL="${MODEL:-$HOME/Desktop/big model/llama.cpp/gguf/qwen-27b-Q4_K_M.gguf}"
curl -s -m 2 "http://127.0.0.1:${PORT:-8089}/v1/models" >/dev/null && { echo "already running on ${PORT:-8089}"; exit 0; }
exec "$LLAMA_SERVER" -m "$MODEL" -ngl "${NGL:-24}" -c "${CTX:-8192}" --jinja --host 127.0.0.1 --port "${PORT:-8089}" --chat-template-kwargs '{"enable_thinking":false}'
