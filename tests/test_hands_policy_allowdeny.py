"""
Tests for Hands Policy: allowlist/denylist + PolicyDecision (minimal core tests)
"""
import pytest
from ajson.hands.policy import (
    ApprovalPolicy,
    PolicyDecision,
    OperationCategory,
)


def test_policy_allowlist():
    """Allowlist operations should be ALLOW"""
    decision, category, reason = ApprovalPolicy.evaluate("ls -la", dry_run=True)
    assert decision == PolicyDecision.ALLOW
    assert category == OperationCategory.READONLY


def test_policy_denylist():
    """Denylist operations should be DENY"""
    decision, category, reason = ApprovalPolicy.evaluate("rm -rf /", dry_run=True)
    assert decision == PolicyDecision.DENY


def test_policy_network_denied():
    """Network operations should be DENY"""
    decision, category, reason = ApprovalPolicy.evaluate("curl https://example.com", dry_run=True)
    assert decision == PolicyDecision.DENY
    assert category == OperationCategory.NETWORK


def test_policy_unknown_dry_run():
    """Unknown operations in DRY_RUN should be DRY_RUN_ONLY"""
    decision, category, _ = ApprovalPolicy.evaluate("unknown_command", dry_run=True)
    assert decision == PolicyDecision.DRY_RUN_ONLY
    assert category == OperationCategory.UNKNOWN
