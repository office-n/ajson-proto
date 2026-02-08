#!/usr/bin/env bash
set -euo pipefail

# Configure Git to use the local hooks directory
git config core.hooksPath .githooks

echo "Git hooks configured successfully."
echo "core.hooksPath set to: $(git config core.hooksPath)"
