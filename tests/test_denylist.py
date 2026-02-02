"""
Test denylist enforcement
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ajson.tools import runner


def test_denylist_blocks_rm():
    """Test: 'rm' command is blocked"""
    success, result, error = runner.run_tool("rm -rf /tmp/test")
    assert not success
    assert "BLOCKED" in result
    assert "rm" in error.lower()


def test_denylist_blocks_sudo():
    """Test: 'sudo' command is blocked"""
    success, result, error = runner.run_tool("sudo apt update")
    assert not success
    assert "BLOCKED" in result
    assert "sudo" in error.lower()


def test_denylist_blocks_chmod():
    """Test: 'chmod' command is blocked"""
    success, result, error = runner.run_tool("chmod 777 /etc/passwd")
    assert not success
    assert "BLOCKED" in result
    assert "chmod" in error.lower()


def test_denylist_blocks_delete():
    """Test: 'delete' keyword is blocked"""
    success, result, error = runner.run_tool("delete database tables")
    assert not success
    assert "BLOCKED" in result


def test_denylist_blocks_curl():
    """Test: 'curl' command is blocked"""
    success, result, error = runner.run_tool("curl https://example.com")
    assert not success
    assert "BLOCKED" in result
    assert "curl" in error.lower()


def test_allowlist_accepts_echo():
    """Test: 'echo' command is allowed"""
    success, result, error = runner.run_tool("echo 'Hello World'")
    assert success
    assert error is None


def test_allowlist_accepts_ls():
    """Test: 'ls' command is allowed"""
    success, result, error = runner.run_tool("ls")
    assert success
    assert error is None


def test_allowlist_accepts_python():
    """Test: 'python3' command is allowed"""
    success, result, error = runner.run_tool("python3 --version")
    # Note: python3 might not exist in all environments, so we accept either success or specific error
    if not success:
        # It's OK if python3 is not found, as long as it wasn't blocked by denylist
        assert "allowlist" not in result.lower() or "not found" in result.lower() or "no such" in result.lower()


def test_allowlist_rejects_unlisted():
    """Test: Unlisted commands are rejected"""
    success, result, error = runner.run_tool("unlisted_command")
    assert not success
    assert "allowlist" in result.lower()


def test_approval_gate_detection_deploy():
    """Test: Detect 'deploy' keyword"""
    gates = runner.detect_approval_gates("Deploy application to production")
    assert "deploy" in gates


def test_approval_gate_detection_delete():
    """Test: Detect 'delete' keyword"""
    gates = runner.detect_approval_gates("Delete old database records")
    assert "delete" in gates


def test_approval_gate_detection_database():
    """Test: Detect database operations"""
    gates = runner.detect_approval_gates("CREATE TABLE users")
    assert "database" in gates


def test_approval_gate_detection_external():
    """Test: Detect external/public keywords"""
    gates = runner.detect_approval_gates("Make API public for external access")
    assert "external" in gates


def test_approval_gate_detection_none():
    """Test: No gates for safe operations"""
    gates = runner.detect_approval_gates("Run pytest tests")
    assert len(gates) == 0
