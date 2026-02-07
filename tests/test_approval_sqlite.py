"""
Tests for SQLite-backed approval store
"""
import pytest
import tempfile
import os
from ajson.hands.approval_sqlite import SQLiteApprovalStore
from ajson.hands.approval import ApprovalDecision


def test_sqlite_store_initialization():
    """SQLite store creates database and tables"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        store = SQLiteApprovalStore(db_path=db_path)
        
        assert os.path.exists(db_path)


def test_create_and_get_pending():
    """Create request and retrieve pending"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SQLiteApprovalStore(db_path=os.path.join(tmpdir, "test.db"))
        
        request = store.create_request("ls -la", "readonly", "test")
        
        assert request.request_id is not None
        assert request.status == "pending"
        
        pending = store.get_pending()
        assert len(pending) == 1
        assert pending[0].request_id == request.request_id


def test_approve_request_creates_grant():
    """Approving request creates active grant"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SQLiteApprovalStore(db_path=os.path.join(tmpdir, "test.db"))
        
        request = store.create_request("ls -la", "readonly", "test")
        
        decision = ApprovalDecision(
            request_id=request.request_id,
            decision="approve",
            reason="Test",
            scope=["ls"]
        )
        
        grant = store.approve_request(request.request_id, decision)
        
        assert grant.grant_id is not None
        assert grant.request_id == request.request_id
        assert grant.scope == ["ls"]
        
        # Request should no longer be pending
        pending = store.get_pending()
        assert len(pending) == 0
        
        # Grant should be active
        grants = store.get_active_grants()
        assert len(grants) == 1
        assert grants[0].grant_id == grant.grant_id


def test_deny_request():
    """Denying request updates status"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SQLiteApprovalStore(db_path=os.path.join(tmpdir, "test.db"))
        
        request = store.create_request("rm -rf /", "destructive", "test")
        
        store.deny_request(request.request_id, "Too dangerous")
        
        # Should no longer be pending
        pending = store.get_pending()
        assert len(pending) == 0


def test_verify_grant_scope():
    """Grant verification checks scope"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = SQLiteApprovalStore(db_path=os.path.join(tmpdir, "test.db"))
        
        request = store.create_request("ls -la", "readonly", "test")
        
        decision = ApprovalDecision(
            request_id=request.request_id,
            decision="approve",
            reason="Test",
            scope=["ls", "git"]
        )
        
        grant = store.approve_request(request.request_id, decision)
        
        # In scope
        assert store.verify_grant(grant.grant_id, "ls -la")
        assert store.verify_grant(grant.grant_id, "git status")
        
        # Out of scope
        assert not store.verify_grant(grant.grant_id, "rm -rf /")


def test_persistence_across_instances():
    """Data persists across store instances"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        
        # Create request with first instance
        store1 = SQLiteApprovalStore(db_path=db_path)
        request = store1.create_request("ls", "readonly", "test")
        request_id = request.request_id
        
        # Verify with second instance
        store2 = SQLiteApprovalStore(db_path=db_path)
        pending = store2.get_pending()
        
        assert len(pending) == 1
        assert pending[0].request_id == request_id


def test_env_var_activation():
    """get_approval_store respects APPROVAL_STORE_DB env var"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        
        # Set env var
        os.environ['APPROVAL_STORE_DB'] = db_path
        
        try:
            from ajson.hands.approval_sqlite import get_approval_store
            store = get_approval_store()
            
            # Check it's SQLite store by verifying db_path attribute exists
            assert hasattr(store, 'db_path')
            assert store.db_path == db_path
        finally:
            del os.environ['APPROVAL_STORE_DB']



def test_fallback_to_in_memory():
    """get_approval_store falls back to in-memory store"""
    # Ensure env var is not set
    os.environ.pop('APPROVAL_STORE_DB', None)
    
    from ajson.hands.approval_sqlite import get_approval_store
    from ajson.hands.approval import ApprovalStore
    
    store = get_approval_store()
    
    assert isinstance(store, ApprovalStore)
