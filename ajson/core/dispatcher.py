from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import random

@dataclass
class WorkItem:
    id: str
    objective: str
    constraints: List[str]
    required_evidence: List[str]
    skill_tags: List[str]
    assigned_agent_id: Optional[str] = None
    status: str = "PENDING"
    result: Optional[Any] = None
    excluded_agent_ids: List[str] = field(default_factory=list)

class TaskGraph:
    def __init__(self):
        self.nodes: List[WorkItem] = []

    def add_node(self, node: WorkItem):
        self.nodes.append(node)

class Dispatcher:
    def __init__(self):
        pass

    def dispatch(self, graph: TaskGraph, registry: Any) -> Dict[str, str]:
        """
        Assigns agents to pending work items.
        Returns a mapping of work_item_id -> agent_id
        """
        # Initialize with None to avoid KeyError (Strategy A)
        assignments = {n.id: None for n in graph.nodes if n.status == "PENDING"}
        pending_items = [n for n in graph.nodes if n.status == "PENDING"]
        
        # Capability Match Strategy (Simple)
        for item in pending_items:
            # Find capable agents
            candidates = []
            for agent in registry.list_agents(enabled_only=True):
                # Failover check: skip if excluded
                if agent.id in item.excluded_agent_ids:
                    continue
                
                if agent.status == "IDLE":
                    # Check if agent has at least one matching skill? Or strict match?
                    # Start simplistic: if exact match or agent has 'all' capability
                    match_score = 0
                    for skill in item.skill_tags:
                        if skill in agent.capabilities:
                            match_score += 2 # Specific match
                        elif "general" in agent.capabilities:
                            match_score += 1 # General fallback
                    
                    if match_score > 0:
                        candidates.append((agent.id, match_score))
            
            # Load Balance: Randomize before sort to break ties fairly
            random.shuffle(candidates)
            
            # Sort by match score descent
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            if candidates:
                best_agent_id = candidates[0][0]
                # Acquire agent (mark busy)
                # FIX: acquire_agents(1) grabs ANY agent, potentially wrong one.
                # Since we identified IDLE agent in candidates, just mark it BUSY.
                # if registry.acquire_agents(1): <- REMOVED (Buggy)
                registry._agents[best_agent_id].status = "BUSY" 
                item.assigned_agent_id = best_agent_id
                item.status = "ASSIGNED"
                assignments[item.id] = best_agent_id
        
        return assignments
