import pytest
from ajson.core.dispatcher import Dispatcher, TaskGraph, WorkItem
from ajson.core.registry import AgentRegistry

@pytest.fixture
def mock_registry():
    registry = AgentRegistry()
    # Agent A: General
    registry.register_agent(
        id="agent-a", provider="mock", model="model-a", key_ref="key-a",
        capabilities=["general"], enabled=True
    )
    # Agent B: Coding
    registry.register_agent(
        id="agent-b", provider="mock", model="model-b", key_ref="key-b",
        capabilities=["coding"], enabled=True
    )
    # Agent C: General
    registry.register_agent(
        id="agent-c", provider="mock", model="model-c", key_ref="key-c",
        capabilities=["general"], enabled=True
    )
    return registry

def test_capability_match(mock_registry):
    dispatcher = Dispatcher()
    graph = TaskGraph()
    item = WorkItem(
        id="task-1", objective="Code something", constraints=[],
        required_evidence=[], skill_tags=["coding"]
    )
    graph.add_node(item)
    
    assignments = dispatcher.dispatch(graph, mock_registry)
    
    # Needs Agent B (coding)
    assert assignments["task-1"] == "agent-b"
    assert item.status == "ASSIGNED"
    assert mock_registry.get_agent("agent-b").status == "BUSY"

def test_load_balance_random(mock_registry):
    # Check that dispatch distributes between A and C for general task
    counts = {"agent-a": 0, "agent-c": 0}
    
    for _ in range(50):
        # Reset registry status to IDLE for next iteration
        mock_registry.release_agents(["agent-a", "agent-c"])
        
        dispatcher = Dispatcher()
        graph = TaskGraph()
        item = WorkItem(
            id="task-2", objective="Chat", constraints=[],
            required_evidence=[], skill_tags=["general"]
        )
        graph.add_node(item)
        
        assignments = dispatcher.dispatch(graph, mock_registry)
        assigned = assignments.get("task-2")
        if assigned in counts:
            counts[assigned] += 1
            
    # With 50 tries, it is extremely statistically unlikely to verify 0 on either if logic works
    assert counts["agent-a"] > 0
    assert counts["agent-c"] > 0

def test_failover(mock_registry):
    dispatcher = Dispatcher()
    graph = TaskGraph()
    item = WorkItem(
        id="task-3", objective="Chat", constraints=[],
        required_evidence=[], skill_tags=["general"]
    )
    graph.add_node(item)
    
    # First dispatch - gets A or C
    assignments = dispatcher.dispatch(graph, mock_registry)
    first_agent = assignments["task-3"]
    assert first_agent in ["agent-a", "agent-c"]
    
    # Simulate failure: release agent (back to idle), but exclude it from item
    mock_registry.release_agents([first_agent])
    item.status = "PENDING" # Reset status to pending to retry
    item.excluded_agent_ids.append(first_agent)
    
    # Second dispatch
    assignments_retry = dispatcher.dispatch(graph, mock_registry)
    second_agent = assignments_retry["task-3"]
    
    # Should pick the OTHER general agent
    assert second_agent != first_agent
    assert second_agent in ["agent-a", "agent-c"]
