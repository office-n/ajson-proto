# tests/test_orchestrator_dry_run.py
import pytest
import os
import json
from ajson.core.orchestrator import Orchestrator

# Mock Config
MOCK_CONFIG = {
    "subagents": [
        {
            "id": "gemini-1",
            "provider": "gemini",
            "key_ref": "ENV:GEMINI_API_KEY",
            "capabilities": ["general"],
            "enabled": True
        }
    ]
}

@pytest.fixture
def mock_config_file(tmp_path):
    config_file = tmp_path / "subagents.json"
    config_file.write_text(json.dumps(MOCK_CONFIG))
    return str(config_file)

def test_orchestrator_dry_run(mock_config_file):
    """
    Verifies that the Orchestrator can load config, dispatch a task, and return a result
    without making actual API calls.
    """
    # Initialize
    orc = Orchestrator(mock_config_file)
    
    # Verify Registry Loaded
    agents = orc.registry.list_agents()
    assert len(agents) == 1
    assert agents[0].id == "gemini-1"
    
    # Process Request
    response = orc.process_request("Hello World")
    
    # Verify Output
    assert response["status"] == "success"
    assert len(response["items"]) == 1
    assert "Processed 'Hello World' by gemini-1" in response["items"][0]
    
    # Verify Trace
    assert len(orc.trace.records) >= 4 # receive, decompose, dispatch, execute, aggregate
    assert orc.trace.records[0]["type"] == "request_received"

if __name__ == "__main__":
    pytest.main([__file__])
