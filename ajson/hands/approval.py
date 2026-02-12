"""
Approval Queue: Manages approval requests for gated operations

Provides:
- ApprovalRequest: Represents a pending approval request
- ApprovalDecision: Approve/Deny with reason
- ApprovalGrant: Approved permission with scope/expiry
- ApprovalStore: In-memory storage for requests/grants
"""
from ajson.hands.domain import ApprovalRequest, ApprovalDecision, ApprovalGrant
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


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
        # Use centralized time utility if available, else standard datetime
        try:
            from ajson.utils.time import get_utc_iso
            now_iso = get_utc_iso()
        except ImportError:
             from datetime import timezone
             now_iso = datetime.now(timezone.utc).isoformat()

        request = ApprovalRequest(
            request_id=request_id,
            operation=operation,
            category=category,
            reason=reason,
            created_at=now_iso,  # Standardized field
            status=ApprovalStatus.PENDING.value,
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
