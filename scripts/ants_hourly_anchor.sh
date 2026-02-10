#!/bin/bash
# ants_hourly_anchor.sh
# Background job to refresh anchor every hour

while true; do
  bash scripts/ants_anchor.sh
  sleep 3600
done
