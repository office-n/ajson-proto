import pytest
import os
import sqlite3
import json
from ajson.core.scheduler_store_sqlite import SchedulerStore, TaskStatus

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_scheduler.db"
    return str(db_file)

@pytest.fixture
def store(temp_db):
    return SchedulerStore(db_path=temp_db)

def test_init_db(temp_db):
    store = SchedulerStore(db_path=temp_db)
    assert os.path.exists(temp_db)
    
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scheduler_tasks'")
        assert cursor.fetchone() is not None

def test_enqueue_dequeue(store):
    task_id = "task-1"
    payload = {"command": "echo hello"}
    
    # Enqueue
    store.enqueue(task_id, payload)
    
    # Dequeue
    task = store.dequeue()
    assert task is not None
    assert task['id'] == task_id
    assert task['state'] == TaskStatus.RUNNING.value
    assert task['payload'] == payload

def test_update_state(store):
    task_id = "task-2"
    store.enqueue(task_id, {"obj": "test"})
    
    store.update_state(task_id, TaskStatus.WAITING_APPROVAL)
    task = store.get_task(task_id)
    assert task['state'] == TaskStatus.WAITING_APPROVAL.value

def test_get_backlog(store):
    store.enqueue("t1", {"x": 1})
    store.enqueue("t2", {"x": 2})
    
    store.update_state("t1", TaskStatus.WAITING_APPROVAL)
    store.update_state("t2", TaskStatus.HOLD, hold_until="2099-01-01")
    
    backlog = store.get_backlog()
    assert len(backlog) == 2
    ids = [b['id'] for b in backlog]
    assert "t1" in ids
    assert "t2" in ids

def test_evidence_hash(store):
    task_id = "t3"
    store.enqueue(task_id, {"obj": "hash-test"})
    
    metadata = {"runlog": "docs/evidence/runlog.md", "user": "nakamurashingo"}
    h1 = store.set_evidence_hash(task_id, metadata)
    
    task = store.get_task(task_id)
    assert task['evidence_hash'] == h1
    assert len(h1) == 64  # SHA256 hex
    
    # Deterministic hash check
    h2 = store.set_evidence_hash("t-other", metadata)
    assert h1 == h2
