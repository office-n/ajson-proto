"""
Gemini Provider - Lazy imports to avoid dependency when not using paid mode
"""

from ajson.llm_gateway.base import LLMProvider
from ajson.llm_gateway.types import LLMRequest, LLMResponse, Usage
from ajson.llm_gateway.config import GEMINI_API_KEY, GEMINI_DEFAULT_MODEL, calculate_cost
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google import genai


class GeminiProvider(LLMProvider):
    """Gemini provider using Google GenAI SDK"""
    
    def __init__(self, model: str = GEMINI_DEFAULT_MODEL):
        self.model = model
        self._client = None
    
    @property
    def provider_name(self) -> str:
        return "GEMINI"
    
    def _get_client(self) -> "genai.Client":
        """Lazy import and initialize Gemini client"""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=GEMINI_API_KEY)
            except ImportError:
                raise ImportError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai"
                )
        return self._client
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """Generate text using Gemini API"""
        client = self._get_client()
        
        # Build config with system instruction if provided
        config = None
        if request.system_instruction:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=request.system_instruction
            )
        
        # Call API
        response = client.models.generate_content(
            model=self.model,
            contents=request.prompt,
            config=config,
        )
        
        # Extract response text
        text = response.text if hasattr(response, "text") else ""
        
        # Extract usage metadata
        usage_metadata = getattr(response, "usage_metadata", None)
        usage = None
        cost_estimate = None
        
        if usage_metadata:
            input_tokens = getattr(usage_metadata, "prompt_token_count", 0)
            output_tokens = getattr(usage_metadata, "candidates_token_count", 0)
            total_tokens = getattr(usage_metadata, "total_token_count", 0)
            
            usage = Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                raw_usage={"usage_metadata": str(usage_metadata)},
            )
            
            # Calculate cost (may be None if pricing table incomplete)
            cost_estimate = calculate_cost("GEMINI", self.model, input_tokens, output_tokens)
        
        return LLMResponse(
            text=text,
            usage=usage,
            provider="gemini",
            model=self.model,
            cost_estimate_usd=cost_estimate,
            timestamp=datetime.now(),
        )
