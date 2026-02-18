#!/bin/bash
set -e
# Phase 10 Audit Script
# Wrapper for all audit checks required for Phase 10 compliance.

echo "=== Starting Phase 10 Audit ==="

# 1. Forbidden Strings Lint
if [ -f "./scripts/lint_forbidden_strings.sh" ]; then
    ./scripts/lint_forbidden_strings.sh
else
    echo "Error: scripts/lint_forbidden_strings.sh not found!"
    exit 1
fi

echo "=== Phase 10 Audit Complete ==="

