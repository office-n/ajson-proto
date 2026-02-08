#!/usr/bin/env bash
set -euo pipefail

mkdir -p logs/boot
OUT="logs/boot/latest.md"

is_git() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1
}

{
  echo "## BOOT PACK"
  echo "- timestamp: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "- pwd: $(basename "$PWD")"
  echo ""

  echo "### PACK LINK CHECK"
  for f in ".cursorrules" ".githooks/pre-commit" "scripts/guardrails.sh" "scripts/proof_pack.sh"; do
    if [ -e "$f" ] || [ -L "$f" ]; then
      echo "- $f: OK"
    else
      echo "- $f: NG (missing)"
    fi
  done
  echo ""

  echo "### GIT"
  if is_git; then
    echo "- hooksPath: $(git config core.hooksPath 2>/dev/null || echo 'N/A')"
    echo ""
    echo "### git status (porcelain)"
    git status --porcelain || true
    echo ""
    echo "### git log -5"
    git log --oneline -5 || true
  else
    echo "- not a git repository: skipped"
  fi
  echo ""
  echo "### NOTE"
  echo "- non-git folders are 'All Green' if PACK LINK CHECK is OK and logs update."
} > "$OUT"

echo "BOOT OK -> $OUT updated"
