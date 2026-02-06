"""
Tests for LLM Gateway DRY_RUN provider
"""

import pytest
import os
from ajson.llm_gateway import get_gateway, LLMRequest


def test_dry_run_provider_returns_deterministic_response():
    """DRY_RUN provider returns deterministic, predictable response"""
    # Set environment
    os.environ["LLM_PROVIDER"] = "DRY_RUN"
    os.environ["LLM_ENABLE_PAID"] = "0"
    
    gateway = get_gateway()
    request = LLMRequest(
        task_id="test_1",
        role="planner",
        prompt="Test prompt for deterministic response",
    )
    
    response = gateway.generate_text(request)
    
    # Should be awaitable, but gateway wraps in sync context
    import asyncio
    result = asyncio.run(response) if asyncio.iscoroutine(response) else response
    
    assert result.text.startswith("DRY_RUN response for planner:")
    assert result.provider == "dry_run"
    assert result.model == "dry_run"
    assert result.cost_estimate_usd == 0.0
    assert result.usage is not None
    assert result.usage.total_tokens > 0


def test_gateway_defaults_to_dry_run():
    """Without env vars, gateway defaults to DRY_RUN"""
    # Clear environment
    os.environ.pop("LLM_PROVIDER", None)
    os.environ.pop("LLM_ENABLE_PAID", None)
    
    # Force new gateway instance
    from ajson.llm_gateway import gateway as gw_module
    gw_module._gateway = None
    
    gateway = get_gateway()
    request = LLMRequest(
        task_id="test_default",
        role="planner",
        prompt="Default test",
    )
    
    import asyncio
    response = asyncio.run(gateway.generate_text(request))
    
    assert response.provider == "dry_run"
    assert response.cost_estimate_usd == 0.0


def test_dry_run_no_external_dependencies():
    """DRY_RUN works without openai or google-genai installed"""
    os.environ["LLM_PROVIDER"] = "DRY_RUN"
    os.environ["LLM_ENABLE_PAID"] = "0"
    
    # This test passes if no ImportError is raised
    from ajson.llm_gateway.providers.dry_run import DryRunProvider
    
    provider = DryRunProvider()
    request = LLMRequest(
        task_id="test_deps",
        role="eyes",
        prompt="Dependency test",
    )
    
    import asyncio
    response = asyncio.run(provider.generate_text(request))
    
    assert response.text is not None
    assert "DRY_RUN" in response.text
