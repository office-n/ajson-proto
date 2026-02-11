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



# 1. JST Timestamp Check (First line must contain +09:00)
FIRST_LINE=$(head -n 1 "$REPORT_FILE")
if ! echo "$FIRST_LINE" | grep -q "+09:00"; then
  echo "NG: First line must contain JST timestamp (+09:00). Found: $FIRST_LINE"
  exit 1
fi

# 2. Forbidden phrases check
if grep -q "Progress Updates" "$REPORT_FILE"; then
  echo "NG: Forbidden phrase 'Progress Updates' found in $REPORT_FILE. Use 'Final Report Only'."
  exit 1
fi
if grep -c "^#.*Report" "$REPORT_FILE" | grep -q -v "^1$"; then
    # Warning only for now, as some valid reports might have multiple sections
    echo "WARNING: Multiple '# ... Report' headers found. Ensure only ONE final report."
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

