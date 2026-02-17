"""
SQLite-backed approval store (opt-in persistence)

Provides persistent storage for approval requests, grants, and decisions.
Activated via APPROVAL_STORE_DB environment variable.
"""
import sqlite3
import json
from datetime import datetime, timedelta, timezone
from ajson.utils.time import get_utc_iso, get_utc_now
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import os
from ajson.hands.domain import ApprovalRequest, ApprovalGrant, ApprovalDecision


@dataclass
class SQLiteApprovalStore:
    """SQLite-backed approval store"""
    
    def __init__(self, db_path: str = "data/approvals.db"):
        """
        Initialize SQLite approval store
        
        Args:
            db_path: Relative path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """Ensure database and tables exist"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    request_id TEXT PRIMARY KEY,
                    operation TEXT NOT NULL,
                    category TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS grants (
                    grant_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES requests(request_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_requests_status 
                ON requests(status)
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS allowlist_rules (
                    rule_id TEXT PRIMARY KEY,
                    host_pattern TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def create_request(
        self,
        operation: str,
        category: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """Create approval request"""
        import uuid
        
        request = ApprovalRequest(
            request_id=str(uuid.uuid4()),
            operation=operation,
            category=category,
            reason=reason,
            status="pending",
            metadata=metadata or {},
            created_at=get_utc_iso()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO requests 
                   (request_id, operation, category, reason, status, metadata, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    request.request_id,
                    request.operation,
                    request.category,
                    request.reason,
                    request.status,
                    json.dumps(request.metadata),
                    request.created_at
                )
            )
            conn.commit()
        
        return request
    
    def get_pending(self) -> List[ApprovalRequest]:
        """Get all pending approval requests"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM requests WHERE status = 'pending' ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
        
        return [
            ApprovalRequest(
                request_id=row['request_id'],
                operation=row['operation'],
                category=row['category'],
                reason=row['reason'],
                status=row['status'],
                metadata=json.loads(row['metadata']),
                created_at=row['created_at']
            )
            for row in rows
        ]
    
    def approve_request(self, request_id: str, decision: ApprovalDecision) -> ApprovalGrant:
        """Approve request and create grant"""
        import uuid
        
        # We need to fetch the request to get the operation
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT operation FROM requests WHERE request_id = ?", (request_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Request {request_id} not found")
            operation = row['operation']

        grant = ApprovalGrant(
            grant_id=str(uuid.uuid4()),
            request_id=request_id,
            operation=operation,
            scope=decision.scope,
            expires_at=(get_utc_now() + timedelta(hours=1)).isoformat(),
            granted_at=get_utc_iso()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            # Update request status
            conn.execute(
                "UPDATE requests SET status = 'approved' WHERE request_id = ?",
                (request_id,)
            )
            
            # Create grant
            # Note: storing granted_at in created_at column
            conn.execute(
                """INSERT INTO grants 
                   (grant_id, request_id, scope, expires_at, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    grant.grant_id,
                    grant.request_id,
                    json.dumps(grant.scope),
                    grant.expires_at,
                    grant.granted_at
                )
            )
            conn.commit()
        
        return grant
    
    def deny_request(self, request_id: str, reason: str):
        """Deny approval request"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE requests SET status = 'denied' WHERE request_id = ?",
                (request_id,)
            )
            conn.commit()
    
    def verify_grant(self, grant_id: str, operation: str) -> bool:
        """Verify grant is valid and operation is in scope"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM grants WHERE grant_id = ?",
                (grant_id,)
            )
            row = cursor.fetchone()
        
        if not row:
            return False
        
        # Check expiration
        expires_at = datetime.fromisoformat(row['expires_at'])
        if get_utc_now() > expires_at:
            return False
        
        # Check scope
        scope = json.loads(row['scope'])
        # operation check logic duplicated from domain or reused?
        # domain grant has matches_scope method.
        # But we need to hydrate the object to use it, OR dup the logic.
        # Reuse domain logic is better.
        # But we need 'operation' field to hydrate.
        # Fetch operation from requests
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT operation FROM requests WHERE request_id = ?", (row['request_id'],))
            req_row = cursor.fetchone()
            op_stored = req_row[0] if req_row else ""
            
        grant = ApprovalGrant(
             grant_id=row['grant_id'],
             request_id=row['request_id'],
             operation=op_stored,
             scope=scope,
             expires_at=row['expires_at'],
             granted_at=row['created_at']
        )
        return grant.matches_scope(operation)
    
    def get_active_grants(self) -> List[ApprovalGrant]:
        """Get all active (non-expired) grants"""
        now = get_utc_iso()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # JOIN to get operation
            cursor = conn.execute(
                """
                SELECT g.*, r.operation 
                FROM grants g 
                JOIN requests r ON g.request_id = r.request_id 
                WHERE g.expires_at > ? 
                ORDER BY g.created_at DESC
                """,
                (now,)
            )
            rows = cursor.fetchall()
        
        return [
            ApprovalGrant(
                grant_id=row['grant_id'],
                request_id=row['request_id'],
                operation=row['operation'],
                scope=json.loads(row['scope']),
                expires_at=row['expires_at'],
                granted_at=row['created_at']
            )
            for row in rows
        ]


def get_approval_store():
    """Get approval store (SQLite if env var set, else in-memory)"""
    db_path = os.environ.get('APPROVAL_STORE_DB')
    
    if db_path:
        return SQLiteApprovalStore(db_path=db_path)
    else:
        # Fallback to in-memory store
        from ajson.hands.approval import ApprovalStore
        return ApprovalStore()
