"""
Jarvis role - Planning and finalization
"""
from ajson.llm import mock
import os


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
    elif LLM_MODE == "OPENAI":
        # TODO: Implement OpenAI integration
        raise NotImplementedError("OpenAI mode not yet implemented")
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")


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
    elif LLM_MODE == "OPENAI":
        # TODO: Implement OpenAI integration
        raise NotImplementedError("OpenAI mode not yet implemented")
    else:
        raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")
