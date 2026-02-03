"""
SQLite database operations for AJSON MVP
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import os


DB_PATH = os.getenv("DB_PATH", "./ajson.db")


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Missions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Steps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            input_data TEXT NOT NULL,
            output_data TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mission_id) REFERENCES missions (id)
        )
    """)
    
    # Tool runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            result TEXT,
            blocked BOOLEAN NOT NULL DEFAULT 0,
            block_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (step_id) REFERENCES steps (id)
        )
    """)
    
    # Approvals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            gate_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (mission_id) REFERENCES missions (id)
        )
    """)
    
    # Artifacts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            artifact_type TEXT NOT NULL,
            path TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mission_id) REFERENCES missions (id)
        )
    """)
    
    # Memories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mission_id) REFERENCES missions (id)
        )
    """)
    
    # Uploads table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id TEXT PRIMARY KEY,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            mime_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Messages table (Phase6B)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mission_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            attachments_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mission_id) REFERENCES missions (id)
        )
    """)
    
    conn.commit()
    conn.close()


# Mission CRUD
def create_mission(title: str, description: str) -> int:
    """Create a new mission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO missions (title, description, status) VALUES (?, ?, ?)",
        (title, description, "CREATED")
    )
    mission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return mission_id


def get_mission(mission_id: int) -> Optional[Dict[str, Any]]:
    """Get mission by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM missions WHERE id = ?", (mission_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_mission_status(mission_id: int, status: str):
    """Update mission status"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE missions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, mission_id)
    )
    conn.commit()
    conn.close()


def list_missions() -> List[Dict[str, Any]]:
    """List all missions"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM missions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Step CRUD
def create_step(mission_id: int, role: str, input_data: str, status: str = "PENDING") -> int:
    """Create a new step"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO steps (mission_id, role, input_data, status) VALUES (?, ?, ?, ?)",
        (mission_id, role, input_data, status)
    )
    step_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return step_id


def update_step(step_id: int, output_data: str, status: str):
    """Update step output and status"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE steps SET output_data = ?, status = ? WHERE id = ?",
        (output_data, status, step_id)
    )
    conn.commit()
    conn.close()


def get_steps_by_mission(mission_id: int) -> List[Dict[str, Any]]:
    """Get all steps for a mission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM steps WHERE mission_id = ? ORDER BY created_at", (mission_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ToolRun CRUD
def create_tool_run(step_id: int, command: str, result: Optional[str] = None, 
                   blocked: bool = False, block_reason: Optional[str] = None) -> int:
    """Create a new tool run"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tool_runs (step_id, command, result, blocked, block_reason) VALUES (?, ?, ?, ?, ?)",
        (step_id, command, result, blocked, block_reason)
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id


def get_tool_runs_by_step(step_id: int) -> List[Dict[str, Any]]:
    """Get all tool runs for a step"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tool_runs WHERE step_id = ? ORDER BY created_at", (step_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_tool_runs_by_mission(mission_id: int) -> List[Dict[str, Any]]:
    """Get all tool runs for a mission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tr.* FROM tool_runs tr
        JOIN steps s ON tr.step_id = s.id
        WHERE s.mission_id = ?
        ORDER BY tr.created_at
    """, (mission_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Approval CRUD
def create_approval(mission_id: int, gate_type: str, reason: str) -> int:
    """Create a new approval request"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO approvals (mission_id, gate_type, reason, status) VALUES (?, ?, ?, ?)",
        (mission_id, gate_type, reason, "PENDING")
    )
    approval_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return approval_id


def approve_approval(approval_id: int):
    """Approve an approval request"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE approvals SET status = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?",
        ("APPROVED", approval_id)
    )
    conn.commit()
    conn.close()


def get_pending_approvals(mission_id: int) -> List[Dict[str, Any]]:
    """Get pending approvals for a mission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM approvals WHERE mission_id = ? AND status = ? ORDER BY created_at",
        (mission_id, "PENDING")
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Artifact CRUD
def create_artifact(mission_id: int, artifact_type: str, path: str, content: str) -> int:
    """Create a new artifact"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO artifacts (mission_id, artifact_type, path, content) VALUES (?, ?, ?, ?)",
        (mission_id, artifact_type, path, content)
    )
    artifact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return artifact_id


def get_artifacts_by_mission(mission_id: int) -> List[Dict[str, Any]]:
    """Get all artifacts for a mission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artifacts WHERE mission_id = ? ORDER BY created_at", (mission_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Memory CRUD
def create_memory(mission_id: int, key: str, value: str) -> int:
    """Create a new memory entry"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (mission_id, key, value) VALUES (?, ?, ?)",
        (mission_id, key, value)
    )
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memory_id


def get_memories_by_mission(mission_id: int) -> List[Dict[str, Any]]:
    """Get all memories for a mission"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories WHERE mission_id = ? ORDER BY created_at", (mission_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Upload CRUD
def create_upload(upload_id: str, original_name: str, stored_name: str, size: int, mime_type: str = None) -> str:
    """Create a new upload record"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO uploads (id, original_name, stored_name, size, mime_type) VALUES (?, ?, ?, ?, ?)",
        (upload_id, original_name, stored_name, size, mime_type)
    )
    conn.commit()
    conn.close()
    return upload_id


def get_upload(upload_id: str) -> Optional[Dict[str, Any]]:
    """Get upload by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM uploads WHERE id = ?", (upload_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_uploads_by_ids(upload_ids: List[str]) -> List[Dict[str, Any]]:
    """Get multiple uploads by their IDs"""
    if not upload_ids:
        return []
    
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(upload_ids))
    cursor.execute(f"SELECT * FROM uploads WHERE id IN ({placeholders})", upload_ids)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Message CRUD (Phase6B)
def create_message(mission_id: int, role: str, content: str, attachments_json: Optional[str] = None) -> int:
    """Create a new message"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (mission_id, role, content, attachments_json)
        VALUES (?, ?, ?, ?)
    """, (mission_id, role, content, attachments_json))
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id


def get_messages(mission_id: int) -> List[Dict[str, Any]]:
    """Get all messages for a mission, ordered by creation time"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM messages 
        WHERE mission_id = ?
        ORDER BY id ASC
    """, (mission_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
