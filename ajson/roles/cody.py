"""
Cody role - Pre and post auditing
"""
from ajson.llm import mock
import os


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
    elif LLM_MODE == "OPENAI":
        # TODO: Implement OpenAI integration
        raise NotImplementedError("OpenAI mode not yet implemented")
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")


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
    elif LLM_MODE == "OPENAI":
        # TODO: Implement OpenAI integration
        raise NotImplementedError("OpenAI mode not yet implemented")
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")
