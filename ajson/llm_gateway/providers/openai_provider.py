"""
OpenAI Provider - Lazy imports to avoid dependency when not using paid mode
"""

from ajson.llm_gateway.base import LLMProvider
from ajson.llm_gateway.types import LLMRequest, LLMResponse, Usage
from ajson.llm_gateway.config import OPENAI_API_KEY, OPENAI_DEFAULT_MODEL, calculate_cost
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openai import OpenAI


class OpenAIProvider(LLMProvider):
    """OpenAI provider using Responses API"""
    
    def __init__(self, model: str = OPENAI_DEFAULT_MODEL):
        self.model = model
        self._client = None
    
    @property
    def provider_name(self) -> str:
        return "OPENAI"
    
    def _get_client(self) -> "OpenAI":
        """Lazy import and initialize OpenAI client"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )
        return self._client
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI Responses API"""
        client = self._get_client()
        
        # Build messages
        messages = []
        if request.system_instruction:
            messages.append({"role": "system", "content": request.system_instruction})
        messages.append({"role": "user", "content": request.prompt})
        
        # Call API
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        
        # Extract response
        text = response.choices[0].message.content if response.choices else ""
        
        # Extract usage
        usage_data = response.usage if hasattr(response, "usage") else None
        usage = None
        cost_estimate = None
        
        if usage_data:
            input_tokens = getattr(usage_data, "prompt_tokens", 0)
            output_tokens = getattr(usage_data, "completion_tokens", 0)
            total_tokens = getattr(usage_data, "total_tokens", 0)
            
            usage = Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                raw_usage=usage_data.model_dump() if hasattr(usage_data, "model_dump") else None,
            )
            
            # Calculate cost
            cost_estimate = calculate_cost("OPENAI", self.model, input_tokens, output_tokens)
        
        return LLMResponse(
            text=text,
            usage=usage,
            provider="openai",
           model=self.model,
            provider_request_id=getattr(response, "id", None),
            cost_estimate_usd=cost_estimate,
            timestamp=datetime.now(),
        )
