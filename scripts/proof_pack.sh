#!/usr/bin/env bash
set -euo pipefail

mkdir -p logs/proof
OUT="logs/proof/latest.md"

is_git() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1
}

{
  echo "## PROOF PACK"
  echo "- timestamp: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "- pwd: $(basename "$PWD")"
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
    echo ""
    echo "### staged diff (stat)"
    git diff --cached --stat || true
  else
    echo "- not a git repository: skipped"
    echo ""
    echo "### staged diff (stat)"
    echo "- skipped (non-git)"
  fi

  echo ""
  echo "### NOTE"
  echo "- このログが出せない作業は「未検証/未完了」扱い"
} > "$OUT"

echo "OK: wrote $OUT"
