"""
Tests for ajson.hands.runner (no network, all local)
"""
import pytest
from ajson.hands.runner import ToolRunner
from ajson.hands.policy import ApprovalRequiredError, ApprovalRequired


def test_tool_runner_dry_run_default():
    """ToolRunner should default to DRY_RUN mode"""
    runner = ToolRunner()
    assert runner.dry_run is True


def test_tool_runner_execute_dry_run():
    """DRY_RUN execution should return simulated result"""
    runner = ToolRunner(dry_run=True)
    result = runner.execute_tool("git_status", {"repo": "/foo"})
    
    assert result["dry_run"] is True
    assert result["status"] == "simulated"
    assert "DRY_RUN" in result["output"]
    assert result["requires_approval"] is False


def test_tool_runner_audit_log():
    """Audit log should record all executions"""
    runner = ToolRunner(dry_run=True)
    runner.execute_tool("tool1", {"arg": "val1"})
    runner.execute_tool("tool2", {"arg": "val2"})
    
    log = runner.get_audit_log()
    assert len(log) == 2
    assert log[0]["operation"] == "tool1 {'arg': 'val1'}"
    assert log[1]["operation"] == "tool2 {'arg': 'val2'}"


def test_tool_runner_approval_required_when_not_dry_run():
    """Non-DRY_RUN execution of destructive ops should raise ApprovalRequiredError"""
    runner = ToolRunner(dry_run=False)
    
    with pytest.raises(ApprovalRequiredError) as excinfo:
        runner.execute_tool("rm", {"-rf": "/foo"})
    
    assert "Destructive" in str(excinfo.value)
    assert excinfo.value.gate_type == ApprovalRequired.DESTRUCTIVE


def test_tool_runner_safe_operation_no_approval_needed():
    """Safe operations should not require approval even when not dry_run"""
    runner = ToolRunner(dry_run=False)
    result = runner.execute_tool("git_status", {"repo": "/foo"})
    
    assert result["requires_approval"] is False
    assert result["status"] == "executed"
