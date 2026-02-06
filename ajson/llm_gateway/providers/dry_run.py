"""
DryRun Provider - Returns deterministic responses without external API calls
"""

from ajson.llm_gateway.base import LLMProvider
from ajson.llm_gateway.types import LLMRequest, LLMResponse, Usage
from datetime import datetime


class DryRunProvider(LLMProvider):
    """DryRun provider for testing and development"""
    
    @property
    def provider_name(self) -> str:
        return "DRY_RUN"
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate deterministic response"""
        # Deterministic response based on request
        prompt_preview = request.prompt[:50] if request.prompt else "empty"
        response_text = f"DRY_RUN response for {request.role}: [{prompt_preview}...]"
        
        # Mock usage (deterministic)
        usage = Usage(
            input_tokens=len(request.prompt) if request.prompt else 0,
            output_tokens=len(response_text),
            total_tokens=(len(request.prompt) if request.prompt else 0) + len(response_text),
        )
        
        return LLMResponse(
            text=response_text,
            usage=usage,
            provider="dry_run",
            model="dry_run",
            cost_estimate_usd=0.0,
            timestamp=datetime.now(),
        )
