from typing import Any, Dict, List
from ajson.core.registry import AgentRegistry
from ajson.core.dispatcher import Dispatcher, TaskGraph, WorkItem
from ajson.core.aggregator import Aggregator
from ajson.core.trace import Trace
from ajson.core.policy import Policy

class Orchestrator:
    """
    The main coordinator for AJSON agents and tools (Fleet Commander).
    """
    def __init__(self, config_path: str = None):
        self.registry = AgentRegistry(config_path)
        self.dispatcher = Dispatcher()
        self.aggregator = Aggregator()
        self.trace = Trace()

    def register_agent(self, name: str, agent: Any):
        # Legacy support or direct registration
        pass

    def register_tool(self, name: str, tool: Any):
        # Legacy/Global tool registration
        pass

    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Processes a user request using the Fleet.
        """
        self.trace.log("request_received", {"request": request})

        # 1. Decompose (Stub: Single item for now)
        graph = TaskGraph()
        item = WorkItem(
            id="task-1",
            objective=request,
            constraints=[],
            required_evidence=[],
            skill_tags=["general"]
        )
        graph.add_node(item)
        self.trace.log("task_decomposed", {"items": [item.id]})

        # 2. Dispatch
        assignments = self.dispatcher.dispatch(graph, self.registry)
        self.trace.log("task_dispatched", assignments)

        # 3. Execute (Stub: Sequential)
        results = []
        for task_id, agent_id in assignments.items():
            # In Phase 9.1, we mock execution or use the agent instance if we had one
            # Here we just verify the assignment worked
            result = {
                "task_id": task_id,
                "agent_id": agent_id,
                "output": f"Processed '{request}' by {agent_id}"
            }
            results.append(result)
            self.trace.log("task_executed", result)
            
            # Release agent
            self.registry.release_agents([agent_id])

        # 4. Aggregate
        final_output = self.aggregator.collect(results)
        self.trace.log("result_aggregated", final_output)

        return final_output
