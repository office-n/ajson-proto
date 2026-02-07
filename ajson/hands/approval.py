"""
Approval Queue: Manages approval requests for gated operations

Provides:
- ApprovalRequest: Represents a pending approval request
- ApprovalDecision: Approve/Deny with reason
- ApprovalGrant: Approved permission with scope/expiry
- ApprovalStore: In-memory storage for requests/grants
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Approval request for a gated operation"""
    request_id: str
    operation: str
    category: str  # OperationCategory value
    reason: str  # Why approval is needed
    requested_at: str  # ISO 8601 timestamp
    requested_by: str = "system"  # Future: user ID
    status: str = ApprovalStatus.PENDING.value
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return asdict(self)


@dataclass
class ApprovalDecision:
    """Approval decision (approve or deny)"""
    request_id: str
    decision: str  # "approve" or "deny"
    reason: str
    decided_by: str = "admin"  # Future: user ID
    decided_at: str = ""  # ISO 8601 timestamp
    scope: List[str] = field(default_factory=list)  # For approve: allowed operations
    ttl_seconds: int = 300  # Time to live for grant (default 5 min)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return asdict(self)


@dataclass
class ApprovalGrant:
    """Approved permission grant"""
    grant_id: str
    request_id: str
    operation: str
    scope: List[str]  # Allowed operations
    granted_at: str  # ISO 8601 timestamp
    expires_at: str  # ISO 8601 timestamp
    granted_by: str = "admin"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return asdict(self)
    
    def is_expired(self) -> bool:
        """Check if grant has expired"""
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


class ApprovalStore:
    """
    In-memory store for approval requests and grants
    
    Future: Replace with persistent storage (SQLite/Redis)
    """
    
    def __init__(self):
        self.requests: Dict[str, ApprovalRequest] = {}
        self.grants: Dict[str, ApprovalGrant] = {}
    
    def create_request(self, operation: str, category: str, reason: str, metadata: Optional[Dict[str, Any]] = None) -> ApprovalRequest:
        """Create a new approval request"""
        request_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        request = ApprovalRequest(
            request_id=request_id,
            operation=operation,
            category=category,
            reason=reason,
            requested_at=now,
            metadata=metadata or {}
        )
        
        self.requests[request_id] = request
        return request
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID"""
        return self.requests.get(request_id)
    
    def list_pending_requests(self) -> List[ApprovalRequest]:
        """List all pending approval requests"""
        return [r for r in self.requests.values() if r.status == ApprovalStatus.PENDING.value]
    
    def approve_request(self, request_id: str, decision: ApprovalDecision) -> Optional[ApprovalGrant]:
        """Approve a request and create grant"""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING.value:
            return None
        
        # Update request status
        request.status = ApprovalStatus.APPROVED.value
        
        # Create grant
        grant_id = str(uuid.uuid4())
        now = datetime.now()
        expires = now + timedelta(seconds=decision.ttl_seconds)
        
        grant = ApprovalGrant(
            grant_id=grant_id,
            request_id=request_id,
            operation=request.operation,
            scope=decision.scope or [request.operation],
            granted_at=now.isoformat(),
            expires_at=expires.isoformat(),
            granted_by=decision.decided_by,
            metadata=request.metadata
        )
        
        self.grants[grant_id] = grant
        return grant
    
    def deny_request(self, request_id: str, decision: ApprovalDecision) -> bool:
        """Deny a request"""
        request = self.requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING.value:
            return False
        
        request.status = ApprovalStatus.DENIED.value
        request.metadata["denial_reason"] = decision.reason
        request.metadata["denied_by"] = decision.decided_by
        request.metadata["denied_at"] = datetime.now().isoformat()
        return True
    
    def get_grant(self, grant_id: str) -> Optional[ApprovalGrant]:
        """Get grant by ID"""
        grant = self.grants.get(grant_id)
        if grant and grant.is_expired():
            return None  # Expired grants are not returned
        return grant
    
    def list_active_grants(self) -> List[ApprovalGrant]:
        """List all active (non-expired) grants"""
        now = datetime.now()
        return [g for g in self.grants.values() if not g.is_expired()]
    
    def verify_grant(self, grant_id: str, operation: str) -> bool:
        """Verify grant is valid for operation"""
        grant = self.get_grant(grant_id)
        if not grant:
            return False
        return grant.matches_scope(operation)


# Global singleton instance (for now)
_global_store = ApprovalStore()


def get_approval_store() -> ApprovalStore:
    """Get global approval store instance"""
    return _global_store
