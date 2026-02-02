"""
Mock LLM responses for DRY_RUN mode
"""


def get_jarvis_plan(mission_description: str) -> str:
    """
    Get mock planning response from Jarvis
    """
    return f"""# Mission Plan

## Objective
{mission_description}

## Execution Steps
1. Analyze mission requirements
2. Prepare test environment
3. Execute pytest suite
4. Generate report artifact

## Success Criteria
- All tests pass
- Report generated successfully
- No security violations detected

## Risk Assessment
- Low risk: Read-only operations
- No external dependencies
- Workspace isolated
"""


def get_cody_pre_audit(plan: str) -> dict:
    """
    Get mock pre-audit response from Cody
    
    Returns:
        dict with 'approved' (bool) and 'reason' (str)
    """
    plan_lower = plan.lower()
    
    # Extract description if present (format: "Description: ...\n\nPlan: ...")
    description_part = ""
    if "description:" in plan_lower:
        parts = plan.split("\n\n", 1)
        description_part = parts[0].lower()
    else:
        description_part = plan_lower
    
    # 承認ゲートキーワードの検出（descriptionで検査）
    dangerous_keywords = ["deploy", "delete", "drop", "public", "external", "sudo", "rm", "production"]
    
    for keyword in dangerous_keywords:
        if keyword in description_part:
            return {
                "approved": False,
                "reason": f"Approval required: Detected potentially dangerous operation '{keyword}'",
                "gate_type": "security"
            }
    
    return {
        "approved": True,
        "reason": "Pre-audit passed: No security concerns detected",
        "gate_type": None
    }


def get_cody_post_audit(execution_log: str) -> dict:
    """
    Get mock post-audit response from Cody
    
    Returns:
        dict with 'approved' (bool) and 'reason' (str)
    """
    # 実行ログから問題を検出
    if "BLOCKED" in execution_log or "ERROR" in execution_log.upper():
        return {
            "approved": False,
            "reason": "Post-audit failed: Execution contained errors or blocked operations",
            "gate_type": "execution_error"
        }
    
    return {
        "approved": True,
        "reason": "Post-audit passed: Execution completed successfully",
        "gate_type": None
    }


def get_jarvis_finalize(mission_id: int, steps_summary: str) -> str:
    """
    Get mock finalization response from Jarvis
    """
    return f"""# Mission {mission_id} - Final Report

## Summary
Mission completed successfully through automated orchestration.

## Steps Executed
{steps_summary}

## Artifacts
- Execution logs stored in SSOT
- Test results archived
- All operations tracked

## Status
✅ DONE - Mission objectives achieved
"""


# サンプルミッション用のレスポンス
def get_sample_mission_response() -> str:
    """Sample mission for testing"""
    return """Execute pytest in workspace to verify system functionality"""
