import os
import shutil
from typing import Optional

class WorktreeManager:
    """
    Manages task-specific work directories (Worktree).
    Ensures isolation between tasks.
    """
    def __init__(self, base_dir: str = "worktrees"):
        # Use absolute path to avoid ambiguity
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def create(self, task_id: str) -> str:
        """
        Creates a new worktree directory for a given task_id.
        """
        path = self.get_path(task_id)
        os.makedirs(path, exist_ok=True)
        return path

    def remove(self, task_id: str):
        """
        Removes the worktree directory for a given task_id.
        """
        path = self.get_path(task_id)
        if os.path.exists(path):
            shutil.rmtree(path)

    def get_path(self, task_id: str) -> str:
        """
        Returns the absolute path for a given task_id.
        """
        # Ensure task_id is safe for filesystem
        safe_id = "".join(c for c in task_id if c.isalnum() or c in ("-", "_")).rstrip()
        return os.path.join(self.base_dir, safe_id)

    def is_inside(self, task_id: str, sub_path: str) -> bool:
        """
        Checks if a given path is inside the worktree for task_id.
        Used for safety guards.
        """
        work_path = self.get_path(task_id)
        target_path = os.path.abspath(os.path.join(work_path, sub_path))
        return target_path.startswith(work_path)
