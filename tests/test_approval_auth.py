"""
Tests for approval endpoint authentication
"""
import pytest
import os
from fastapi.testclient import TestClient
from ajson.app import app
from ajson.hands.approval import get_approval_store


client = TestClient(app)


def test_approval_no_auth_required_when_token_not_set():
    """Approval endpoints work without auth when AJSON_APPROVAL_TOKEN not set"""
    # Ensure env var is not set
    os.environ.pop('AJSON_APPROVAL_TOKEN', None)
    
    # Should work without authorization header
    response = client.get("/api/approvals/pending")
    assert response.status_code == 200


def test_approval_auth_required_when_token_set():
    """Approval POST endpoints require auth when AJSON_APPROVAL_TOKEN is set"""
    # Set token
    test_token = "test-secret-token-12345"
    os.environ['AJSON_APPROVAL_TOKEN'] = test_token
    
    try:
        # Create a request first (GET doesn't require auth)
        store = get_approval_store()
        request = store.create_request("ls", "readonly", "test")
        
        # POST without auth should fail
        response = client.post(
            f"/api/approvals/{request.request_id}/approve",
            json={
                "decision": "approve",
                "reason": "test",
                "scope": ["ls"]
            }
        )
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]
    finally:
        del os.environ['AJSON_APPROVAL_TOKEN']


def test_approval_auth_succeeds_with_valid_token():
    """Approval POST endpoints work with valid token"""
    test_token = "test-secret-token-12345"
    os.environ['AJSON_APPROVAL_TOKEN'] = test_token
    
    try:
        # Create a request
        store = get_approval_store()
        request = store.create_request("ls", "readonly", "test")
        
        # POST with valid token should succeed
        response = client.post(
            f"/api/approvals/{request.request_id}/approve",
            json={
                "decision": "approve",
                "reason": "test",
                "scope": ["ls"]
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        assert "grant_id" in response.json()
    finally:
        del os.environ['AJSON_APPROVAL_TOKEN']


def test_approval_auth_fails_with_invalid_token():
    """Approval POST endpoints reject invalid token"""
    test_token = "test-secret-token-12345"
    os.environ['AJSON_APPROVAL_TOKEN'] = test_token
    
    try:
        store = get_approval_store()
        request = store.create_request("ls", "readonly", "test")
        
        # POST with wrong token should fail
        response = client.post(
            f"/api/approvals/{request.request_id}/approve",
            json={
                "decision": "approve",
                "reason": "test",
                "scope": ["ls"]
            },
            headers={"Authorization": "Bearer wrong-token"}
        )
        assert response.status_code == 403
        assert "Invalid authentication" in response.json()["detail"]
    finally:
        del os.environ['AJSON_APPROVAL_TOKEN']


def test_deny_endpoint_requires_auth():
    """Deny endpoint also requires auth when token is set"""
    test_token = "test-secret-token-12345"
    os.environ['AJSON_APPROVAL_TOKEN'] = test_token
    
    try:
        store = get_approval_store()
        request = store.create_request("rm -rf /", "destructive", "test")
        
        # Without auth
        response = client.post(
            f"/api/approvals/{request.request_id}/deny",
            json={"decision": "deny", "reason": "too risky"}
        )
        assert response.status_code == 401
        
        # With valid auth
        response = client.post(
            f"/api/approvals/{request.request_id}/deny",
            json={"decision": "deny", "reason": "too risky"},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
    finally:
        del os.environ['AJSON_APPROVAL_TOKEN']


def test_get_endpoints_no_auth_required():
    """GET endpoints don't require auth even when token is set"""
    test_token = "test-secret-token-12345"
    os.environ['AJSON_APPROVAL_TOKEN'] = test_token
    
    try:
        # GET endpoints should work without auth
        response = client.get("/api/approvals/pending")
        assert response.status_code == 200
        
        response = client.get("/api/approvals/grants/active")
        assert response.status_code == 200
    finally:
        del os.environ['AJSON_APPROVAL_TOKEN']
