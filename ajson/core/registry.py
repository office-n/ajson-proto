# ajson/core/registry.py
import os
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class AgentInfo:
    id: str
    provider: str
    key_ref: str
    capabilities: List[str]
    enabled: bool = True
    status: str = "IDLE"  # IDLE, BUSY, OFFLINE

class AgentRegistry:
    def __init__(self, config_path: str = None):
        self.agents: Dict[str, AgentInfo] = {}
        if config_path and os.path.exists(config_path):
            self.load_from_config(config_path)
            
    def load_from_config(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                for agent_data in data.get('subagents', []):
                    self.register_agent(
                        id=agent_data['id'],
                        provider=agent_data['provider'],
                        key_ref=agent_data['key_ref'],
                        capabilities=agent_data.get('capabilities', []),
                        enabled=agent_data.get('enabled', True)
                    )
        except Exception as e:
            print(f"Error loading config: {e}")

    def register_agent(self, id: str, provider: str, key_ref: str, capabilities: List[str], enabled: bool = True):
        self._agents[id] = AgentInfo(id, provider, key_ref, capabilities, enabled) # Changed from self.agents to self._agents

    def list_agents(self, role: str = None, enabled: bool = True) -> List[AgentInfo]:
        """
        Lists available agents, optionally filtered by role/capability or enabled status.
        """
        results = []
        for agent in self._agents.values():
            if enabled and not agent.enabled:
                continue
            # Basic role filter (matches if capability is present)
            if role and role not in agent.capabilities:
                continue
            results.append(agent)
        return results

    def acquire_agents(self, k: int, strategy: str = "random") -> List[str]:
        """
        Acquires k idle agents from the pool.
        Strategies: 'random', 'capability_match' (future)
        """
        available = [a.id for a in self._agents.values() if a.status == "IDLE" and a.enabled]
        if len(available) < k:
            return [] # Or return partial? For now, strict: all or nothing
        
        # Simple selection (first k)
        selected = available[:k]
        
        # Mark as BUSY
        for aid in selected:
            self._agents[aid].status = "BUSY"
            
        return selected

    def release_agents(self, agent_ids: List[str], status: str = "IDLE"):
        for aid in agent_ids:
            if aid in self.agents:
                self.agents[aid].status = status

    def get_api_key(self, agent_id: str) -> Optional[str]:
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        if agent.key_ref.startswith("ENV:"):
            env_var = agent.key_ref[4:]
            return os.environ.get(env_var)
        return None
