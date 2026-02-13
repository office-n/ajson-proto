#!/bin/bash
# ants_preflight.sh
# Usage: bash scripts/ants_preflight.sh <report_file>

REPORT_FILE=$1

if [ -z "$REPORT_FILE" ]; then
  echo "Usage: $0 <report_file>"
  exit 1
fi

if [ ! -f "$REPORT_FILE" ]; then
  echo "Error: Report file '$REPORT_FILE' not found."
  exit 1
fi



# 1. JST Timestamp Check (Must be in first 5 lines)
HEADER=$(head -n 5 "$REPORT_FILE")
if ! echo "$HEADER" | grep -q "+09:00"; then
  echo "NG: First 5 lines must contain JST timestamp (+09:00)."
  exit 1
fi

# 2. Forbidden phrases check
if grep -q "Progress Updates" "$REPORT_FILE"; then
  echo "NG: Forbidden phrase 'Progress Updates' found in $REPORT_FILE. Use 'Final Report Only'."
  exit 1
fi
REPORT_COUNT=$(grep -c "^#.*Report" "$REPORT_FILE")
if [ "$REPORT_COUNT" -gt 1 ]; then
    echo "NG: Multiple '# ... Report' headers found. Ensure only ONE final report."
    exit 1
fi

# 3. English-only (ASCII ratio) check
# Strategy: Count total bytes vs ASCII bytes. If ASCII > 90%, it's likely English-only.
# Using 'wc -c' for total bytes and 'tr -cd "[[:print:]]\t\n" | wc -c' for ASCII printable.
TOTAL_BYTES=$(wc -c < "$REPORT_FILE")
ASCII_BYTES=$(tr -cd '\000-\177' < "$REPORT_FILE" | wc -c)

if [ "$TOTAL_BYTES" -gt 0 ]; then
  # Calculate ASCII ratio (integer math)
  RATIO=$(( 100 * ASCII_BYTES / TOTAL_BYTES ))
  if [ "$RATIO" -gt 90 ]; then
    echo "NG: Report content seems to be English-only (ASCII ratio: ${RATIO}%). Use Japanese."
    exit 1
  fi
fi

echo "OK: Preflight passed for $REPORT_FILE (JST OK, ASCII: ${RATIO}%)"
exit 0

