"""
Type definitions for LLM Gateway
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Usage:
    """Normalized usage statistics across providers"""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    raw_usage: Optional[Dict[str, Any]] = None  # Provider-specific raw data


@dataclass
class LLMRequest:
    """Unified LLM request"""
    task_id: str
    role: str  # planner / eyes / auditor
    prompt: str
    system_instruction: Optional[str] = None
    context_refs: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None
    desired_quality: str = "standard"  # standard / high
    

@dataclass
class LLMResponse:
    """Unified LLM response"""
    text: str
    usage: Optional[Usage] = None
    provider: str = "dry_run"
    model: str = "dry_run"
    provider_request_id: Optional[str] = None
    cost_estimate_usd: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApprovalRequired(Exception):
    """Raised when approval is required before proceeding"""
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"ApprovalRequired: {self.reason}"


@dataclass
class BudgetExceeded(Exception):
    """Raised when budget limit is exceeded"""
    predicted_cost: float
    limit: float
    current_cost: float
    
    def __str__(self):
        return f"BudgetExceeded: predicted ${self.predicted_cost:.4f} > limit ${self.limit:.2f} (current: ${self.current_cost:.4f})"
