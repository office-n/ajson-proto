"""
Configuration for LLM Gateway
"""

import os
from typing import Dict


# Provider selection
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "DRY_RUN").upper()  # DRY_RUN, OPENAI, GEMINI
LLM_ENABLE_PAID = os.getenv("LLM_ENABLE_PAID", "0")  # "1" to enable paid providers

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model presets
OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Low cost default
OPENAI_HIGH_COST_MODEL = os.getenv("OPENAI_HIGH_COST_MODEL", "gpt-4o")
GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Low cost default
GEMINI_HIGH_COST_MODEL = os.getenv("GEMINI_HIGH_COST_MODEL", "gemini-1.5-pro")

# Budget
LLM_DAILY_BUDGET_USD = float(os.getenv("LLM_DAILY_BUDGET_USD", "3.00"))

# Price tables (snapshot as of 2026-02-06, update via PR review)
OPENAI_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {
        "input_per_1m": 0.15,
        "output_per_1m": 0.60,
    },
    "gpt-4o": {
        "input_per_1m": 2.50,
        "output_per_1m": 10.00,
    },
}

# Gemini pricing (placeholder - adjust based on actual Developer API pricing)
GEMINI_PRICING: Dict[str, Dict[str, float]] = {
    "gemini-1.5-flash": {
        "input_per_1m": 0.075,  # Estimated
        "output_per_1m": 0.30,  # Estimated
    },
    "gemini-1.5-pro": {
        "input_per_1m": 1.25,  # Estimated
        "output_per_1m": 5.00,  # Estimated
    },
}


def get_price_for_model(provider: str, model: str) -> Dict[str, float]:
    """Get pricing for a specific model"""
    if provider == "OPENAI":
        return OPENAI_PRICING.get(model, {"input_per_1m": 0.0, "output_per_1m": 0.0})
    elif provider == "GEMINI":
        return GEMINI_PRICING.get(model, {"input_per_1m": 0.0, "output_per_1m": 0.0})
    return {"input_per_1m": 0.0, "output_per_1m": 0.0}


def calculate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost estimate in USD"""
    pricing = get_price_for_model(provider, model)
    input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
    return input_cost + output_cost
