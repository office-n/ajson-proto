#!/bin/bash
# scripts/phase10_audit.sh
# Purpose: Comprehensive Phase 10 Quality Audit (Execution focused)
# v1.2 - Env-independent (python3/grep fallback)
set -e
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m"

echo ">>> Starting Phase 10 Quality Audit..."
CURRENT_MAIN_HEAD=$(git rev-parse origin/main 2>/dev/null || echo "UNKNOWN")
echo "[1/4] origin/main HEAD: ${CURRENT_MAIN_HEAD}"
echo "[2/4] Running mandatory command checks..."

# Determine python command
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "${RED}CRITICAL: python3/python not found.${NC}"
    exit 1
fi
echo "  - Using Python: $PYTHON_CMD"

# Determine pytest execution command
if $PYTHON_CMD -m pytest --version >/dev/null 2>&1; then
    PYTEST_CMD="$PYTHON_CMD -m pytest"
elif [ -f "./venv/bin/pytest" ]; then
    PYTEST_CMD="./venv/bin/pytest"
else
    PYTEST_CMD="pytest"
fi
echo "  - Using Pytest: $PYTEST_CMD"

set +e
echo "  - Running pytest (Normal)..."
if ${PYTEST_CMD} -q tests/test_*.py --override-ini="python_files=test_*.py" -p no:conftest > /dev/null 2>&1; then
    PYTEST_RES="PASS"; echo "    ${GREEN}PASS: pytest${NC}"
else
    PYTEST_RES="FAIL"; echo "    ${RED}FAIL: pytest${NC}"
fi

echo "  - Running pytest (Werror: DeprecationWarning)..."
# Using -W ignore::DeprecationWarning:pydantic to filter known valid warnings
if ${PYTEST_CMD} -q tests/test_*.py --override-ini="python_files=test_*.py" -p no:conftest -W error::DeprecationWarning -W ignore::DeprecationWarning:pydantic > /dev/null 2>&1; then
    WERROR_RES="PASS"; echo "    ${GREEN}PASS: DeprecationWarning Check${NC}"
else
    WERROR_RES="FAIL"; echo "    ${RED}FAIL: DeprecationWarning Check${NC}"
fi

# Boot check might use python, so ensure it uses the correct one if possible, or just rely on script
echo "  - Running ants_boot.sh..."
if bash scripts/ants_boot.sh | grep -q "BOOT OK"; then
    BOOT_RES="PASS"; echo "    ${GREEN}PASS: ants_boot.sh${NC}"
else
    BOOT_RES="FAIL"; echo "    ${RED}FAIL: ants_boot.sh${NC}"
fi
set -e

echo "[3/4] Scanning for forbidden strings..."
TMP_VIOLATIONS="/tmp/audit_violations.txt"
if python3 scripts/audit_scan.py > "${TMP_VIOLATIONS}" 2>&1; then
    STRINGS_RES="PASS"; echo "    ${GREEN}PASS: No forbidden strings found.${NC}"
else
    STRINGS_RES="FAIL"; echo "    ${RED}FAIL: Forbidden strings detected!${NC}"
    head -n 5 "${TMP_VIOLATIONS}"
fi

# 4. Environment Stability
STABILITY_RES="OK"
if [ -f "/tmp/audit_violations.txt" ]; then
    VIOLATION_COUNT=$(wc -l < /tmp/audit_violations.txt)
    if [ "${VIOLATION_COUNT}" -gt 100 ]; then
        STABILITY_RES="WARN (Large Violations)"
    fi
fi

# 5. Evidence Template Generation
echo "[4/4] Generating evidence template..."
mkdir -p docs/evidence
TIMESTAMP=$(date +%Y-%m-%dT%H:%M:%S%z)
REPORT_FILE="docs/evidence/audit_report_$(date +%Y%m%d_%H%M%S).md"

echo "# Phase 10 Audit Report" > "${REPORT_FILE}"
echo "- **Date**: ${TIMESTAMP}" >> "${REPORT_FILE}"
echo "- **Main HEAD**: ${CURRENT_MAIN_HEAD}" >> "${REPORT_FILE}"
echo "- **Audit Tool**: phase10_audit.sh v1.2" >> "${REPORT_FILE}"
echo "## Results" >> "${REPORT_FILE}"
echo "- **pytest**: ${PYTEST_RES}" >> "${REPORT_FILE}"
echo "- **DeprecationWarning**: ${WERROR_RES}" >> "${REPORT_FILE}"
echo "- **ants_boot**: ${BOOT_RES}" >> "${REPORT_FILE}"
echo "- **Forbidden Strings**: ${STRINGS_RES}" >> "${REPORT_FILE}"
echo "- **Environment Stability**: ${STABILITY_RES}" >> "${REPORT_FILE}"

if [ "${PYTEST_RES}" = "PASS" ] && [ "${WERROR_RES}" = "PASS" ] && [ "${BOOT_RES}" = "PASS" ] && [ "${STRINGS_RES}" = "PASS" ]; then
    echo "✅ PASS" >> "${REPORT_FILE}"
    echo "    ${GREEN}SUCCESS: ${REPORT_FILE}${NC}"
    echo ">>> Phase 10 Audit: ALL PASS"
    exit 0
else
    echo "❌ FAIL" >> "${REPORT_FILE}"
    echo "    ${RED}FAILED: See ${REPORT_FILE}${NC}"
    exit 1
fi
