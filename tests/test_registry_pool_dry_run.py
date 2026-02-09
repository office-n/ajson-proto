import os
import json
import pytest
from ajson.core.registry import AgentRegistry

@pytest.fixture
def mock_subagents_config(tmp_path):
    config = {
        "subagents": [
            {
                "id": "agent-1",
                "provider": "openai",
                "model": "gpt-4o",
                "key_ref": "ENV:TEST_KEY_1",
                "capabilities": ["reasoning"],
                "enabled": True
            },
            {
                "id": "agent-2",
                "provider": "gemini",
                "model": "gemini-1.5-pro",
                "key_ref": "ENV:TEST_KEY_2",
                "capabilities": ["coding"],
                "enabled": True
            }
        ]
    }
    config_file = tmp_path / "subagents.json"
    with open(config_file, "w") as f:
        json.dump(config, f)
    return str(config_file)

def test_registry_pool_lifecycle(mock_subagents_config, monkeypatch):
    # Setup Env
    monkeypatch.setenv("TEST_KEY_1", "sk-mock-1")
    monkeypatch.setenv("TEST_KEY_2", "AIza-mock-2")

    registry = AgentRegistry()
    registry.load_from_config(mock_subagents_config)

    # 1. Verify Load
    agents = registry.list_agents()
    assert len(agents) == 2
    assert agents[0].model == "gpt-4o"
    assert agents[1].model == "gemini-1.5-pro"

    # 2. Acquire
    acquired = registry.acquire_agents(1)
    assert len(acquired) == 1
    assert registry.get_agent(acquired[0]).status == "BUSY"
    
    # 3. Acquire again (1 left)
    acquired2 = registry.acquire_agents(1)
    assert len(acquired2) == 1
    assert acquired2[0] != acquired[0]

    # 4. Acquire fail (0 left)
    acquired3 = registry.acquire_agents(1)
    assert len(acquired3) == 0

    # 5. Release
    registry.release_agents(acquired)
    assert registry.get_agent(acquired[0]).status == "IDLE"

    # 6. Get API Key
    key = registry.get_api_key("agent-1")
    assert key == "sk-mock-1"

    key2 = registry.get_api_key("agent-2")
    assert key2 == "AIza-mock-2"
