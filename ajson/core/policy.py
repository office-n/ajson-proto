# ajson/core/policy.py
import os
from pathlib import Path

class Policy:
    """
    Enforces security policies.
    """
    @staticmethod
    def validate_path(path_str: str, allow_root: str = ".") -> bool:
        """
        Validates that a path is relative and within the allowed root.
        """
        # Stub logic
        if path_str.startswith("/"):
            return False
        return True
