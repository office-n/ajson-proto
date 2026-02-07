"""
API endpoints for approval queue management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from ajson.hands.approval import (
    get_approval_store,
    ApprovalRequest,
    ApprovalDecision as ApprovalDecisionModel,
    ApprovalGrant,
    ApprovalStatus
)

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


# Request/Response models
class ApprovalDecisionRequest(BaseModel):
    """Request to approve or deny"""
    decision: str  # "approve" or "deny"
    reason: str
    decided_by: str = "admin"
    scope: Optional[List[str]] = None  # For approve: operation patterns
    ttl_seconds: int = 300  # Grant TTL


class ApprovalRequestResponse(BaseModel):
    """Approval request response"""
    request_id: str
    operation: str
    category: str
    reason: str
    status: str
    requested_at: str
    metadata: Dict[str, Any] = {}


class ApprovalGrantResponse(BaseModel):
    """Approval grant response"""
    grant_id: str
    request_id: str
    operation: str
    scope: List[str]
    granted_at: str
    expires_at: str
    granted_by: str


@router.get("/pending", response_model=List[ApprovalRequestResponse])
async def list_pending_approvals():
    """List all pending approval requests"""
    store = get_approval_store()
    pending = store.list_pending_requests()
    return [ApprovalRequestResponse(**req.to_dict()) for req in pending]


@router.get("/{request_id}", response_model=ApprovalRequestResponse)
async def get_approval_request(request_id: str):
    """Get single approval request"""
    store = get_approval_store()
    request = store.get_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return ApprovalRequestResponse(**request.to_dict())


@router.post("/{request_id}/approve", response_model=ApprovalGrantResponse)
async def approve_request(request_id: str, decision_req: ApprovalDecisionRequest):
    """Approve an approval request and create grant"""
    if decision_req.decision.lower() != "approve":
        raise HTTPException(status_code=400, detail="Decision must be 'approve'")
    
    store = get_approval_store()
    
    # Create decision
    decision = ApprovalDecisionModel(
        request_id=request_id,
        decision="approve",
        reason=decision_req.reason,
        decided_by=decision_req.decided_by,
        decided_at=datetime.now().isoformat(),
        scope=decision_req.scope or [],
        ttl_seconds=decision_req.ttl_seconds
    )
    
    # Approve and create grant
    grant = store.approve_request(request_id, decision)
    if not grant:
        raise HTTPException(status_code=400, detail="Cannot approve request (not found or not pending)")
    
    return ApprovalGrantResponse(**grant.to_dict())


@router.post("/{request_id}/deny")
async def deny_request(request_id: str, decision_req: ApprovalDecisionRequest):
    """Deny an approval request"""
    if decision_req.decision.lower() != "deny":
        raise HTTPException(status_code=400, detail="Decision must be 'deny'")
    
    store = get_approval_store()
    
    # Create decision
    decision = ApprovalDecisionModel(
        request_id=request_id,
        decision="deny",
        reason=decision_req.reason,
        decided_by=decision_req.decided_by,
        decided_at=datetime.now().isoformat()
    )
    
    # Deny request
    success = store.deny_request(request_id, decision)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot deny request (not found or not pending)")
    
    return {"status": "denied", "request_id": request_id, "reason": decision_req.reason}


@router.get("/grants/active", response_model=List[ApprovalGrantResponse])
async def list_active_grants():
    """List all active (non-expired) grants"""
    store = get_approval_store()
    grants = store.list_active_grants()
    return [ApprovalGrantResponse(**grant.to_dict()) for grant in grants]


@router.get("/grants/{grant_id}", response_model=ApprovalGrantResponse)
async def get_grant(grant_id: str):
    """Get grant by ID (if not expired)"""
    store = get_approval_store()
    grant = store.get_grant(grant_id)
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found or expired")
    return ApprovalGrantResponse(**grant.to_dict())
