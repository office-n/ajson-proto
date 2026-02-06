#!/bin/bash
# Generate com.ajson.healthmonitor.plist from template
# Usage: ./generate_healthmonitor_plist.sh

set -e

# Determine AJSON_ROOT (current repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AJSON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Output path
OUTPUT_PATH="$HOME/Library/LaunchAgents/com.ajson.healthmonitor.plist"

# Template path
TEMPLATE_PATH="$SCRIPT_DIR/com.ajson.healthmonitor.plist.example"

# Generate plist by replacing {{AJSON_ROOT}}
sed "s|{{AJSON_ROOT}}|$AJSON_ROOT|g" "$TEMPLATE_PATH" > "$OUTPUT_PATH"

echo "Generated: $OUTPUT_PATH"
echo "AJSON_ROOT: $AJSON_ROOT"
echo ""
echo "To load:"
echo "  launchctl load $OUTPUT_PATH"
echo ""
echo "To unload:"
echo "  launchctl unload $OUTPUT_PATH"
