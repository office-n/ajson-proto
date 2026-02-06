"""
Tests for BrowserPilot: DRY_RUN planning (minimal core tests)
"""
import pytest
import json
from ajson.hands.browser_pilot import BrowserPilot, BrowserStep, BrowserAction


def test_browserpilot_dry_run():
    """DRY_RUN should return execution plan"""
    pilot = BrowserPilot(dry_run=True)
    steps = [
        BrowserStep(BrowserAction.NAVIGATE, {"url": "http://localhost:8000"}),
        BrowserStep(BrowserAction.CLICK, {"selector": "#button"}),
    ]
    
    result = pilot.run(steps)
    assert result["dry_run"] == True
    assert result["total_steps"] == 2


def test_browserpilot_audit_log_json():
    """Audit log should be JSON-serializable"""
    pilot = BrowserPilot(dry_run=True)
    steps = [BrowserStep(BrowserAction.NAVIGATE, {"url": "http://localhost:8000"})]
    
    pilot.run(steps)
    audit_json = pilot.get_audit_log_json()
    parsed = json.loads(audit_json)
    assert len(parsed) == 1


def test_browserpilot_secret_masking():
    """Secrets should be masked"""
    pilot = BrowserPilot(dry_run=True)
    steps = [
        BrowserStep(BrowserAction.TYPE, {
            "selector": "#api-key",
            "text": "sk-1234567890abcdefghijklmnopqrstuvwxyz"
        }),
    ]
    
    pilot.run(steps)
    audit = pilot.get_audit_log()
    assert "***MASKED***" in str(audit[0]["params"]["text"])
