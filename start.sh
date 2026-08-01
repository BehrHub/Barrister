#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT=8993
PYTHON="$ROOT/.venv/bin/python3"

cd "$ROOT"

if [ ! -x "$PYTHON" ]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/python3" -m pip install --upgrade pip
  "$ROOT/.venv/bin/python3" -m pip install -r requirements.txt
fi

"$PYTHON" -m py_compile app.py

PID="$(lsof -tiTCP:$PORT -sTCP:LISTEN 2>/dev/null | head -n 1 || true)"
if [ -n "$PID" ]; then
  kill "$PID" 2>/dev/null || true
  sleep 2
fi

nohup "$PYTHON" -m streamlit run app.py \
  --server.address 0.0.0.0 \
  --server.port "$PORT" \
  --server.headless true \
  > "$ROOT/test-8993.log" 2>&1 </dev/null &

sleep 8

curl -fsS "http://127.0.0.1:$PORT/" >/dev/null || {
  echo "ERROR: local preview failed"
  tail -n 120 "$ROOT/test-8993.log"
  exit 1
}

echo "LOCAL PREVIEW: http://100.70.235.51:8993"
