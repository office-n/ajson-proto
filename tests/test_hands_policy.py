"""
Tests for ajson.hands.policy (no network, all local)
"""
import pytest
from ajson.hands.policy import ApprovalPolicy, ApprovalRequired, ApprovalRequiredError


def test_approval_policy_dry_run():
    """DRY_RUN mode should allow all operations"""
    requires, reason, gate = ApprovalPolicy.check_approval_required("rm -rf /foo", dry_run=True)
    assert requires is False
    assert "DRY_RUN" in reason
    assert gate is None


def test_approval_policy_destructive():
    """Destructive operations should require approval (when not dry_run)"""
    requires, reason, gate = ApprovalPolicy.check_approval_required("rm -rf /foo", dry_run=False)
    assert requires is True
    assert "Destructive" in reason
    assert gate == ApprovalRequired.DESTRUCTIVE


def test_approval_policy_paid():
    """Paid API calls should require approval (when not dry_run)"""
    requires, reason, gate = ApprovalPolicy.check_approval_required("openai.ChatCompletion.create()", dry_run=False)
    assert requires is True
    assert "Paid" in reason
    assert gate == ApprovalRequired.PAID


def test_approval_policy_irreversible():
    """Irreversible operations should require approval (when not dry_run)"""
    requires, reason, gate = ApprovalPolicy.check_approval_required("git merge origin/main", dry_run=False)
    assert requires is True
    assert "Irreversible" in reason
    assert gate == ApprovalRequired.IRREVERSIBLE


def test_approval_policy_safe_operation():
    """Safe operations should not require approval"""
    requires, reason, gate = ApprovalPolicy.check_approval_required("git status", dry_run=False)
    assert requires is False
    assert "allowed" in reason
    assert gate is None


def test_approval_required_error():
    """ApprovalRequiredError should contain operation details"""
    error = ApprovalRequiredError("rm -rf /foo", "Destructive", ApprovalRequired.DESTRUCTIVE)
    assert "rm -rf /foo" in str(error)
    assert error.gate_type == ApprovalRequired.DESTRUCTIVE
