"""
Tests for LLM Gateway paid guard enforcement
"""

import pytest
import os
from ajson.llm_gateway import get_gateway, LLMRequest
from ajson.llm_gateway.types import ApprovalRequired


def test_openai_without_enable_paid_blocks():
    """LLM_PROVIDER=OPENAI but LLM_ENABLE_PAID!=1 falls back to DRY_RUN"""
    os.environ["LLM_PROVIDER"] = "OPENAI"
    os.environ["LLM_ENABLE_PAID"] = "0"  # Explicitly disabled
    
    # Force new gateway
    from ajson.llm_gateway import gateway as gw_module
    gw_module._gateway = None
    
    gateway = get_gateway()
    request = LLMRequest(
        task_id="test_openai_blocked",
        role="planner",
        prompt="Test with OPENAI provider but paid disabled",
    )
    
    import asyncio
    response = asyncio.run(gateway.generate_text(request))
    
    # Should fall back to DRY_RUN
    assert response.provider == "dry_run"
    assert response.cost_estimate_usd == 0.0


def test_gemini_without_enable_paid_blocks():
    """LLM_PROVIDER=GEMINI but LLM_ENABLE_PAID!=1 falls back to DRY_RUN"""
    os.environ["LLM_PROVIDER"] = "GEMINI"
    os.environ["LLM_ENABLE_PAID"] = "0"
    
    from ajson.llm_gateway import gateway as gw_module
    gw_module._gateway = None
    
    gateway = get_gateway()
    request = LLMRequest(
        task_id="test_gemini_blocked",
        role="eyes",
        prompt="Test with GEMINI provider but paid disabled",
    )
    
    import asyncio
    response = asyncio.run(gateway.generate_text(request))
    
    # Should fall back to DRY_RUN
    assert response.provider == "dry_run"


def test_invalid_provider_falls_back_to_dry_run():
    """Invalid LLM_PROVIDER safely falls back to DRY_RUN"""
    os.environ["LLM_PROVIDER"] = "INVALID_PROVIDER"
    os.environ["LLM_ENABLE_PAID"] = "1"  # Even with paid enabled
    
    from ajson.llm_gateway import gateway as gw_module
    gw_module._gateway = None
    
    gateway = get_gateway()
    request = LLMRequest(
        task_id="test_invalid",
        role="planner",
        prompt="Test with invalid provider",
    )
    
    import asyncio
    response = asyncio.run(gateway.generate_text(request))
    
    # Should safely fall back to DRY_RUN
    assert response.provider == "dry_run"


def test_lazy_import_not_triggered_in_dry_run():
    """OpenAI/Gemini imports not triggered when using DRY_RUN"""
    os.environ["LLM_PROVIDER"] = "DRY_RUN"
    os.environ["LLM_ENABLE_PAID"] = "0"
    
    # Import the provider modules
    from ajson.llm_gateway.providers import openai_provider
    from ajson.llm_gateway.providers import gemini_provider
    
    # Providers should exist but not have initialized clients
    assert openai_provider.OpenAIProvider is not None
    assert gemini_provider.GeminiProvider is not None
    
    # Creating DRY_RUN gateway should not import openai/google
    from ajson.llm_gateway import gateway as gw_module
    gw_module._gateway = None
    
    gateway = get_gateway()
    
    # This should not raise ImportError even if openai/google-genai not installed
    request = LLMRequest(task_id="test", role="planner", prompt="test")
    import asyncio
    response = asyncio.run(gateway.generate_text(request))
    assert response.provider == "dry_run"
