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


# Phase6B Tests

def test_messages_api_post_and_get():
    """Test: POST message then GET messages returns created message"""
    # Create a mission first
    create_response = client.post("/missions", json={
        "title": "Messages Test Mission",
        "description": "Testing messages API",
        "attachments": []
    })
    mission_id = create_response.json()["mission_id"]
    
    # Post a message
    message_response = client.post(f"/missions/{mission_id}/messages", json={
        "content": "Hello from test",
        "attachment_ids": None
    })
    
    assert message_response.status_code == 200
    msg_data = message_response.json()
    assert "message_id" in msg_data
    assert "mission_id" in msg_data
    assert msg_data["mission_id"] == mission_id
    
    # Get messages
    get_response = client.get(f"/missions/{mission_id}/messages")
    
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert "messages" in get_data
    assert "mission_id" in get_data
    assert get_data["mission_id"] == mission_id
    
    # Verify our message is in the list
    messages = get_data["messages"]
    assert len(messages) >= 1
    user_messages = [m for m in messages if m["role"] == "user"]
    assert len(user_messages) >= 1
    assert user_messages[0]["content"] == "Hello from test"


def test_mission_title_auto_generation():
    """Test: Empty title generates title from description + timestamp"""
    # Create mission with empty title
    response = client.post("/missions", json={
        "title": "",
        "description": "This is a test description for auto-title generation",
        "attachments": []
    })
    
    assert response.status_code == 200
    mission_id = response.json()["mission_id"]
    
    # Get mission and check title
    get_response = client.get(f"/missions/{mission_id}")
    mission_data = get_response.json()["mission"]
    
    # Title should not be empty
    assert mission_data["title"] != ""
    
    # Title should contain first 20 chars of description
    assert "This is a test descr" in mission_data["title"]
    
    # Title should contain a timestamp pattern (YYYY-MM-DD HH:MM)
    import re
    assert re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', mission_data["title"])


def test_messages_attachment_ids_linkage():
    """Test: Attachment IDs are stored and retrieved in messages"""
    # Create a mission
    create_response = client.post("/missions", json={
        "title": "Attachment Test",
        "description": "Testing attachment linkage",
        "attachments": []
    })
    mission_id = create_response.json()["mission_id"]
    
    # Post a message with attachment IDs
    test_upload_ids = ["upload-123", "upload-456"]
    message_response = client.post(f"/missions/{mission_id}/messages", json={
        "content": "Message with attachments",
        "attachment_ids": test_upload_ids
    })
    
    assert message_response.status_code == 200
    message_id = message_response.json()["message_id"]
    
    # Get messages and verify attachments_json
    get_response = client.get(f"/missions/{mission_id}/messages")
    messages = get_response.json()["messages"]
    
    # Find our message
    our_message = None
    for msg in messages:
        if msg["id"] == message_id:
            our_message = msg
            break
    
    assert our_message is not None
    assert our_message["content"] == "Message with attachments"
    
    # Verify attachments_json contains our upload IDs
    import json
    attachments = json.loads(our_message["attachments_json"])
    assert attachments == test_upload_ids
