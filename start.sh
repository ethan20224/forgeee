#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"
mkdir -p "$PID_DIR"

MODE="full"
PLATFORM=""
for arg in "$@"; do
  case "$arg" in
    --backend-only|--b) MODE="backend" ;;
    --no-launch|--n)    MODE="no-launch" ;;
    ios|android)        PLATFORM="$arg" ;;
    --help|-h)
      cat <<EOF
FORGE Dev Services
==================

Usage: ./start.sh [options] [platform]

Options:
  --n, --no-launch     Install the latest dev build, start backend + metro
                       bundler, but don't launch Expo's default simulator.
                       Requires a platform: ios or android.
  --b, --backend-only  Start only the backend (no metro/simulator). Use this
                       when running a preview or production build that has
                       the JS bundle embedded.
  --help, -h           Show this help message.

Typical workflows:
  ./start.sh                Full dev: backend + Expo with iOS Simulator
  ./start.sh --n ios        Install latest iOS build, start backend + metro
  ./start.sh --n android    Install latest Android build, start backend + metro
  ./start.sh --b            For preview/production builds: backend only

EOF
      exit 0
      ;;
  esac
done

if [ "$MODE" = "no-launch" ] && [ -z "$PLATFORM" ]; then
  echo "Error: --no-launch requires a platform (ios or android)."
  echo "Usage: ./start.sh --n ios   or   ./start.sh --n android"
  exit 1
fi

echo "=== FORGE Dev Services ==="

# --- Stop anything already running ---
"$SCRIPT_DIR/stop.sh" 2>/dev/null || true
echo ""

case "$MODE" in
  backend)    TOTAL_STEPS=1 ;;
  no-launch)  TOTAL_STEPS=3 ;;
  *)          TOTAL_STEPS=2 ;;
esac

# --- Backend (FastAPI) ---
echo "[1/$TOTAL_STEPS] Starting backend (FastAPI on :8000)..."
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

if [ "$MODE" = "backend" ]; then
  echo ""
  echo "Backend is running (--backend-only mode)."
  echo "Use this with preview/production builds that have JS bundled."
  echo "Use './stop.sh' to stop the backend when done."
  exit 0
fi

cd "$SCRIPT_DIR/mobile"

if [ "$MODE" = "no-launch" ]; then
  # --- Install latest build ---
  echo "[2/$TOTAL_STEPS] Installing latest $PLATFORM build..."
  eas build:run --platform "$PLATFORM" --profile development
  echo ""

  # --- Start metro bundler ---
  echo "[3/$TOTAL_STEPS] Starting metro bundler..."
  echo "       Open the installed FORGE app to connect."
  echo ""
  npx expo start --localhost --port 8081
else
  echo "[2/$TOTAL_STEPS] Starting frontend (Expo → iOS Simulator)..."
  echo "       Launching in this terminal (interactive mode required)."
  echo ""
  npx expo start --localhost --ios --port 8081
fi
