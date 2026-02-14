from typing import List, Optional, Dict, Any
from ajson.core.scheduler_store_sqlite import SchedulerStore, TaskStatus

class Scheduler:
    """
    M3 Scheduler Implementation.
    Handles task queueing and persistent state management using SQLite.
    Supports asynchronous control (non-blocking WAITING_APPROVAL).
    """
    def __init__(self, db_path: str = "ajson.db"):
        self.store = SchedulerStore(db_path=db_path)

    def enqueue(self, task_id: str, objective: str, payload_extra: Optional[Dict[str, Any]] = None):
        """Register a new task in READY state"""
        payload = {"objective": objective}
        if payload_extra:
            payload.update(payload_extra)
        
        self.store.enqueue(task_id, payload)
        print(f"[Scheduler] Enqueued task {task_id}: {objective}")

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Fetch the next READY task and mark it as RUNNING"""
        task = self.store.dequeue()
        if task:
            print(f"[Scheduler] Dequeued task {task['id']}")
        return task

    def ack(self, task_id: str):
        """Mark task as DONE"""
        self.store.update_state(task_id, TaskStatus.DONE)
        print(f"[Scheduler] Task {task_id} marked as DONE (ack)")

    def nack(self, task_id: str):
        """Mark task as FAILED"""
        self.store.update_state(task_id, TaskStatus.FAILED)
        print(f"[Scheduler] Task {task_id} marked as FAILED (nack)")

    def hold(self, task_id: str, hold_until: Optional[str] = None):
        """Mark task as HOLD or WAITING_APPROVAL"""
        # If no time given, it's likely a WAITING_APPROVAL (indefinite hold)
        status = TaskStatus.WAITING_APPROVAL if not hold_until else TaskStatus.HOLD
        self.store.update_state(task_id, status, hold_until=hold_until)
        print(f"[Scheduler] Task {task_id} status -> {status.value} (hold until: {hold_until})")

    def checkpoint(self, task_id: str, evidence_metadata: Dict[str, Any]):
        """Record evidence hash based on normalized metadata"""
        #Normalization logic inside store.set_evidence_hash for now
        evidence_hash = self.store.set_evidence_hash(task_id, evidence_metadata)
        print(f"[Scheduler] Checkpoint for {task_id}: Hash={evidence_hash[:8]}...")

    def get_backlog(self) -> List[Dict[str, Any]]:
        """Retrieve tasks that are in HOLD or WAITING_APPROVAL"""
        return self.store.get_backlog()
