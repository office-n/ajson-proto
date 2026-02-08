#!/usr/bin/env bash
set -euo pipefail

TASK_FILE="tickets/CURRENT_TASK.md"
LOCK_FILE="LOCKLIST.md"
BOOT_LOG="logs/boot/latest.md"

if [ ! -f "$TASK_FILE" ]; then
  echo "[GUARD] NG: $TASK_FILE がありません"
  exit 1
fi

# Allowlist抽出（「## 触っていいファイル（Allowlist）」セクションの - 行）
ALLOW_RAW=$(awk '
  $0 ~ /^## 触っていいファイル/ {flag=1; next}
  flag && $0 ~ /^## / {flag=0}
  flag {print}
' "$TASK_FILE" | grep -E '^\s*-\s+' || true)

if [ -z "$ALLOW_RAW" ]; then
  echo "[GUARD] NG: Allowlist が空です。CURRENT_TASK.md に許可パスを列挙してください。"
  exit 1
fi

ALLOW=$(echo "$ALLOW_RAW" | sed -E 's/^\s*-\s+//' | sed -E 's#^/##')

CHANGED=$(git diff --cached --name-only)

# --- PROOF GATE (anti-hallucination) ---
PROOF_LOG="logs/proof/latest.md"
NEEDS_PROOF=0
for cf in $CHANGED; do
  case "$cf" in
    logs/boot/latest.md) ;;
    logs/proof/latest.md) ;;
    tickets/*) ;;
    *) NEEDS_PROOF=1 ;;
  esac
done

if [ "$NEEDS_PROOF" -eq 1 ]; then
  if ! echo "$CHANGED" | grep -qx "$PROOF_LOG"; then
    echo "[GUARD] NG: 証跡ログが不足 → $PROOF_LOG（重要変更が含まれるため必須）"
    echo "[GUARD] 対応: bash scripts/proof_pack.sh → git add $PROOF_LOG"
    exit 1
  fi
fi
# --- /PROOF GATE ---

# 0) 起動ログ必須（毎コミット）
if ! echo "$CHANGED" | grep -qx "$BOOT_LOG"; then
  echo "[GUARD] NG: 起動ログがステージされていません → $BOOT_LOG"
  echo "[GUARD] 対応: scripts/ants_boot.sh を実行し、logs/boot/latest.md を更新して add してください。"
  exit 1
fi

# 1) Allowlist外禁止
for cf in $CHANGED; do
  ok=0
  for a in $ALLOW; do
    a="${a#/}"
    # ディレクトリ許可 (末尾が / の場合)
    if [[ "$a" == */ ]]; then
      # $cf が $a で始まるならOK
      if [[ "$cf" == "$a"* ]]; then ok=1; break; fi
    else
      # ファイル完全一致
      if [[ "$cf" == "$a" ]]; then ok=1; break; fi
    fi
  done
  if [ $ok -eq 0 ]; then
    echo "[GUARD] NG: Allowlist外の変更 → $cf"
    exit 1
  fi
done

# 2) LOCKLIST対象禁止
if [ -f "$LOCK_FILE" ]; then
  LOCKED=$(grep -vE '^\s*$|^\s*#' "$LOCK_FILE" || true)
  if [ -n "$LOCKED" ]; then
    for lf in $LOCKED; do
      lf="${lf#/}"
      if echo "$CHANGED" | grep -qx "$lf"; then
        echo "[GUARD] NG: LOCKLIST対象を変更 → $lf"
        exit 1
      fi
    done
  fi
fi

echo "[GUARD] OK"
# proof gate test
