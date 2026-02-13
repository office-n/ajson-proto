#!/bin/bash
# scripts/verify_post_merge.sh
# Usage: bash scripts/verify_post_merge.sh

set -e

echo "=== 1. Git Status Check ==="
git fetch origin
HEAD_HASH=$(git rev-parse origin/main)
echo "origin/main HEAD: $HEAD_HASH"
git ls-remote --heads origin main

echo "=== 2. Critical Code Verification ==="
# Verify Phase 9.8.2 (Timezone Fix) is present (now via ajson.utils.time)
if grep -q "get_utc_iso" ajson/hands/allowlist.py; then
    echo "OK: Allowlist uses centralized time utility (get_utc_iso)."
else
    echo "NG: Allowlist missing centralized time utility usage!"
    exit 1
fi

echo "=== 3. Test Suite Verification ==="
# 3.1 Fast Tests
echo "--- Fast Tests ---"
./venv/bin/pytest -q tests/test_network_security.py tests/test_cli_main.py tests/test_approval_integration.py

# 3.2 Deprecation Warning Check
echo "--- Deprecation Check ---"
./venv/bin/pytest -q -W error::DeprecationWarning tests/test_network_security.py tests/test_cli_main.py tests/test_approval_integration.py

echo "--- 3.3 Functional CLI Test (Smoke) ---"
export APPROVAL_STORE_DB=test_post_merge.db
# Clean up previous run
rm -f $APPROVAL_STORE_DB

# Run allowlist add
echo "Running: allowlist add..."
python3 -m ajson.cli allowlist add smoke.test.com 443 --reason "Smoke Test"
if [ $? -eq 0 ]; then
    echo "OK: CLI command successful."
else
    echo "NG: CLI command failed."
    exit 1
fi

# Verify persistence
COUNT=$(sqlite3 $APPROVAL_STORE_DB "SELECT count(*) FROM allowlist_rules WHERE host_pattern='smoke.test.com'")
if [ "$COUNT" -eq 1 ]; then
    echo "OK: Data persisted in DB."
else
    echo "NG: Data not found in DB (Count: $COUNT)."
    exit 1
fi
rm -f $APPROVAL_STORE_DB
unset APPROVAL_STORE_DB

echo "=== 4. Boot Verification (Full) ==="
bash scripts/ants_boot.sh

echo "=== 5. Documentation Preflight ==="
bash scripts/ants_preflight.sh docs/ops/cli_user_guide.md
bash scripts/ants_preflight.sh docs/ops/admin_manual.md
bash scripts/ants_preflight.sh docs/ops/prod_readiness_checklist.md

echo "=== VERIFICATION SUCCESS (ChainRun v1.9) ==="
exit 0
