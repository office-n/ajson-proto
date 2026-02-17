"""
SQLite-backed scheduler store for M3.
Handles task queuing, state persistence, and evidence hashing.
"""
import sqlite3
import json
import os
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class TaskStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    HOLD = "HOLD"


class SchedulerStore:
    """SQLite-backed storage for the Scheduler"""

    def __init__(self, db_path: str = "ajson.db"):
        """
        Initialize the scheduler store.
        
        Args:
            db_path: Path to the SQLite database. Relative to CWD.
        """
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize schema if not exists"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduler_tasks (
                    id TEXT PRIMARY KEY,
                    state TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    evidence_hash TEXT,
                    hold_until TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_scheduler_tasks_state 
                ON scheduler_tasks(state)
            """)
            # Evidence Chain Table (Append-Only)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_chain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    event_kind TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    curr_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def enqueue(self, task_id: str, payload: Dict[str, Any]) -> str:
        """Add a new task to the queue"""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO scheduler_tasks (id, state, payload_json) VALUES (?, ?, ?)",
                (task_id, TaskStatus.READY.value, json.dumps(payload))
            )
            self._append_evidence_tx(conn, task_id, "ENQUEUE", payload)
            conn.commit()
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task by ID"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM scheduler_tasks WHERE id = ?", (task_id,)).fetchone()
            if row:
                task = dict(row)
                task['payload'] = json.loads(task['payload_json'])
                return task
        return None

    def update_state(self, task_id: str, state: TaskStatus, hold_until: Optional[str] = None):
        """Update task state"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE scheduler_tasks SET state = ?, hold_until = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (state.value, hold_until, task_id)
            )
            self._append_evidence_tx(conn, task_id, f"UPDATE_STATE::{state.value}", {"hold_until": hold_until})
            conn.commit()

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get the next READY task and set to RUNNING"""
        with self._get_connection() as conn:
            # Simple FIFO: get oldest READY task
            row = conn.execute(
                "SELECT * FROM scheduler_tasks WHERE state = ? ORDER BY created_at ASC LIMIT 1",
                (TaskStatus.READY.value,)
            )
            task_row = row.fetchone()
            if task_row:
                task_id = task_row['id']
                conn.execute(
                    "UPDATE scheduler_tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (TaskStatus.RUNNING.value, task_id)
                )
                
                # Fetch again for return
                task = dict(task_row)
                task_payload = json.loads(task['payload_json'])
                
                self._append_evidence_tx(conn, task_id, "DEQUEUE", task_payload)
                conn.commit()

                task['state'] = TaskStatus.RUNNING.value
                task['payload'] = task_payload
                return task
        return None

    def get_backlog(self) -> List[Dict[str, Any]]:
        """Get tasks in WAITING_APPROVAL or HOLD state"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM scheduler_tasks WHERE state IN (?, ?) ORDER BY updated_at ASC",
                (TaskStatus.WAITING_APPROVAL.value, TaskStatus.HOLD.value)
            ).fetchall()
            return [dict(r) for r in rows]

    def set_evidence_hash(self, task_id: str, metadata: Dict[str, Any]):
        """Calculate and store hash of normalized metadata (Legacy wrapper + Chain append)"""
        # Chain append (This is the robust v2.1 implementation)
        with self._get_connection() as conn:
            curr_hash = self._append_evidence_tx(conn, task_id, "EVIDENCE_HASH", metadata)
            
            # Update legacy column for backward compatibility/quick lookup
            conn.execute(
                "UPDATE scheduler_tasks SET evidence_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (curr_hash, task_id)
            )
            conn.commit()
        return curr_hash

    def _append_evidence_tx(self, conn, task_id: str, kind: str, payload: Dict[str, Any]) -> str:
        """Internal: Append to evidence chain within a transaction"""
        # 1. Get last hash
        last_row = conn.execute("SELECT curr_hash FROM evidence_chain ORDER BY id DESC LIMIT 1").fetchone()
        prev_hash = last_row[0] if last_row else "0" * 64

        # 2. Normalize payload
        payload_json = json.dumps(payload, sort_keys=True)
        
        # 3. Calc new hash: sha256(prev + kind + task_id + payload)
        # We exclude timestamp from hash calculation to make it deterministic given the sequence,
        # but we store timestamp. Or should we include it?
        # Use simple deterministic verification: prev + kind + task_id + payload
        feed = f"{prev_hash}{kind}{task_id}{payload_json}"
        curr_hash = hashlib.sha256(feed.encode()).hexdigest()

        # 4. Insert
        conn.execute(
            "INSERT INTO evidence_chain (task_id, event_kind, payload_json, prev_hash, curr_hash) VALUES (?, ?, ?, ?, ?)",
            (task_id, kind, payload_json, prev_hash, curr_hash)
        )
        return curr_hash

