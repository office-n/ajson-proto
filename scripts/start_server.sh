#!/bin/bash
# AJSON Server Startup Script
# Purpose: Start uvicorn with PID tracking for safe monitoring

set -e

# --- Instrumentation ---
START_TS=$(date +%s.%N)


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/run/uvicorn.pid"
VENV_PATH="$PROJECT_ROOT/venv"

cd "$PROJECT_ROOT"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Server already running with PID: $OLD_PID"
        exit 0
    else
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Stale PID file found, removing..."
        rm -f "$PID_FILE"
    fi
fi

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Start uvicorn in background
echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting uvicorn..."
nohup uvicorn ajson.app:app --host 127.0.0.1 --port 8000 --reload \
    >> logs/uvicorn.log 2>&1 &

# Save PID
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Server started with PID: $SERVER_PID"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] PID saved to: $PID_FILE"

# Wait a moment and verify it started
sleep 2
if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    END_TS=$(date +%s.%N)
    DURATION=$(echo "$END_TS - $START_TS" | bc)
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Server verified running (Startup: ${DURATION}s)"
    exit 0
else
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: Server failed to start"
    rm -f "$PID_FILE"
    exit 1
fi
