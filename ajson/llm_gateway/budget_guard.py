"""
Budget Guard - Daily cost tracking and circuit breaker
"""

from datetime import date
from typing import Dict, Tuple
from ajson.llm_gateway.types import BudgetExceeded
from ajson.llm_gateway.config import LLM_DAILY_BUDGET_USD


class BudgetGuard:
    """Tracks daily costs and enforces budget limits"""
    
    def __init__(self, daily_limit_usd: float = LLM_DAILY_BUDGET_USD):
        self.daily_limit = daily_limit_usd
        self.daily_costs: Dict[str, float] = {}  # date -> cumulative_cost
        self.recent_costs: list[float] = []
        self.max_recent = 10  # Track last N costs for prediction
    
    def _get_date_key(self) -> str:
        """Get current date as string key"""
        return date.today().isoformat()
    
    def get_daily_cost(self) -> float:
        """Get cumulative cost for today"""
        date_key = self._get_date_key()
        return self.daily_costs.get(date_key, 0.0)
    
    def record_cost(self, cost_usd: float):
        """Record a cost"""
        if cost_usd is None or cost_usd <= 0:
            return
        
        date_key = self._get_date_key()
        self.daily_costs[date_key] = self.daily_costs.get(date_key, 0.0) + cost_usd
        
        # Track recent costs for prediction
        self.recent_costs.append(cost_usd)
        if len(self.recent_costs) > self.max_recent:
            self.recent_costs.pop(0)
    
    def predict_daily_cost(self, expected_remaining_requests: int = 10) -> float:
        """Predict end-of-day cost"""
        current = self.get_daily_cost()
        
        # If no recent costs, can't predict
        if not self.recent_costs:
            return current
        
        # Average of recent costs
        avg_cost = sum(self.recent_costs) / len(self.recent_costs)
        
        # Predict: current + (avg_cost * expected_remaining)
        predicted = current + (avg_cost * expected_remaining_requests)
        return predicted
    
    def check_budget(self, expected_remaining_requests: int = 10) -> Tuple[bool, float, float]:
        """
        Check if budget is safe to proceed
        
        Returns:
            (is_safe, current_cost, predicted_cost)
        """
        current = self.get_daily_cost()
        predicted = self.predict_daily_cost(expected_remaining_requests)
        
        is_safe = predicted <= self.daily_limit
        return is_safe, current, predicted
    
    def enforce_budget(self, expected_remaining_requests: int = 10):
        """Raise BudgetExceeded if predicted to exceed limit"""
        is_safe, current, predicted = self.check_budget(expected_remaining_requests)
        
        if not is_safe:
            raise BudgetExceeded(
                predicted_cost=predicted,
                limit=self.daily_limit,
                current_cost=current,
            )


# Global instance
_budget_guard = BudgetGuard()


def get_budget_guard() -> BudgetGuard:
    """Get global budget guard instance"""
    return _budget_guard
