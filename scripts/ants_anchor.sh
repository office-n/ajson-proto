#!/bin/bash
# ants_anchor.sh
# Generates JST timestamp anchor

mkdir -p .ants
TS=$(date "+%Y-%m-%dT%H:%M:%S%z" | sed -E 's/([+-][0-9]{2})([0-9]{2})/\1:\2/')
echo "$TS" > .ants/last_anchor_ts.txt
echo "Anchor updated: $TS (JST)"
exit 0
