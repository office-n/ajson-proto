#!/usr/bin/env python3
import os
import sys

# Forbidden patterns
FORBIDDEN_TERMS = [
    "file:///",
    "/Users/",
    "\\\\Users\\\\",
    "/mnt/",
    "sandbox:",
    "Progress Updates",
    "Model quota limit exceeded"
]

EXCLUDE_DIRS = {".git", "venv", "node_modules", "docs/evidence", "__pycache__"}
EXCLUDE_FILES = {"audit_scan.py", "phase10_audit.sh", "lint_forbidden_strings.sh", "ants_preflight.sh"}

def scan_file(filepath):
    violations = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                clean_line = line.strip()
                for term in FORBIDDEN_TERMS:
                    if term in clean_line:
                        # Allow self-reference in scripts if it looks like variable assignment
                        if os.path.basename(filepath) in EXCLUDE_FILES:
                            continue
                        violations.append(f"{filepath}:{i}: {term}")
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
    return violations

def main():
    root_dir = "."
    all_violations = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            if filename.endswith(".pyc") or filename.endswith(".DS_Store"):
                continue
                
            filepath = os.path.join(dirpath, filename)
            # Skip binary checks for simplicity (handled by unicode ignore in read)
            violations = scan_file(filepath)
            all_violations.extend(violations)

    if all_violations:
        print(f"FAIL: Found {len(all_violations)} forbidden string violations:")
        for v in all_violations[:10]:
            print(v)
        if len(all_violations) > 10:
            print(f"... and {len(all_violations) - 10} more.")
        sys.exit(1)
    else:
        print("PASS: No forbidden strings found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
