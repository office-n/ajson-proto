"""
CAMR - Cost-Adaptive Model Routing
"""

from ajson.llm_gateway.types import LLMRequest, ApprovalRequired
from ajson.llm_gateway.config import (
    OPENAI_DEFAULT_MODEL,
    OPENAI_HIGH_COST_MODEL,
    GEMINI_DEFAULT_MODEL,
    GEMINI_HIGH_COST_MODEL,
)


class ModelRouter:
    """Routes requests to appropriate models based on task characteristics"""
    
    def __init__(self):
        self.failure_counts = {}  # task_id -> count
    
    def route(self, request: LLMRequest, provider: str) -> str:
        """
        Determine which model to use based on request characteristics
        
        Returns:
            model_name
        
        Raises:
            ApprovalRequired if high-cost model is needed
        """
        role = request.role.lower()
        quality = request.desired_quality.lower()
        
        # Check for explicit high quality requirement
        if quality == "high":
            return self._request_high_cost_model(provider, "explicit_high_quality")
        
        # Role-based routing (deterministic)
        if provider == "OPENAI":
            if role in ["planner", "auditor"]:
                return OPENAI_DEFAULT_MODEL  # gpt-4o-mini
            else:
                # Unknown role, default to low cost
                return OPENAI_DEFAULT_MODEL
        
        elif provider == "GEMINI":
            if role in ["eyes", "auditor"]:
                return GEMINI_DEFAULT_MODEL  # flash
            else:
                return GEMINI_DEFAULT_MODEL
        
        # Fallback
        return OPENAI_DEFAULT_MODEL if provider == "OPENAI" else GEMINI_DEFAULT_MODEL
    
    def record_failure(self, task_id: str):
        """Record a failure for a task"""
        self.failure_counts[task_id] = self.failure_counts.get(task_id, 0) + 1
    
    def should_upgrade(self, task_id: str, threshold: int = 2) -> bool:
        """Check if task has failed enough to warrant upgrade"""
        return self.failure_counts.get(task_id, 0) >= threshold
    
    def _request_high_cost_model(self, provider: str, reason: str) -> str:
        """Request approval for high-cost model"""
        model = OPENAI_HIGH_COST_MODEL if provider == "OPENAI" else GEMINI_HIGH_COST_MODEL
        
        raise ApprovalRequired(
            reason=f"high_cost_model_required: {reason}",
            details={
                "provider": provider,
                "requested_model": model,
                "reason": reason,
            }
        )


# Global instance
_router = ModelRouter()


def get_router() -> ModelRouter:
    """Get global router instance"""
    return _router
