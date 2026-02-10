#!/bin/bash
# ants_guard.sh
# Checks validity of anchor (must be < 1 hour old)

ANCHOR_FILE=".ants/last_anchor_ts.txt"

if [ ! -f "$ANCHOR_FILE" ]; then
  echo "NG: Anchor file missing. Run scripts/ants_anchor.sh first."
  exit 1
fi

# Get current time and file mtime
NOW=$(date +%s)
# portable way to get mtime? 'stat' varies.
# Let's use python for portability if available, or just 'stat -f %m' (BSD/Mac) vs 'stat -c %Y' (GNU).
# Since User is Mac, 'stat -f %m'.
MTIME=$(stat -f %m "$ANCHOR_FILE" 2>/dev/null || stat -c %Y "$ANCHOR_FILE" 2>/dev/null)

if [ -z "$MTIME" ]; then
   # Fallback if stat fails
   echo "Warning: Could not check anchor age. Assuming fresh."
   exit 0
fi

DIFF=$((NOW - MTIME))
LIMIT=3600

if [ "$DIFF" -gt "$LIMIT" ]; then
  echo "NG: Anchor expired (${DIFF}s old > ${LIMIT}s). Run scripts/ants_anchor.sh to refresh memory."
  exit 1
fi

echo "OK: Anchor fresh (${DIFF}s old)"
exit 0
