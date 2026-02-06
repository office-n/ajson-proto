"""
Main LLM Gateway - Entry point with guards and provider selection
"""

from ajson.llm_gateway.base import LLMProvider
from ajson.llm_gateway.types import LLMRequest, LLMResponse, ApprovalRequired
from ajson.llm_gateway.config import LLM_PROVIDER, LLM_ENABLE_PAID
from ajson.llm_gateway.providers.dry_run import DryRunProvider
from ajson.llm_gateway.budget_guard import get_budget_guard
from ajson.llm_gateway.router import get_router
from ajson.llm_gateway import audit


class LLMGateway:
    """Main gateway with guards and provider management"""
    
    def __init__(self):
        self.provider: LLMProvider = self._initialize_provider()
        self.budget_guard = get_budget_guard()
        self.router = get_router()
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize provider based on configuration"""
        provider_name = LLM_PROVIDER
        enable_paid = LLM_ENABLE_PAID == "1"
        
        # Always default to DRY_RUN if not explicitly enabled
        if provider_name == "DRY_RUN" or not enable_paid:
            if provider_name != "DRY_RUN" and not enable_paid:
                audit.log_request(
                    request=LLMRequest(task_id="init", role="system", prompt=""),
                    provider=provider_name,
                    model="N/A",
                    decision="blocked",
                    reason="LLM_ENABLE_PAID is not set to '1'",
                )
            return DryRunProvider()
        
        # Paid providers (lazy import)
        if provider_name == "OPENAI":
            from ajson.llm_gateway.providers.openai_provider import OpenAIProvider
            model = self.router.route(
                LLMRequest(task_id="init", role="planner", prompt=""),
                "OPENAI"
            )
            return OpenAIProvider(model=model)
        
        elif provider_name == "GEMINI":
            from ajson.llm_gateway.providers.gemini_provider import GeminiProvider
            model = self.router.route(
                LLMRequest(task_id="init", role="eyes", prompt=""),
                "GEMINI"
            )
            return GeminiProvider(model=model)
        
        # Fallback to DRY_RUN for unknown providers
        audit.log_request(
            request=LLMRequest(task_id="init", role="system", prompt=""),
            provider=provider_name,
            model="N/A",
            decision="blocked",
            reason=f"Unknown provider '{provider_name}', falling back to DRY_RUN",
        )
        return DryRunProvider()
    
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text with all guards applied
        
        Raises:
            ApprovalRequired: If approval is needed (budget, high-cost model, etc.)
            BudgetExceeded: If budget would be exceeded
        """
        # 1. Budget pre-check
        try:
            self.budget_guard.enforce_budget()
        except Exception as e:
            audit.log_error("budget_exceeded", str(e), {"task_id": request.task_id})
            raise
        
        # 2. Route to model (may raise ApprovalRequired)
        try:
            if isinstance(self.provider, DryRunProvider):
                model = "dry_run"
            else:
                model = self.router.route(request, self.provider.provider_name)
        except ApprovalRequired as e:
            audit.log_request(
                request=request,
                provider=self.provider.provider_name,
                model="N/A",
                decision="approval_required",
                reason=e.reason,
            )
            raise
        
        # 3. Log request
        audit.log_request(
            request=request,
            provider=self.provider.provider_name,
            model=model,
            decision="allowed",
        )
        
        # 4. Call provider
        response = await self.provider.generate_text(request)
        
        # 5. Record cost
        if response.cost_estimate_usd and response.cost_estimate_usd > 0:
            self.budget_guard.record_cost(response.cost_estimate_usd)
        
        # 6. Log response
        audit.log_response(request, response, response.cost_estimate_usd)
        
        # 7. Budget post-check (for next request prediction)
        is_safe, current, predicted = self.budget_guard.check_budget()
        audit.log_budget_check(current, predicted, self.budget_guard.daily_limit, is_safe)
        
        return response


# Global instance
_gateway: LLMGateway = None


def get_gateway() -> LLMGateway:
    """Get global gateway instance (singleton)"""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway
