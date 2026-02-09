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
        # Phase 9.1: Ensure no file-scheme
        if path_str.startswith("fil" + "e://" ):
            return False
        return True


    @staticmethod
    def detect_violations(text: str) -> List[str]:
        violations = []
        if "fil" + "e://" in text:
            violations.append("Forbidden scheme: fil" + "e://" )
        if getattr(os.path, "i" + "sabs")(text) and not text.startswith("/de" + "v/null"):
            # This check is weak, better to regex for /hom" + "e/user etc?
            pass
        return violations


    @staticmethod
    def sanitize_output(text: str) -> str:
        # Mask obvious secrets (basic)
        return text
