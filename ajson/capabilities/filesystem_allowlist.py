# ajson/capabilities/filesystem_allowlist.py
from ajson.core.tool import Tool
from ajson.core.policy import Policy

class FilesystemAllowlist(Tool):
    """
    A Tool wrapper for safe filesystem operations.
    """
    @property
    def name(self) -> str:
        return "filesystem_allowlist"

    @property
    def description(self) -> str:
        return "Safe filesystem operations within allowed directories."

    def execute(self, action: str, path: str, content: str = None) -> str:
        if not Policy.validate_path(path):
            return "Error: Path not allowed"
        
        # Stub implementation
        return f"Executed {action} on {path}"
