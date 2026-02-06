"""
Tests for Budget Guard circuit breaker
"""

import pytest
from ajson.llm_gateway.budget_guard import BudgetGuard
from ajson.llm_gateway.types import BudgetExceeded


def test_budget_guard_tracks_daily_cost():
    """Budget guard correctly tracks cumulative daily costs"""
    guard = BudgetGuard(daily_limit_usd=3.00)
    
    # Record some costs
    guard.record_cost(0.50)
    guard.record_cost(0.75)
    guard.record_cost(0.25)
    
    daily_cost = guard.get_daily_cost()
    assert daily_cost == 1.50


def test_budget_guard_predicts_cost():
    """Budget guard predicts end-of-day cost based on recent average"""
    guard = BudgetGuard(daily_limit_usd=3.00)
    
    # Record recent costs (avg = 0.20)
    for _ in range(5):
        guard.record_cost(0.20)
    
    # Predict with 10 more requests expected
    predicted = guard.predict_daily_cost(expected_remaining_requests=10)
    
    # Should be: current (1.00) + (0.20 * 10) = 3.00
    assert predicted == 3.00


def test_budget_guard_enforces_limit():
    """Budget guard raises BudgetExceeded when predicted to exceed limit"""
    guard = BudgetGuard(daily_limit_usd=3.00)
    
    # Record expensive recent costs
    guard.record_cost(1.00)
    guard.record_cost(1.00)
    guard.record_cost(0.80)
    
    # Current: 2.80, avg recent: ~0.93, predicted with 10 more: 2.80 + 9.3 > 3.00
    with pytest.raises(BudgetExceeded) as exc_info:
        guard.enforce_budget(expected_remaining_requests=10)
    
    assert exc_info.value.predicted_cost > 3.00
    assert exc_info.value.limit == 3.00
    assert exc_info.value.current_cost == 2.80


def test_budget_guard_allows_safe_requests():
    """Budget guard allows requests when predicted cost is safe"""
    guard = BudgetGuard(daily_limit_usd=3.00)
    
    # Record small costs
    guard.record_cost(0.10)
    guard.record_cost(0.10)
    
    # Should not raise (current: 0.20, predicted with 10 more: 0.20 + 1.00 = 1.20 < 3.00)
    guard.enforce_budget(expected_remaining_requests=10)  # No exception


def test_budget_guard_check_budget_returns_status():
    """check_budget returns (is_safe, current, predicted) tuple"""
    guard = BudgetGuard(daily_limit_usd=3.00)
    
    guard.record_cost(0.50)
    
    is_safe, current, predicted = guard.check_budget(expected_remaining_requests=1)
    
    assert isinstance(is_safe, bool)
    assert current == 0.50
    assert predicted >= current


def test_budget_guard_conservative_with_no_history():
    """Budget guard is conservative when no cost history exists"""
    guard = BudgetGuard(daily_limit_usd=3.00)
    
    # No costs recorded yet
    predicted = guard.predict_daily_cost(expected_remaining_requests=10)
    
    # Should return current cost (0.0) since no recent costs to average
    assert predicted == 0.0
    
    # Should allow (since predicted = 0)
    guard.enforce_budget()  # No exception
