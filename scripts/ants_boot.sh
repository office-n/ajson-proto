#!/usr/bin/env bash
set -euo pipefail

# --- Instrumentation ---
START_TS=$(date +%s.%N)
LOG_DIR="logs/boot"
mkdir -p "$LOG_DIR"
OUT="$LOG_DIR/latest.md"
RUN_DIR="run"
mkdir -p "$RUN_DIR"

log_step() {
    local step_name="$1"
    local start_ts="$2"
    local end_ts=$(date +%s.%N)
    local duration=$(echo "$end_ts - $start_ts" | bc)
    echo "- **$step_name**: ${duration}s" >> "$OUT"
}

# --- Arguments ---
MODE="FAST"
if [[ "${1:-}" == "--full" ]]; then
    MODE="FULL"
fi

# --- Report Init ---
{
  echo "# Boot Log"
  echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "Mode: **$MODE**"
  echo ""
  echo "## Timings"
} > "$OUT"

# --- 1. Dependencies (Smart Skip) ---
STEP_START=$(date +%s.%N)
REQ_FILE="requirements.txt"
HASH_FILE="$RUN_DIR/requirements.hash"
CURRENT_HASH=""

if [ -f "$REQ_FILE" ]; then
    # md5 on mac, md5sum on linux
    if command -v md5 >/dev/null; then
        CURRENT_HASH=$(md5 -q "$REQ_FILE")
    else
        CURRENT_HASH=$(md5sum "$REQ_FILE" | awk '{print $1}')
    fi
fi

if [ -f "$HASH_FILE" ] && [ "$(cat "$HASH_FILE")" == "$CURRENT_HASH" ]; then
    echo "- Dependencies: Skipped (Hash Match)" >> "$OUT"
else
    echo "Installing dependencies..."
    # Ideally reuse existing venv or create new
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r "$REQ_FILE" >/dev/null 2>&1
    echo "$CURRENT_HASH" > "$HASH_FILE"
    echo "- Dependencies: Installed" >> "$OUT"
fi
log_step "Dependencies" "$STEP_START"

# --- 2. PACK Checks ---
STEP_START=$(date +%s.%N)
if [ -f "scripts/proof_pack.sh" ]; then
    bash scripts/proof_pack.sh >/dev/null 2>&1
    echo "- Pack Check: OK" >> "$OUT"
else
    echo "- Pack Check: Skipped (Missing script)" >> "$OUT"
fi
log_step "Pack Check" "$STEP_START"

# --- 3. Testing (FAST/FULL) ---
STEP_START=$(date +%s.%N)
source venv/bin/activate 2>/dev/null || true

if [ "$MODE" == "FAST" ]; then
    # FAST: Version check + Smoke (if available) or just a simple check
    # Ensuring critical path works without full regression
    if pytest -q --collect-only -m smoke >/dev/null 2>&1; then
        pytest -m smoke -q >/dev/null 2>&1
    else
        # Fallback if no smoke: just version/help to ensure import
        python -c "import ajson; print('Import OK')" >/dev/null 2>&1
    fi
    echo "- Tests: FAST (Smoke/Sanity Passed)" >> "$OUT"
else
    # FULL: Full pytest
    pytest -q >/dev/null 2>&1
    echo "- Tests: FULL (All Passed)" >> "$OUT"
fi
log_step "Testing ($MODE)" "$STEP_START"

# --- Finalize ---
TOTAL_DURATION=$(echo "$(date +%s.%N) - $START_TS" | bc)
echo ""
echo "## Total Time: ${TOTAL_DURATION}s" >> "$OUT"
echo "BOOT OK ($MODE)"
