"""
Tests for CAMR Model Router
"""

import pytest
from ajson.llm_gateway.router import ModelRouter
from ajson.llm_gateway.types import LLMRequest, ApprovalRequired
from ajson.llm_gateway.config import (
    OPENAI_DEFAULT_MODEL,
    OPENAI_HIGH_COST_MODEL,
    GEMINI_DEFAULT_MODEL,
)


def test_router_planner_role_uses_openai_mini():
    """Planner role routes to OpenAI mini (low cost)"""
    router = ModelRouter()
    request = LLMRequest(
        task_id="test",
        role="planner",
        prompt="Plan something",
    )
    
    model = router.route(request, "OPENAI")
    assert model == "gpt-4o-mini"  # Default low cost


def test_router_eyes_role_uses_gemini_flash():
    """Eyes role routes to Gemini flash (low cost)"""
    router = ModelRouter()
    request = LLMRequest(
        task_id="test",
        role="eyes",
        prompt="Read this large log",
    )
    
    model = router.route(request, "GEMINI")
    assert model == "gemini-1.5-flash"  # Default low cost


def test_router_high_quality_requires_approval():
    """High quality requirement raises ApprovalRequired"""
    router = ModelRouter()
    request = LLMRequest(
        task_id="test",
        role="planner",
        prompt="Critical task",
        desired_quality="high",
    )
    
    with pytest.raises(ApprovalRequired) as exc_info:
        router.route(request, "OPENAI")
    
    assert "high_cost_model_required" in exc_info.value.reason
    assert exc_info.value.details["requested_model"] == "gpt-4o"


def test_router_failure_tracking():
    """Router tracks failures for upgrade consideration"""
    router = ModelRouter()
    
    task_id = "failing_task"
    
    # Record failures
    router.record_failure(task_id)
    assert not router.should_upgrade(task_id, threshold=2)
    
    router.record_failure(task_id)
    assert router.should_upgrade(task_id, threshold=2)


def test_router_auditor_defaults_to_low_cost():
    """Auditor role defaults to low cost models"""
    router = ModelRouter()
    
    request = LLMRequest(
        task_id="test",
        role="auditor",
        prompt="Review this",
    )
    
    # OpenAI
    model_openai = router.route(request, "OPENAI")
    assert model_openai == OPENAI_DEFAULT_MODEL
    
    # Gemini
    model_gemini = router.route(request, "GEMINI")
    assert model_gemini == GEMINI_DEFAULT_MODEL
