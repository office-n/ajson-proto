#!/bin/bash
# scripts/prod_readiness.sh
# Usage: bash scripts/prod_readiness.sh

set -e

echo "=== AJSON Phase 10 Readiness Check ==="
echo "Timestamp: $(TZ=Asia/Tokyo date -Iseconds)"

echo "--- 1. Security & Network ---"
echo "[CHECK] Network Default (DENY)..."
if grep -q "allow_network *= *False" ajson/core/network.py; then
    echo "PASS: allow_network=False found."
else
    echo "FAIL: allow_network=False NOT found!"
    exit 1
fi

echo "[CHECK] Allowlist Rules..."
if [ -f "data/approvals.db" ]; then
    sqlite3 data/approvals.db "SELECT count(*) FROM allowlist_rules;" | xargs echo "Count:"
else
    echo "WARN: data/approvals.db not found (Clean slate?)"
fi

echo "[CHECK] Secrets in Log..."
if [ -f "logs/app.log" ]; then
    SUSPICIOUS=$(grep -iE "key|token|secret" logs/app.log | grep -v "masked" | wc -l)
    if [ "$SUSPICIOUS" -eq 0 ]; then
        echo "PASS: No unmasked secrets found."
    else
        echo "FAIL: $SUSPICIOUS suspicious lines found in logs/app.log!"
        exit 1
    fi
else
    echo "INFO: logs/app.log not found."
fi

echo "--- 2. Infrastructure ---"
echo "[CHECK] Persistence (DB)..."
if [ -f "data/approvals.db" ]; then
    echo "PASS: DB exists."
else
    echo "WARN: DB missing."
fi

echo "--- 3. Operations ---"
echo "[CHECK] Post-Merge Verification..."
bash scripts/verify_post_merge.sh

echo "--- 4. Documentation ---"
if [ -f "docs/ops/admin_manual.md" ]; then
    echo "PASS: Admin manual exists."
else
    echo "FAIL: Admin manual missing!"
    exit 1
fi

echo "=== READINESS CHECK COMPLETE: ALL PASS ==="
exit 0
