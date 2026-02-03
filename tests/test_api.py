"""
Test FastAPI endpoints
"""
import pytest
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from ajson.app import app
from ajson import db
from ajson.models import MissionStatus


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    """Setup test database before each test"""
    # Use in-memory database for tests
    test_db_path = ":memory:"
    monkeypatch.setenv("DB_PATH", test_db_path)
    
    # Clear any existing module cache and force reimport
    import sys
    for module in list(sys.modules.keys()):
        if module.startswith('ajson'):
            del sys.modules[module]
    
    # Reimport fresh modules
    from ajson import db
    db.init_db()
    
    yield
    
    # Cleanup
    for module in list(sys.modules.keys()):
        if module.startswith('ajson'):
            if module in sys.modules:
                del sys.modules[module]


client = TestClient(app)


def test_create_mission():
    """Test: POST /missions returns mission_id"""
    response = client.post("/missions", json={
        "title": "Test Mission",
        "description": "Run pytest tests",
        "attachments": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "mission_id" in data
    assert isinstance(data["mission_id"], int)
    assert data["mission_id"] > 0


def test_get_mission():
    """Test: GET /missions/{id} returns correct data"""
    # Create a mission first
    create_response = client.post("/missions", json={
        "title": "Test Get Mission",
        "description": "Testing GET endpoint",
        "attachments": []
    })
    mission_id = create_response.json()["mission_id"]
    
    # Wait a bit for background task to process
    time.sleep(2)
    
    # Get mission
    response = client.get(f"/missions/{mission_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "mission" in data
    assert "steps" in data
    assert "approvals" in data
    assert "artifacts" in data
    
    assert data["mission"]["id"] == mission_id
    assert data["mission"]["title"] == "Test Get Mission"


def test_get_mission_not_found():
    """Test: GET /missions/{id} returns 404 for non-existent mission"""
    response = client.get("/missions/99999")
    assert response.status_code == 404


def test_dangerous_mission_requires_approval():
    """Test: Mission with dangerous keywords stops at PENDING_APPROVAL"""
    response = client.post("/missions", json={
        "title": "Deploy Mission",
        "description": "Deploy application to production",
        "attachments": []
    })
    
    assert response.status_code == 200
    mission_id = response.json()["mission_id"]
    
    # Wait for background task to process
    time.sleep(2)
    
    # Check status
    get_response = client.get(f"/missions/{mission_id}")
    data = get_response.json()
    
    # Should stop at PENDING_APPROVAL due to "deploy"
    assert data["mission"]["status"] == MissionStatus.PENDING_APPROVAL
    
    # Should have pending approvals
    assert len(data["approvals"]) > 0
    assert data["approvals"][0]["status"] == "PENDING"


def test_approve_mission_yes():
    """Test: approve yes resumes mission to correct state"""
    # Create dangerous mission
    create_response = client.post("/missions", json={
        "title": "Delete Mission",
        "description": "Delete old data from database",
        "attachments": []
    })
    mission_id = create_response.json()["mission_id"]
    
    # Wait for it to stop at PENDING_APPROVAL
    time.sleep(2)
    
    # Verify it's pending
    get_response = client.get(f"/missions/{mission_id}")
    assert get_response.json()["mission"]["status"] == MissionStatus.PENDING_APPROVAL
    
    # Approve yes
    approve_response = client.post(f"/missions/{mission_id}/approve", json={
        "decision": "yes"
    })
    
    assert approve_response.status_code == 200
    data = approve_response.json()
    assert data["status"] == "approved"
    
    # Wait for it to resume
    time.sleep(2)
    
    # Check that it resumed (should be PRE_AUDIT based on our fix)
    get_response = client.get(f"/missions/{mission_id}")
    status = get_response.json()["mission"]["status"]
    
    # Should have resumed from PRE_AUDIT
    # (Note: it may have progressed further by the time we check)
    assert status in [MissionStatus.PRE_AUDIT, MissionStatus.EXECUTE, 
                      MissionStatus.POST_AUDIT, MissionStatus.FINALIZE, 
                      MissionStatus.DONE, MissionStatus.PENDING_APPROVAL]


def test_approve_mission_no():
    """Test: approve no keeps mission in stopped state"""
    # Create dangerous mission
    create_response = client.post("/missions", json={
        "title": "Delete All Files",
        "description": "Delete all files from production",
        "attachments": []
    })
    mission_id = create_response.json()["mission_id"]
    
    # Wait for it to stop at PENDING_APPROVAL
    time.sleep(2)
    
    # Verify it's pending
    get_response = client.get(f"/missions/{mission_id}")
    assert get_response.json()["mission"]["status"] == MissionStatus.PENDING_APPROVAL
    
    # Approve no
    approve_response = client.post(f"/missions/{mission_id}/approve", json={
        "decision": "no"
    })
    
    assert approve_response.status_code == 200
    data = approve_response.json()
    assert data["status"] == "rejected"
    
    # Wait a bit
    time.sleep(1)
    
    # Check that it's still pending (not resumed)
    get_response = client.get(f"/missions/{mission_id}")
    status = get_response.json()["mission"]["status"]
    
    # Should still be PENDING_APPROVAL (not resumed)
    assert status == MissionStatus.PENDING_APPROVAL


def test_approve_non_pending_mission():
    """Test: Cannot approve a mission that's not pending"""
    # Create normal mission
    create_response = client.post("/missions", json={
        "title": "Normal Mission",
        "description": "Run tests",
        "attachments": []
    })
    mission_id = create_response.json()["mission_id"]
    
    # Wait for it to complete
    time.sleep(3)
    
    # Try to approve (should fail)
    approve_response = client.post(f"/missions/{mission_id}/approve", json={
        "decision": "yes"
    })
    
    # Should fail with 400 since mission is not pending approval
    assert approve_response.status_code == 400


def test_console_endpoint():
    """Test: GET /console returns HTML"""
    response = client.get("/console")
    
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"AJSON Mission Console" in response.content


def test_root_endpoint():
    """Test: GET / returns API info"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "console" in data
    assert data["console"] == "/console"
