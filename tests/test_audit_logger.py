"""
Tests for audit logger
"""
import pytest
import json
import tempfile
from pathlib import Path
from ajson.hands.audit_logger import AuditLogger


def test_audit_logger_initialization():
    """Logger creates log directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        assert Path(tmpdir).exists()


def test_log_request_created():
    """Log approval request creation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_request_created(
            request_id="req-123",
            operation="ls -la",
            category="readonly",
            reason="test"
        )
        
        # Verify log file exists and contains event
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        assert len(log_files) == 1
        
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert len(events) == 1
        assert events[0]["event_type"] == "approval_request_created"
        assert events[0]["request_id"] == "req-123"
        assert events[0]["operation"] == "ls -la"


def test_log_approval_granted():
    """Log approval grant"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_request_approved(
            request_id="req-123",
            grant_id="grant-456",
            scope=["ls", "git"],
            ttl_seconds=300,
            decided_by="admin"
        )
        
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert events[0]["event_type"] == "approval_granted"
        assert events[0]["grant_id"] == "grant-456"
        assert events[0]["scope"] == ["ls", "git"]


def test_log_denial():
    """Log approval denial"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_request_denied(
            request_id="req-123",
            reason="Too risky",
            decided_by="admin"
        )
        
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert events[0]["event_type"] == "approval_denied"
        assert events[0]["reason"] == "Too risky"


def test_log_grant_verification():
    """Log grant verification"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_grant_verification(
            grant_id="grant-456",
            operation="ls -la",
            valid=True
        )
        
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert events[0]["event_type"] == "grant_verification"
        assert events[0]["valid"] is True


def test_log_execution():
    """Log tool execution"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_execution(
            grant_id="grant-456",
            tool="ls",
            args={"-la": True},
            result="success",
            returncode=0
        )
        
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert events[0]["event_type"] == "tool_execution"
        assert events[0]["result"] == "success"
        assert events[0]["returncode"] == 0


def test_log_security_violation():
    """Log security violation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_security_violation(
            violation_type="network_deny",
            details="Attempted network access with grant",
            context={"operation": "curl https://example.com"}
        )
        
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert events[0]["event_type"] == "security_violation"
        assert events[0]["violation_type"] == "network_deny"


def test_multiple_events():
    """Log multiple events in sequence"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)
        
        logger.log_request_created("req-1", "ls", "readonly", "test")
        logger.log_request_approved("req-1", "grant-1", ["ls"], 300, "admin")
        logger.log_execution("grant-1", "ls", {}, "success", 0)
        
        log_files = list(Path(tmpdir).glob("audit_*.jsonl"))
        with open(log_files[0]) as f:
            events = [json.loads(line) for line in f]
        
        assert len(events) == 3
        assert events[0]["event_type"] == "approval_request_created"
        assert events[1]["event_type"] == "approval_granted"
        assert events[2]["event_type"] == "tool_execution"
