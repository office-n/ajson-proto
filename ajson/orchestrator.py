"""
State machine orchestrator for AJSON MVP
"""
from ajson import db
from ajson.models import MissionStatus, StepStatus
from ajson.roles import jarvis, cody
from ajson.tools import runner


def execute_mission(mission_id: int):
    """
    Execute mission through state transitions
    
    State flow:
    CREATED → PLANNED → PRE_AUDIT → EXECUTE → POST_AUDIT → FINALIZE → DONE
                                      ↓
                              PENDING_APPROVAL (if approval needed)
    """
    mission = db.get_mission(mission_id)
    if not mission:
        raise ValueError(f"Mission {mission_id} not found")
    
    status = mission["status"]
    
    # State transition logic
    if status == MissionStatus.CREATED:
        _transition_to_planned(mission_id, mission["description"])
    elif status == MissionStatus.PLANNED:
        _transition_to_pre_audit(mission_id)
    elif status == MissionStatus.PRE_AUDIT:
        _transition_to_execute(mission_id)
    elif status == MissionStatus.EXECUTE:
        _transition_to_post_audit(mission_id)
    elif status == MissionStatus.POST_AUDIT:
        _transition_to_finalize(mission_id)
    elif status == MissionStatus.FINALIZE:
        _transition_to_done(mission_id)
    elif status == MissionStatus.PENDING_APPROVAL:
        # Wait for manual approval
        return
    elif status == MissionStatus.DONE:
        # Already complete
        return
    else:
        raise ValueError(f"Unknown status: {status}")


def _transition_to_planned(mission_id: int, description: str):
    """CREATED → PLANNED"""
    # Jarvis creates plan
    plan = jarvis.plan_mission(description)
    
    # Create step record
    step_id = db.create_step(
        mission_id=mission_id,
        role="jarvis",
        input_data=description,
        status=StepStatus.COMPLETED
    )
    db.update_step(step_id, plan, StepStatus.COMPLETED)
    
    # Create artifact
    db.create_artifact(
        mission_id=mission_id,
        artifact_type="plan",
        path=f"mission_{mission_id}_plan.md",
        content=plan
    )
    
    # Update mission status
    db.update_mission_status(mission_id, MissionStatus.PLANNED)


def _transition_to_pre_audit(mission_id: int):
    """PLANNED → PRE_AUDIT (or PENDING_APPROVAL)"""
    # Get mission description and plan
    mission = db.get_mission(mission_id)
    description = mission["description"]
    
    steps = db.get_steps_by_mission(mission_id)
    plan_step = [s for s in steps if s["role"] == "jarvis"][-1]
    plan = plan_step["output_data"]
    
    # Cody pre-audit checks both description and plan
    combined_input = f"Description: {description}\n\nPlan: {plan}"
    audit_result = cody.pre_audit(combined_input)
    
    # Create step record
    step_id = db.create_step(
        mission_id=mission_id,
        role="cody_pre_audit",
        input_data=combined_input,
        status=StepStatus.COMPLETED
    )
    db.update_step(step_id, str(audit_result), StepStatus.COMPLETED)
    
    if not audit_result["approved"]:
        # Approval required
        db.create_approval(
            mission_id=mission_id,
            gate_type=audit_result["gate_type"],
            reason=audit_result["reason"]
        )
        db.update_mission_status(mission_id, MissionStatus.PENDING_APPROVAL)
    else:
        db.update_mission_status(mission_id, MissionStatus.PRE_AUDIT)


def _transition_to_execute(mission_id: int):
    """PRE_AUDIT → EXECUTE"""
    # Execute test command (mock execution)
    step_id = db.create_step(
        mission_id=mission_id,
        role="ants_worker",
        input_data="Execute pytest",
        status=StepStatus.RUNNING
    )
    
    # Run safe command
    success, result, error = runner.run_tool("echo 'Mock test execution: All tests passed'")
    
    # Record tool run
    db.create_tool_run(
        step_id=step_id,
        command="echo 'Mock test execution: All tests passed'",
        result=result,
        blocked=not success,
        block_reason=error
    )
    
    db.update_step(step_id, result, StepStatus.COMPLETED if success else StepStatus.FAILED)
    db.update_mission_status(mission_id, MissionStatus.EXECUTE)


def _transition_to_post_audit(mission_id: int):
    """EXECUTE → POST_AUDIT (or PENDING_APPROVAL)"""
    # Get execution log
    tool_runs = db.get_tool_runs_by_mission(mission_id)
    execution_log = "\n".join([f"{tr['command']}: {tr['result']}" for tr in tool_runs])
    
    # Cody post-audit
    audit_result = cody.post_audit(execution_log)
    
    step_id = db.create_step(
        mission_id=mission_id,
        role="cody_post_audit",
        input_data=execution_log,
        status=StepStatus.COMPLETED
    )
    db.update_step(step_id, str(audit_result), StepStatus.COMPLETED)
    
    if not audit_result["approved"]:
        db.create_approval(
            mission_id=mission_id,
            gate_type=audit_result["gate_type"],
            reason=audit_result["reason"]
        )
        db.update_mission_status(mission_id, MissionStatus.PENDING_APPROVAL)
    else:
        db.update_mission_status(mission_id, MissionStatus.POST_AUDIT)


def _transition_to_finalize(mission_id: int):
    """POST_AUDIT → FINALIZE"""
    # Jarvis creates final report
    steps = db.get_steps_by_mission(mission_id)
    steps_summary = "\n".join([f"- {s['role']}: {s['status']}" for s in steps])
    
    final_report = jarvis.finalize_mission(mission_id, steps_summary)
    
    step_id = db.create_step(
        mission_id=mission_id,
        role="jarvis_finalize",
        input_data=steps_summary,
        status=StepStatus.COMPLETED
    )
    db.update_step(step_id, final_report, StepStatus.COMPLETED)
    
    db.create_artifact(
        mission_id=mission_id,
        artifact_type="final_report",
        path=f"mission_{mission_id}_report.md",
        content=final_report
    )
    
    db.update_mission_status(mission_id, MissionStatus.FINALIZE)


def _transition_to_done(mission_id: int):
    """FINALIZE → DONE"""
    db.update_mission_status(mission_id, MissionStatus.DONE)


def approve_mission(mission_id: int):
    """
    Approve pending mission and resume execution
    """
    # Get pending approvals
    approvals = db.get_pending_approvals(mission_id)
    if not approvals:
        raise ValueError(f"No pending approvals for mission {mission_id}")
    
    # Approve all pending
    for approval in approvals:
        db.approve_approval(approval["id"])
    
    # Resume from where we stopped
    mission = db.get_mission(mission_id)
    
    # Determine next state based on last step role
    steps = db.get_steps_by_mission(mission_id)
    if steps:
        last_role = steps[-1]["role"]
        
        # Resume based on where we stopped
        if last_role == "cody_pre_audit":
            # Stopped during pre-audit, resume to PRE_AUDIT
            resume_state = MissionStatus.PRE_AUDIT
        elif last_role == "cody_post_audit":
            # Stopped during post-audit, resume to POST_AUDIT
            resume_state = MissionStatus.POST_AUDIT
        else:
            # Default: resume to PRE_AUDIT for safety
            resume_state = MissionStatus.PRE_AUDIT
    else:
        # No steps found, default to PRE_AUDIT
        resume_state = MissionStatus.PRE_AUDIT
    
    db.update_mission_status(mission_id, resume_state)

