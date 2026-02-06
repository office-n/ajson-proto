"""
Tests for Tool Runner: audit logging + policy enforcement (minimal core tests)
"""
import pytest
import json
from ajson.hands.runner import ToolRunner
from ajson.hands.policy import PolicyDeniedError, PolicyDecision


def test_runner_audit_log_json():
    """Audit log should be JSON-serializable"""
    runner = ToolRunner(dry_run=True)
    result = runner.execute_tool("ls", {"-la": True})
    
    audit_json = runner.get_audit_log_json()
    parsed = json.loads(audit_json)
    assert len(parsed) == 1
    assert "decision" in parsed[0]


def test_runner_allowlist():
    """Allowlist operations should work"""
    runner = ToolRunner(dry_run=True)
    result = runner.execute_tool("ls", {"-la": True})
    assert result["status"] == "simulated"
    assert result["decision"] == PolicyDecision.ALLOW.value


def test_runner_denylist():
    """Denylist operations should raise PolicyDeniedError"""
    runner = ToolRunner(dry_run=True)
    with pytest.raises(PolicyDeniedError):
        runner.execute_tool("curl", {"url": "https://example.com"})
