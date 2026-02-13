from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"

class Scheduler:
    """
    M3 Scheduler Scaffolding.
    Handles task queueing and persistent state management (to be fully implemented).
    """
    def __init__(self, db_path: str = "ajson.db"):
        self.db_path = db_path
        # Schema initialization will go here in next phase

    def enqueue(self, task_id: str, objective: str):
        """Register a new task in PENDING state"""
        # DB Insert stub
        print(f"[Scheduler] Enqueued task {task_id}: {objective}")

    def update_status(self, task_id: str, status: TaskStatus):
        """Update task status and timestamp"""
        # DB Update stub
        print(f"[Scheduler] Task {task_id} status -> {status.value}")

    def get_pending_tasks(self) -> List[str]:
        """Fetch all PENDING task IDs"""
        return []

    def checkpoint(self, task_id: str, evidence_data: Dict[str, Any]):
        """Record evidence hash and metadata"""
        # DB Evidence Insert stub
        print(f"[Scheduler] Checkpoint for {task_id}: {list(evidence_data.keys())}")
