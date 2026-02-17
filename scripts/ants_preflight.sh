#!/bin/bash
# scripts/ants_preflight.sh
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

# ==============================================================================
# 1. JST Timestamp Check (Must be in first 5 lines)
# ==============================================================================
HEADER=$(head -n 5 "$REPORT_FILE")
if ! echo "$HEADER" | grep -qE "\+09:?00"; then
  echo "NG: First 5 lines must contain JST timestamp (+09:00 or +0900)."
  exit 1
fi

# ==============================================================================
# 2. Forbidden Phrases & Formats
# ==============================================================================
# 進捗小出しの禁止 (Progress Updates 等のテンプレ混入)
if grep -qiE "Progress Updates|Step ID: [0-9]+" "$REPORT_FILE"; then
  echo "NG: Forbidden progress-update metadata found in $REPORT_FILE."
  exit 1
fi

# 報告ヘッダーの単一性
REPORT_COUNT=$(grep -c "^#.*Report" "$REPORT_FILE")
if [ "$REPORT_COUNT" -gt 1 ]; then
    echo "NG: Multiple '# ... Report' headers found. Ensure only ONE final report."
    exit 1
fi

# ==============================================================================
# 3. English Error Messages (Quota/Limit/Funds)
# ==============================================================================
ERR_PHRASES="Model quota limit exceeded|Insufficient funds|Rate limit reached|Flash quota exceeded"
if grep -qiE "$ERR_PHRASES" "$REPORT_FILE"; then
  echo "NG: English error message found in report. Use Japanese explanation."
  echo "Found: $(grep -iE "$ERR_PHRASES" "$REPORT_FILE" | head -n 1)"
  exit 1
fi

# ==============================================================================
# 4. Forbidden Strings (Path info, sandboxes)
# ==============================================================================
FORBIDDEN_STRS="file:///|/Users/|\\\\Users\\\\|/mnt/|sandbox:"
if grep -qE "$FORBIDDEN_STRS" "$REPORT_FILE"; then
  echo "NG: Forbidden path information (e.g. /Users/...) found in $REPORT_FILE."
  echo "Line: $(grep -nE "$FORBIDDEN_STRS" "$REPORT_FILE" | head -n 1)"
  exit 1
fi

# ==============================================================================
# 5. Japanese-only Check (ASCII ratio)
# ==============================================================================
TOTAL_BYTES=$(wc -c < "$REPORT_FILE")
# 空ファイルは無視
if [ "$TOTAL_BYTES" -gt 0 ]; then
  ASCII_BYTES=$(tr -cd '\000-\177' < "$REPORT_FILE" | wc -c)
  RATIO=$(( 100 * ASCII_BYTES / TOTAL_BYTES ))
  if [ "$RATIO" -gt 90 ]; then
    echo "NG: Report seems to be English-only (ASCII ratio: ${RATIO}%). Japanese required."
    exit 1
  fi
fi

echo "OK: Preflight passed for $REPORT_FILE (JST OK, ASCII: ${RATIO}%)"
exit 0

