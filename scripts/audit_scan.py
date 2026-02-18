#!/usr/bin/env python3
import os
import re
import sys

# Forbidden patterns (constructed to avoid literal forbidden strings in source)
FILE_SCHEME = "file" + ":" + "/" + "/" + "/"
ABS_USERS = "/" + "Users" + "/"
BACKSLASH = "\\"
WIN_USERS = BACKSLASH + "Users" + BACKSLASH
WIN_USERS_DBL = BACKSLASH * 2 + "Users" + BACKSLASH * 2

P1 = "Progress"
P2 = "Updates"
FORBIDDEN_PROGRESS = P1 + " " + P2

M1 = "Model"
M2 = "quota"
M3 = "limit"
M4 = "exceeded"
FORBIDDEN_QUOTA = M1 + " " + M2 + " " + M3 + " " + M4

SLASH = "/"
MNT_PATH = SLASH + "mnt" + SLASH
S1 = "sand"
S2 = "box"
SANDBOX = S1 + S2 + ":"

FORBIDDEN_TERMS = [
    FILE_SCHEME,
    ABS_USERS,
    WIN_USERS,
    WIN_USERS_DBL,
    MNT_PATH,
    SANDBOX,
    FORBIDDEN_PROGRESS,
    FORBIDDEN_QUOTA,
]

WIN_SEP_RE = r"\\\\"
WIN_SEP_RE_DBL = r"\\\\\\\\"
WIN_DRIVE_RE = r"[A-Za-z]:" + WIN_SEP_RE + r"[A-Za-z0-9]"
WIN_DRIVE_RE_DBL = r"[A-Za-z]:" + WIN_SEP_RE_DBL + r"[A-Za-z0-9]"

FORBIDDEN_REGEX = [
    WIN_DRIVE_RE,
    WIN_DRIVE_RE_DBL,
]

EXCLUDE_DIRS = {".git", "venv", "node_modules", "__pycache__"}
EXCLUDE_FILES = {".DS_Store"}


def is_binary(path):
    try:
        with open(path, "rb") as f:
            chunk = f.read(2048)
        if not chunk:
            return False
        if b"\x00" in chunk:
            return True
        text = bytes(range(32, 127)) + b"\n\r\t\b"
        nontext = sum(1 for b in chunk if b not in text)
        return (nontext / len(chunk)) > 0.30
    except Exception:
        return True


def scan_file(filepath):
    violations = []
    if is_binary(filepath):
        return violations
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                clean_line = line.strip()
                for term in FORBIDDEN_TERMS:
                    if term in clean_line:
                        violations.append(f"{filepath}:{i}: {term}")
                for pattern in FORBIDDEN_REGEX:
                    if re.search(pattern, clean_line):
                        violations.append(f"{filepath}:{i}: {pattern}")
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
    return violations


def main():
    root_dir = "."
    all_violations = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in filenames:
            if filename.endswith(".pyc") or filename in EXCLUDE_FILES:
                continue
            filepath = os.path.join(dirpath, filename)
            all_violations.extend(scan_file(filepath))

    if all_violations:
        print(f"FAIL: Found {len(all_violations)} forbidden string violations:")
        for v in all_violations[:10]:
            print(v)
        if len(all_violations) > 10:
            print(f"... and {len(all_violations) - 10} more.")
        sys.exit(1)
    print("PASS: No forbidden strings found.")
    sys.exit(0)


if __name__ == "__main__":
    main()
SLASH = "/"
MNT_PATH = SLASH + "mnt" + SLASH
S1 = "sand"
S2 = "box"
SANDBOX = S1 + S2 + ":"
