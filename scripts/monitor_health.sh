#!/bin/bash
# AJSON Health Monitor
# Purpose: Monitor /healthz and restart uvicorn on consecutive failures

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/run/uvicorn.pid"
FAIL_COUNT_FILE="$PROJECT_ROOT/run/health_fail_count"
LAST_RESTART_FILE="$PROJECT_ROOT/run/last_restart_ts"
LOG_FILE="$PROJECT_ROOT/logs/monitor.log"
HEALTHZ_URL="http://127.0.0.1:8000/healthz"
MAX_FAILURES=3
COOLDOWN_SECONDS=300  # 5 minutes

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/run" "$PROJECT_ROOT/logs"

# Initialize fail count if not exists
if [ ! -f "$FAIL_COUNT_FILE" ]; then
    echo "0" > "$FAIL_COUNT_FILE"
fi

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if in cooldown period
check_cooldown() {
    if [ -f "$LAST_RESTART_FILE" ]; then
        LAST_RESTART=$(cat "$LAST_RESTART_FILE")
        CURRENT_TIME=$(date +%s)
        TIME_DIFF=$((CURRENT_TIME - LAST_RESTART))
        
        if [ $TIME_DIFF -lt $COOLDOWN_SECONDS ]; then
            REMAINING=$((COOLDOWN_SECONDS - TIME_DIFF))
            log "COOLDOWN: In cooldown period. ${REMAINING}s remaining."
            return 0  # In cooldown
        fi
    fi
    return 1  # Not in cooldown
}

# Health check
log "Health check: Checking $HEALTHZ_URL"
if curl -fsS --max-time 2 "$HEALTHZ_URL" > /dev/null 2>&1; then
    log "Health check: OK"
    echo "0" > "$FAIL_COUNT_FILE"
    exit 0
fi

# Health check failed
FAIL_COUNT=$(cat "$FAIL_COUNT_FILE")
FAIL_COUNT=$((FAIL_COUNT + 1))
echo "$FAIL_COUNT" > "$FAIL_COUNT_FILE"

log "Health check: FAILED (count: $FAIL_COUNT/$MAX_FAILURES)"

# Check if we need to restart
if [ $FAIL_COUNT -lt $MAX_FAILURES ]; then
    exit 0
fi

log "CRITICAL: Health check failed $MAX_FAILURES times consecutively"

# Check cooldown
if check_cooldown; then
    exit 0
fi

# Verify PID file exists
if [ ! -f "$PID_FILE" ]; then
    log "ERROR: PID file not found at $PID_FILE. Cannot verify process. Aborting restart."
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")
log "Found PID: $PID"

# Verify the PID is actually uvicorn for AJSON
if ! ps -p "$PID" > /dev/null 2>&1; then
    log "WARNING: Process $PID is not running. Removing stale PID file."
    rm -f "$PID_FILE"
    echo "0" > "$FAIL_COUNT_FILE"
    
    # Start server
    log "Starting server via start_server.sh"
    "$SCRIPT_DIR/start_server.sh" >> "$LOG_FILE" 2>&1
    
    # Update restart timestamp
    date +%s > "$LAST_RESTART_FILE"
    exit 0
fi

# Verify process command line contains "uvicorn" and "ajson.app:app"
PROCESS_CMD=$(ps -p "$PID" -o command= 2>/dev/null || echo "")
if ! echo "$PROCESS_CMD" | grep -q "uvicorn"; then
    log "ERROR: PID $PID does not appear to be uvicorn. Command: $PROCESS_CMD"
    log "ABORTING: Will not kill non-uvicorn process"
    exit 1
fi

if ! echo "$PROCESS_CMD" | grep -q "ajson.app:app"; then
    log "ERROR: PID $PID is uvicorn but not for ajson.app:app. Command: $PROCESS_CMD"
    log "ABORTING: Will not kill unrelated uvicorn process"
    exit 1
fi

log "Verified: PID $PID is uvicorn for ajson.app:app"
log "Attempting graceful shutdown with SIGTERM"

# Graceful shutdown
kill -TERM "$PID" 2>/dev/null || true

# Wait up to 5 seconds for graceful shutdown
for i in {1..5}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        log "Process $PID terminated gracefully"
        break
    fi
    sleep 1
done

# Check if still running
if ps -p "$PID" > /dev/null 2>&1; then
    log "WARNING: Process $PID still running after SIGTERM. NOT sending SIGKILL for safety."
    log "Manual intervention required. Aborting restart."
    exit 1
fi

# Clean up PID file
rm -f "$PID_FILE"

# Reset fail count
echo "0" > "$FAIL_COUNT_FILE"

# Start server
log "Starting server via start_server.sh"
"$SCRIPT_DIR/start_server.sh" >> "$LOG_FILE" 2>&1

# Update restart timestamp
date +%s > "$LAST_RESTART_FILE"

log "Restart completed successfully"
exit 0
