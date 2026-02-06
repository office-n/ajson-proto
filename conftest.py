"""
pytest configuration with pre-test lint check
"""
import subprocess
import sys


def pytest_sessionstart(session):
    """Run lint before pytest session starts"""
    print("\n>>> Running forbidden strings lint before tests...")
    result = subprocess.run(
        ["./scripts/lint_forbidden_strings.sh"],
        cwd=session.config.rootpath,
        capture_output=False
    )
    if result.returncode != 0:
        print("❌ Lint failed. Please fix violations before running tests.")
        sys.exit(1)
    print("✅ Lint passed. Proceeding to tests...\n")
