#!/bin/bash
# Pre-pytest hook: Run lint before all tests
# Usage: pytest --co (to check this runs) or pytest (to run)

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo ">>> Running lint before pytest..."
./scripts/lint_forbidden_strings.sh

echo ">>> Lint passed. Proceeding to pytest..."
