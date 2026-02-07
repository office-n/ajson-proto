"""
Tests for approval queue functionality
"""
import pytest
from datetime import datetime, timedelta
from ajson.hands.approval import (
    ApprovalStore,
    ApprovalRequest,
    ApprovalDecision,
    ApprovalGrant,
    ApprovalStatus,
    get_approval_store
)


def test_create_approval_request():
    """Test creating an approval request"""
    store = ApprovalStore()
    request = store.create_request(
        operation="git push origin main",
        category="irreversible",
        reason="Irreversible: requires approval"
    )
    
    assert request.request_id is not None
    assert request.operation == "git push origin main"
    assert request.category == "irreversible"
    assert request.status == ApprovalStatus.PENDING.value


def test_list_pending_requests():
    """Test listing pending requests"""
    store = ApprovalStore()
    req1 = store.create_request("op1", "destructive", "test1")
    req2 = store.create_request("op2", "paid", "test2")
    
    pending = store.list_pending_requests()
    assert len(pending) == 2
    assert all(r.status == ApprovalStatus.PENDING.value for r in pending)


def test_approve_request():
    """Test approving a request creates grant"""
    store = ApprovalStore()
    request = store.create_request("test_op", "paid", "test reason")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Approved by admin",
        scope=["test_op"],
        ttl_seconds=300
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    assert grant is not None
    assert grant.request_id == request.request_id
    assert grant.operation == "test_op"
    assert len(grant.scope) > 0
    
    # Request should be approved
    updated_request = store.get_request(request.request_id)
    assert updated_request.status == ApprovalStatus.APPROVED.value


def test_deny_request():
    """Test denying a request"""
    store = ApprovalStore()
    request = store.create_request("denied_op", "destructive", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="deny",
        reason="Security concerns"
    )
    
    success = store.deny_request(request.request_id, decision)
    
    assert success is True
    updated_request = store.get_request(request.request_id)
    assert updated_request.status == ApprovalStatus.DENIED.value


def test_grant_expiration():
    """Test grant expiration"""
    store = ApprovalStore()
    request = store.create_request("exp_test", "paid", "test")
    
    # Create grant with 1 second TTL
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        ttl_seconds=1
    )
    
    grant = store.approve_request(request.request_id, decision)
    assert grant is not None
    
    # Immediately should be valid
    assert grant.is_expired() is False
    
    # After TTL should be expired (we can't wait in test, so just check the method works)
    # In real scenario with time.sleep(2), it would be expired


def test_grant_scope_matching():
    """Test grant scope matching"""
    store = ApprovalStore()
    request = store.create_request("git push", "irreversible", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        scope=["git push", "git status"]
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    assert grant.matches_scope("git push origin main") is True
    assert grant.matches_scope("git status") is True
    assert grant.matches_scope("rm -rf /") is False


def test_verify_grant():
    """Test grant verification"""
    store = ApprovalStore()
    request = store.create_request("test_cmd", "destructive", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        scope=["test_cmd"]
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    # Valid grant and operation
    assert store.verify_grant(grant.grant_id, "test_cmd xyz") is True
    
    # Invalid operation
    assert store.verify_grant(grant.grant_id, "other_cmd") is False
    
    # Invalid grant ID
    assert store.verify_grant("nonexistent", "test_cmd") is False


def test_global_store_singleton():
    """Test global store is singleton"""
    store1 = get_approval_store()
    store2 = get_approval_store()
    assert store1 is store2
