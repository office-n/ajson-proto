"""
Audit logging for LLM Gateway
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from ajson.llm_gateway.types import LLMRequest, LLMResponse


# Configure logger
logger = logging.getLogger("ajson.llm_gateway.audit")


def log_request(
    request: LLMRequest,
    provider: str,
    model: str,
    decision: str,  # allowed, blocked, approval_required
    reason: Optional[str] = None,
):
    """Log an LLM request decision"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "llm_request",
        "task_id": request.task_id,
        "role": request.role,
        "provider": provider,
        "model": model,
        "decision": decision,
        "reason": reason,
        "prompt_length": len(request.prompt) if request.prompt else 0,
    }
    
    logger.info(json.dumps(event))


def log_response(
    request: LLMRequest,
    response: LLMResponse,
    cost_estimate: Optional[float] = None,
):
    """Log an LLM response"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "llm_response",
        "task_id": request.task_id,
        "role": request.role,
        "provider": response.provider,
        "model": response.model,
        "provider_request_id": response.provider_request_id,
        "response_length": len(response.text) if response.text else 0,
        "cost_estimate_usd": cost_estimate,
    }
    
    if response.usage:
        event["usage"] = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.total_tokens,
        }
    
    logger.info(json.dumps(event))


def log_budget_check(
    current_cost: float,
    predicted_cost: float,
    limit: float,
    is_safe: bool,
):
    """Log a budget check event"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "budget_check",
        "current_cost_usd": current_cost,
        "predicted_cost_usd": predicted_cost,
        "limit_usd": limit,
        "is_safe": is_safe,
    }
    
    logger.info(json.dumps(event))


def log_error(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
):
    """Log an error event"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "error",
        "error_type": error_type,
        "message": message,
        "details": details or {},
    }
    
    logger.error(json.dumps(event))
