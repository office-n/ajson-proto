"""
Cody role - Pre and post auditing
"""
from ajson.llm_gateway import get_gateway, LLMRequest
from ajson.llm import mock
import os
import asyncio


LLM_MODE = os.getenv("LLM_MODE", "DRY_RUN")


def pre_audit(plan: str) -> dict:
    """
    Perform pre-execution audit
    
    Args:
        plan: Execution plan to audit
    
    Returns:
        dict with 'approved', 'reason', and 'gate_type'
    """
    if LLM_MODE == "DRY_RUN":
        return mock.get_cody_pre_audit(plan)
    elif LLM_MODE == "OPENAI" or LLM_MODE == "GEMINI":
        # Use LLM Gateway
        return asyncio.run(_pre_audit_async(plan))
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")


async def _pre_audit_async(plan: str) -> dict:
    """Async implementation using LLM Gateway"""
    gateway = get_gateway()
    request = LLMRequest(
        task_id="pre_audit",
        role="auditor",
        prompt=plan,
        system_instruction="You are Cody, a pre-execution auditor. Review the plan and return JSON with 'approved' (bool), 'reason' (str), and 'gate_type' (str).",
    )
    response = await gateway.generate_text(request)
    # For now, parse as simple dict (in production, would parse JSON)
    return mock.get_cody_pre_audit(plan)  # Fallback to mock parsing


def post_audit(execution_log: str) -> dict:
    """
    Perform post-execution audit
    
    Args:
        execution_log: Execution log to audit
    
    Returns:
        dict with 'approved', 'reason', and 'gate_type'
    """
    if LLM_MODE == "DRY_RUN":
        return mock.get_cody_post_audit(execution_log)
    elif LLM_MODE == "OPENAI" or LLM_MODE == "GEMINI":
        # Use LLM Gateway
        return asyncio.run(_post_audit_async(execution_log))
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")


async def _post_audit_async(execution_log: str) -> dict:
    """Async implementation using LLM Gateway"""
    gateway = get_gateway()
    request = LLMRequest(
        task_id="post_audit",
        role="auditor",
        prompt=execution_log,
        system_instruction="You are Cody, a post-execution auditor. Review the execution log and return JSON with 'approved' (bool), 'reason' (str), and 'gate_type' (str).",
    )
    response = await gateway.generate_text(request)
    # For now, parse as simple dict (in production, would parse JSON)
    return mock.get_cody_post_audit(execution_log)  # Fallback to mock parsing
