
from typing import Optional, List
import sqlite3
import os
import re

class NetworkDeniedError(Exception):
    """Raised when a network connection is denied by the allowlist."""
    pass

class Allowlist:
    """
    Network allowlist using SQLite for persistence.
    """
    def __init__(self, db_path: str = "data/approvals.db"):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        # Table creation is handled in approval_sqlite.py (shared DB),
        # but we ensure it exists here too for standalone usage.
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        with sqlite3.connect(self.db_path) as conn:
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

    def is_allowed(self, host: str, port: int) -> bool:
        """Check if host:port is allowed."""
        # Hardcoded safety fallback (e.g. localhost)
        if host in ["localhost", "127.0.0.1"]:
            return True

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT host_pattern, port FROM allowlist_rules")
            rules = cursor.fetchall()

        for rule in rules:
            if self._matches(host, port, rule['host_pattern'], rule['port']):
                return True
        
        return False

    def check(self, host: str, port: int):
        """Raise NetworkDeniedError if not allowed."""
        if not self.is_allowed(host, port):
            raise NetworkDeniedError(f"Connection to {host}:{port} denied by Allowlist.")

    def _matches(self, host: str, port: int, pattern: str, allowed_port: int) -> bool:
        if port != allowed_port and allowed_port != 0: # 0 means any port
            return False
        
        # Simple glob matching
        if pattern == "*":
            return True
        if pattern.startswith("*."):
            suffix = pattern[1:]
            return host.endswith(suffix)
        return host == pattern

    def add_rule(self, host_pattern: str, port: int, reason: str):
        """Add a rule to the allowlist."""
        import uuid
        from ajson.utils.time import get_utc_iso
        
        rule_id = str(uuid.uuid4())
        created_at = get_utc_iso()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO allowlist_rules (rule_id, host_pattern, port, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                (rule_id, host_pattern, port, reason, created_at)
            )
            conn.commit()
