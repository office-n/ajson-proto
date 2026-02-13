import pytest
import os
from ajson.hands.approval_sqlite import SQLiteApprovalStore
from ajson.hands.approval import ApprovalDecision

def test_approval_persistence(tmp_path):
    """Verify that approval data persists across store instances."""
    db_file = tmp_path / "integration_test.db"
    db_path = str(db_file)
    
    # 1. Initialize store and create request
    store1 = SQLiteApprovalStore(db_path=db_path)
    req = store1.create_request(
        operation="connect.integrator",
        category="network",
        reason="Persistence Test"
    )
    req_id = req.request_id
    
    # Verify pending
    pending1 = store1.get_pending()
    assert len(pending1) == 1
    assert pending1[0].request_id == req_id
    
    # 2. Approve request
    store1.approve_request(
        req_id, 
        ApprovalDecision(
            request_id=req_id,
            decision="approve",
            reason="Integration Test",
            scope=["connect.integrator"],
            ttl_seconds=3600
        )
    )  
    # Verify no longer pending
    assert len(store1.get_pending()) == 0
    
    # 3. Re-initialize store (simulate restart)
    store2 = SQLiteApprovalStore(db_path=db_path)
    
    # Verify grants persist
    grants = store2.get_active_grants()
    assert len(grants) >= 1
    persist_grant = next((g for g in grants if g.request_id == req_id), None)
    assert persist_grant is not None
    assert "connect.integrator" in persist_grant.scope

def test_allowlist_persistence(tmp_path):
    """Verify that allowlist rules persist."""
    from ajson.hands.allowlist import Allowlist
    
    db_file = tmp_path / "integration_test.db"
    db_path = str(db_file)
    
    # 1. Add rule
    allowlist1 = Allowlist(db_path=db_path)
    allowlist1.add_rule("persist.example.com", 443, "Persistence Check")
    
    # 2. Check in new instance
    allowlist2 = Allowlist(db_path=db_path)
    assert allowlist2.is_allowed("persist.example.com", 443) is True
    assert allowlist2.is_allowed("other.example.com", 443) is False
