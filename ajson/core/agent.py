# ajson/core/agent.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class Agent(ABC):
    """
    Abstract base class for all Agents.
    """
    @abstractmethod
    def run(self, input_data: Any) -> Dict[str, Any]:
        pass
