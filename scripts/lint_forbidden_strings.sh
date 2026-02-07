#!/bin/bash
# Lint forbidden strings in repository
# Prevents commit of sensitive data and policy violations

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== Forbidden Strings Lint ==="
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Exclude patterns
EXCLUDE_DIRS="--exclude-dir=.git --exclude-dir=venv --exclude-dir=__pycache__ --exclude-dir=node_modules --exclude-dir=docs"
EXCLUDE_FILES="--exclude=*.pyc --exclude=*.log"

# Violation counter
VIOLATIONS=0

# Check 1: file:// scheme (absolute file paths)
# Pattern constructed dynamically to avoid self-detection
PATTERN_FILE_SCHEME="file""://"
echo "Check 1: file:// scheme"
if grep -rIn "$PATTERN_FILE_SCHEME" . $EXCLUDE_DIRS $EXCLUDE_FILES 2>/dev/null | grep -v "lint_forbidden_strings.sh"; then
    echo "❌ VIOLATION: file:// scheme found"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ OK: No file:// scheme"
fi
echo ""

# Check 2: Absolute paths (/Users/, /home/)
# Pattern constructed dynamically to avoid self-detection
PATTERN_USERS="/""Users/"
PATTERN_HOME="/""home/"
echo "Check 2: Absolute paths"
if grep -rIn "$PATTERN_USERS\|$PATTERN_HOME" . $EXCLUDE_DIRS $EXCLUDE_FILES 2>/dev/null | grep -v "lint_forbidden_strings.sh"; then
    echo "❌ VIOLATION: Absolute paths found"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ OK: No absolute paths"
fi
echo ""

# Check 3: API key patterns (sk-, AIza, etc.)
echo "Check 3: API key patterns"
if grep -rInE "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z\\-_]{20,}" . $EXCLUDE_DIRS $EXCLUDE_FILES 2>/dev/null | grep -v ".env.example" | grep -v "README.md" | grep -v "docs/" | grep -v "tests/" | grep -v "scripts/lint_forbidden_strings.sh"; then
    echo "❌ VIOLATION: API key patterns found (not in safe files)"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo "✅ OK: No API key patterns (or only in safe files)"
fi
echo ""

# Check 4: force push commands
echo "Check 4: force push commands"
if grep -rIn "git push.*--force\|git push.*-f " . $EXCLUDE_DIRS $EXCLUDE_FILES 2>/dev/null | grep -v "lint_forbidden_strings.sh" | grep -v ".md:"; then
    echo "⚠️  WARNING: force push commands found (should be in evidence only)"
    # Not counted as violation if in .md files (evidence)
else
    echo "✅ OK: No force push commands"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ $VIOLATIONS -eq 0 ]; then
    echo "✅ PASS: No violations found"
    exit 0
else
    echo "❌ FAIL: $VIOLATIONS violation(s) found"
    echo ""
    echo "Please fix the violations before committing."
    echo "Forbidden patterns:"
    echo "  - file-scheme URLs (use relative paths)"
    echo "  - absolute local paths (use relative paths or placeholders)"
    echo "  - API key patterns (use environment variables or Keychain)"
    exit 1
fi
