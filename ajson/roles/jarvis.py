"""
Jarvis role - Planning and finalization
"""
from ajson.llm_gateway import get_gateway, LLMRequest
from ajson.llm import mock
import os
import asyncio


LLM_MODE = os.getenv("LLM_MODE", "DRY_RUN")


def plan_mission(mission_description: str) -> str:
    """
    Create execution plan for mission
    
    Args:
        mission_description: Mission description text
    
    Returns:
        Execution plan
    """
    if LLM_MODE == "DRY_RUN":
        return mock.get_jarvis_plan(mission_description)
    elif LLM_MODE == "OPENAI" or LLM_MODE == "GEMINI":
        # Use LLM Gateway
        return asyncio.run(_plan_mission_async(mission_description))
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")


async def _plan_mission_async(mission_description: str) -> str:
    """Async implementation using LLM Gateway"""
    gateway = get_gateway()
    request = LLMRequest(
        task_id="plan_mission",
        role="planner",
        prompt=mission_description,
        system_instruction="You are Jarvis, a mission planning assistant. Create a detailed execution plan.",
    )
    response = await gateway.generate_text(request)
    return response.text


def finalize_mission(mission_id: int, steps_summary: str) -> str:
    """
    Create final report for mission
    
    Args:
        mission_id: Mission ID
        steps_summary: Summary of executed steps
    
    Returns:
        Final report
    """
    if LLM_MODE == "DRY_RUN":
        return mock.get_jarvis_finalize(mission_id, steps_summary)
    elif LLM_MODE == "OPENAI" or LLM_MODE == "GEMINI":
        # Use LLM Gateway
        return asyncio.run(_finalize_mission_async(mission_id, steps_summary))
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")


async def _finalize_mission_async(mission_id: int, steps_summary: str) -> str:
    """Async implementation using LLM Gateway"""
    gateway = get_gateway()
    request = LLMRequest(
        task_id=f"finalize_mission_{mission_id}",
        role="planner",
        prompt=f"Mission ID: {mission_id}\n\nSteps Summary:\n{steps_summary}",
        system_instruction="You are Jarvis, a mission finalization assistant. Create a comprehensive final report.",
    )
    response = await gateway.generate_text(request)
    return response.text
