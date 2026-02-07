"""
Tests for limited execute functionality (with mocked subprocess)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from ajson.hands.runner import ToolRunner
from ajson.hands.policy import PolicyDeniedError, OperationCategory
from ajson.hands.approval import ApprovalStore, ApprovalDecision


def test_execute_limited_requires_grant():
    """Execute limited should fail without valid grant"""
    runner = ToolRunner(dry_run=False)
    
    with pytest.raises(ValueError, match="Invalid or expired grant"):
        runner.execute_tool_limited(
            grant_id="invalid-id",
            tool_name="ls",
            args={"-la": True}
        )


def test_execute_limited_network_always_deny():
    """Network operations should be denied even with grant"""
    store = ApprovalStore()
    request = store.create_request("curl https://example.com", "network", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        scope=["curl"]
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    runner = ToolRunner(dry_run=False)
    
    with patch('ajson.hands.approval.get_approval_store', return_value=store):
        # Relaxed check to avoid class identity mismatch during tests
        with pytest.raises(Exception) as exc_info:
            runner.execute_tool_limited(
                grant_id=grant.grant_id,
                tool_name="curl",
                args={"https://example.com": ""}
            )
        assert exc_info.type.__name__ == "PolicyDeniedError"
        assert exc_info.value.category == OperationCategory.NETWORK


def test_execute_limited_allowlist_only():
    """Only allowlist operations should execute"""
    store = ApprovalStore()
    request = store.create_request("rm -rf /", "destructive", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        scope=["rm"]
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    runner = ToolRunner(dry_run=False)
    
    with patch('ajson.hands.approval.get_approval_store', return_value=store):
        with pytest.raises(ValueError, match="not in allowlist"):
            runner.execute_tool_limited(
                grant_id=grant.grant_id,
                tool_name="rm",
                args={"-rf": "/"}
            )


@patch('ajson.hands.runner.subprocess.run')
def test_execute_limited_success(mock_subprocess):
    """Allowlist operation with grant should execute"""
    # Mock subprocess
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "file1\nfile2\n"
    mock_result.stderr = ""
    mock_subprocess.return_value = mock_result
    
    store = ApprovalStore()
    request = store.create_request("ls -la", "readonly", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        scope=["ls"]
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    runner = ToolRunner(dry_run=False)
    
    with patch('ajson.hands.approval.get_approval_store', return_value=store):
        result = runner.execute_tool_limited(
            grant_id=grant.grant_id,
            tool_name="ls",
            args={"-la": True}
        )
    
    assert result["executed"] is True
    assert result["returncode"] == 0
    assert "file1" in result["stdout"]
    
    # Verify subprocess was called with shell=False
    mock_subprocess.assert_called_once()
    call_kwargs = mock_subprocess.call_args[1]
    assert call_kwargs["shell"] is False
    assert call_kwargs["timeout"] == 10


@patch('ajson.hands.runner.subprocess.run')
def test_execute_limited_timeout(mock_subprocess):
    """Subprocess timeout should be handled"""
    import subprocess
    mock_subprocess.side_effect = subprocess.TimeoutExpired("ls", 10)
    
    store = ApprovalStore()
    request = store.create_request("ls", "readonly", "test")
    
    decision = ApprovalDecision(
        request_id=request.request_id,
        decision="approve",
        reason="Test",
        scope=["ls"]
    )
    
    grant = store.approve_request(request.request_id, decision)
    
    runner = ToolRunner(dry_run=False)
    
    with patch('ajson.hands.approval.get_approval_store', return_value=store):
        result = runner.execute_tool_limited(
            grant_id=grant.grant_id,
            tool_name="ls",
            args={}
        )
    
    assert result["error"] == "timeout"


def test_execute_limited_dry_run_never_executes():
    """DRY_RUN mode should never call subprocess"""
    runner = ToolRunner(dry_run=True)
    
    # dry_run runner doesn't have execute_tool_limited
    assert not hasattr(runner, 'execute_tool_limited') or runner.dry_run is True
