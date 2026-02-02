"""
Test state machine transitions
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ajson import db, orchestrator
from ajson.models import MissionStatus


@pytest.fixture(autouse=True)
def setup_db(monkeypatch):
    """Setup test database before each test"""
    # Use in-memory database for tests
    test_db_path = ":memory:"
    monkeypatch.setenv("DB_PATH", test_db_path)
    
    # Clear any existing module cache and force reimport
    import sys
    if 'ajson.db' in sys.modules:
        del sys.modules['ajson.db']
    if 'ajson.orchestrator' in sys.modules:
        del sys.modules['ajson.orchestrator']
    if 'ajson.roles.jarvis' in sys.modules:
        del sys.modules['ajson.roles.jarvis']
    if 'ajson.roles.cody' in sys.modules:
        del sys.modules['ajson.roles.cody']
    
    # Reimport fresh modules
    from ajson import db
    db.init_db()
    
    yield
    
    # Cleanup
    if 'ajson.db' in sys.modules:
        del sys.modules['ajson.db']


def test_mission_full_lifecycle():
    """Test: Mission transitions from CREATED to DONE"""
    # Create mission
    mission_id = db.create_mission(
        title="Test Mission",
        description="Run pytest tests"
    )
    
    # Verify initial state
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.CREATED
    
    # Execute through all states
    orchestrator.execute_mission(mission_id)  # CREATED → PLANNED
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.PLANNED
    
    orchestrator.execute_mission(mission_id)  # PLANNED → PRE_AUDIT
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.PRE_AUDIT
    
    orchestrator.execute_mission(mission_id)  # PRE_AUDIT → EXECUTE
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.EXECUTE
    
    orchestrator.execute_mission(mission_id)  # EXECUTE → POST_AUDIT
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.POST_AUDIT
    
    orchestrator.execute_mission(mission_id)  # POST_AUDIT → FINALIZE
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.FINALIZE
    
    orchestrator.execute_mission(mission_id)  # FINALIZE → DONE
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.DONE
    
    # Verify steps were created
    steps = db.get_steps_by_mission(mission_id)
    assert len(steps) > 0
    
    # Verify artifacts were created
    artifacts = db.get_artifacts_by_mission(mission_id)
    assert len(artifacts) > 0


def test_approval_gate_detection():
    """Test: Mission stops at PENDING_APPROVAL when dangerous operation detected"""
    # Create mission with dangerous keyword
    mission_id = db.create_mission(
        title="Deploy Mission",
        description="Deploy application to production"
    )
    
    # Transition to PLANNED
    orchestrator.execute_mission(mission_id)
    assert db.get_mission(mission_id)["status"] == MissionStatus.PLANNED
    
    # Should stop at PENDING_APPROVAL due to "deploy"
    orchestrator.execute_mission(mission_id)
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.PENDING_APPROVAL
    
    # Verify approval was created
    approvals = db.get_pending_approvals(mission_id)
    assert len(approvals) > 0
    assert approvals[0]["status"] == "PENDING"


def test_approval_and_resume():
    """Test: Mission can be approved and resumed"""
    # Create mission with dangerous keyword
    mission_id = db.create_mission(
        title="Delete Mission",
        description="Delete old data from database"
    )
    
    # Execute to PENDING_APPROVAL
    orchestrator.execute_mission(mission_id)  # → PLANNED
    orchestrator.execute_mission(mission_id)  # → PENDING_APPROVAL
    
    assert db.get_mission(mission_id)["status"] == MissionStatus.PENDING_APPROVAL
    
    # Approve and resume
    orchestrator.approve_mission(mission_id)
    
    # Should move to next state
    mission = db.get_mission(mission_id)
    assert mission["status"] == MissionStatus.EXECUTE


def test_ssot_tracking():
    """Test: All operations are tracked in SSOT"""
    mission_id = db.create_mission(
        title="SSOT Test",
        description="Test SSOT tracking"
    )
    
    # Execute one transition
    orchestrator.execute_mission(mission_id)
    
    # Verify mission exists
    mission = db.get_mission(mission_id)
    assert mission is not None
    assert mission["id"] == mission_id
    
    # Verify step was recorded
    steps = db.get_steps_by_mission(mission_id)
    assert len(steps) == 1
    assert steps[0]["mission_id"] == mission_id
    
    # Execute more transitions
    orchestrator.execute_mission(mission_id)  # PRE_AUDIT
    orchestrator.execute_mission(mission_id)  # EXECUTE
    
    # Verify tool runs were recorded
    tool_runs = db.get_tool_runs_by_mission(mission_id)
    assert len(tool_runs) > 0
    
    # Complete mission
    while db.get_mission(mission_id)["status"] != MissionStatus.DONE:
        orchestrator.execute_mission(mission_id)
    
    # Verify final artifacts
    artifacts = db.get_artifacts_by_mission(mission_id)
    assert len(artifacts) >= 2  # plan + final report
