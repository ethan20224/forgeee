#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"
mkdir -p "$PID_DIR"

echo "=== FORGE Dev Services ==="

# --- Stop anything already running ---
"$SCRIPT_DIR/stop.sh" 2>/dev/null || true
echo ""

# --- Backend (FastAPI) ---
echo "[1/2] Starting backend (FastAPI on :8000)..."
cd "$SCRIPT_DIR/backend"
nohup bash -c 'source venv/bin/activate && exec uvicorn src.main:app --port 8000 --reload --host 0.0.0.0' \
  > "$PID_DIR/backend.log" 2>&1 &
disown
echo $! > "$PID_DIR/backend.pid"
echo "       PID $(cat "$PID_DIR/backend.pid")"

# Wait for backend to be reachable
echo -n "       Waiting for backend"
for i in $(seq 1 20); do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo " ready."
    break
  fi
  echo -n "."
  sleep 1
done

# --- Frontend (Expo + iOS Simulator) ---
echo "[2/2] Starting frontend (Expo → iOS Simulator)..."
echo "       Launching in this terminal (interactive mode required)."
echo ""
cd "$SCRIPT_DIR/mobile"
npx expo start --ios --port 8081
