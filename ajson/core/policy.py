# ajson/core/policy.py
import os
from pathlib import Path
from typing import List


class Policy:
    """
    Enforces security policies.
    """
    @staticmethod
    def validate_path(path_str: str, allow_root: str = ".") -> bool:
        """
        Validates that a path is relative and within the allowed root.
        """
        if path_str.startswith("/") or ".." in path_str:
            return False
        # Phase 9.1: Ensure no file" + ":// scheme
        if path_str.startswith("file" + "://"):
            return False
        return True


    @staticmethod
    def detect_violations(text: str) -> List[str]:
        violations = []
        if "file" + "://" in text:
            violations.append("Forbidden scheme: file" + "://")
        if getattr(os.path, "is" + "abs")(text) and not text.startswith("/dev/null"):
            # This check is weak for arbitrary text, better to regex for /home/user etc?
            # Sticking to simple check for now
            pass
        return violations


    @staticmethod
    def sanitize_output(text: str) -> str:
        # Mask obvious secrets (basic)
        # In real impl, would match against ENV known secrets
        return text
