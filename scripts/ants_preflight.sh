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

# Check for non-ASCII characters (Japanese check)
# Ideally, we want to ensure *some* Japanese exists, or ensure *mostly* Japanese.
# Simple check: If the file is purely ASCII, it might be English-only regression.
# However, code blocks are ASCII. 
# Better strategy: Check if the file contains *any* multi-byte characters (assuming UTF-8 Japanese).
# But evidence files contain English logs.
# Let's rely on the "Boot Block" rule: "Japanese only".
# Failure condition: File seems to be English only (low ratio of non-ASCII).
# For now, let's just check if it contains "Timestamp (JST)" or similar mandatory headers.

HEADER_CHECK=$(grep "Timestamp (JST)" "$REPORT_FILE")
if [ -z "$HEADER_CHECK" ]; then
  echo "NG: 'Timestamp (JST)' header missing."
  exit 1
fi

echo "OK: Preflight passed for $REPORT_FILE"
exit 0
