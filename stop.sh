#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"

echo "=== Stopping FORGE Dev Services ==="

stopped=0

for service in backend frontend; do
  pidfile="$PID_DIR/$service.pid"
  if [ -f "$pidfile" ]; then
    pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      echo "Stopping $service (PID $pid)..."
      kill "$pid" 2>/dev/null
      for i in $(seq 1 10); do
        kill -0 "$pid" 2>/dev/null || break
        sleep 0.5
      done
      kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null
      stopped=$((stopped + 1))
    else
      echo "$service (PID $pid) already stopped."
    fi
    rm -f "$pidfile"
  fi
done

# Kill any stragglers on known ports
for port in 8000 8081; do
  pids=$(lsof -ti tcp:$port 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "Killing remaining processes on port $port..."
    echo "$pids" | xargs kill 2>/dev/null || true
    stopped=$((stopped + 1))
  fi
done

if [ "$stopped" -eq 0 ]; then
  echo "No services were running."
else
  echo "All services stopped."
fi
