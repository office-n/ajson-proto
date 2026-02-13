import os
import shutil
from typing import List, Optional

class FileSystemConnector:
    """
    Secure File System Connector for Local Host MVP (M2).
    Enforces access control to specific workspaces/worktrees.
    """
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir, exist_ok=True)

    def _safe_path(self, path: str) -> str:
        """
        Resolves path and ensures it is within root_dir.
        Raises ValueError if access is attempted outside root_dir.
        """
        target = os.path.abspath(os.path.join(self.root_dir, path))
        if not target.startswith(self.root_dir):
            raise ValueError(f"Security Violation: Path '{path}' is outside root_dir '{self.root_dir}'")
        return target

    def list_dir(self, path: str = ".") -> List[str]:
        target = self._safe_path(path)
        if not os.path.isdir(target):
            return []
        return os.listdir(target)

    def read_file(self, path: str) -> str:
        target = self._safe_path(path)
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str):
        target = self._safe_path(path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)

    def mkdir(self, path: str):
        target = self._safe_path(path)
        os.makedirs(target, exist_ok=True)

    def move(self, src: str, dst: str):
        s = self._safe_path(src)
        d = self._safe_path(dst)
        shutil.move(s, d)

    def remove(self, path: str, permanent: bool = False):
        """
        Remove path. If permanent is False, move to .trash/
        """
        target = self._safe_path(path)
        if not permanent:
            trash_dir = os.path.join(self.root_dir, ".trash")
            os.makedirs(trash_dir, exist_ok=True)
            shutil.move(target, os.path.join(trash_dir, os.path.basename(target)))
        else:
            # Governance check would be needed here in a full implementation
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
