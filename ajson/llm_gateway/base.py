"""
Base provider interface
"""

from abc import ABC, abstractmethod
from ajson.llm_gateway.types import LLMRequest,LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text from LLM"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier"""
        pass
