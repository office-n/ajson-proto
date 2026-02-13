from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ApprovalRequest:
    """Approval request for a gated operation"""
    request_id: str
    operation: str
    category: str
    reason: str
    status: str
    metadata: Dict[str, Any]
    created_at: str  # ISO 8601 timestamp (standardized from requested_at)
    requested_by: str = "system"
    
    @property
    def requested_at(self) -> str:
        """Alias for created_at for backward compatibility"""
        return self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ApprovalDecision:
    """Approval decision (approve or deny)"""
    request_id: str
    decision: str  # "approve" or "deny"
    reason: str
    decided_by: str = "admin"
    decided_at: str = ""
    scope: List[str] = field(default_factory=list)
    ttl_seconds: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ApprovalGrant:
    """Approved permission grant"""
    grant_id: str
    request_id: str
    operation: str
    scope: List[str]
    granted_at: str
    expires_at: str
    granted_by: str = "admin"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def is_expired(self) -> bool:
        """Check if grant has expired"""
        from datetime import datetime
        now = datetime.now()
        expires = datetime.fromisoformat(self.expires_at)
        return now > expires
    
    def matches_scope(self, operation: str) -> bool:
        """Check if operation matches grant scope"""
        if not self.scope:
            return True  # Empty scope = matches original operation only
        for pattern in self.scope:
            if pattern.lower() in operation.lower():
                return True
        return False
