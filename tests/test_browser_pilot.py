"""
Tests for ajson.hands.browser_pilot (no network, all local)
"""
import pytest
from ajson.hands.browser_pilot import BrowserPilot


def test_browser_pilot_dry_run_default():
    """BrowserPilot should default to DRY_RUN mode"""
    pilot = BrowserPilot()
    assert pilot.dry_run is True


def test_browser_pilot_navigate():
    """Navigate should return simulated result in DRY_RUN"""
    pilot = BrowserPilot(dry_run=True)
    result = pilot.navigate("https://example.com")
    
    assert result["action"] == "navigate"
    assert result["dry_run"] is True
    assert result["status"] == "simulated"
    assert "example.com" in result["url"]


def test_browser_pilot_click():
    """Click should return simulated result in DRY_RUN"""
    pilot = BrowserPilot(dry_run=True)
    result = pilot.click("#submit-button")
    
    assert result["action"] == "click"
    assert result["selector"] == "#submit-button"
    assert result["dry_run"] is True
    assert result["status"] == "simulated"


def test_browser_pilot_type_text():
    """Type should return simulated result with masked secrets"""
    pilot = BrowserPilot(dry_run=True)
    result = pilot.type_text("#password", "sk-1234567890abcdefghijklmnopqrstuvwxyz")
    
    assert result["action"] == "type"
    assert result["selector"] == "#password"
    assert "sk-***MASKED***" in result["text"]
    assert "1234567890" not in result["text"]


def test_browser_pilot_audit_log():
    """Audit log should record all actions"""
    pilot = BrowserPilot(dry_run=True)
    pilot.navigate("https://example.com")
    pilot.click("#button")
    pilot.type_text("#input", "test")
    
    log = pilot.get_audit_log()
    assert len(log) == 3
    assert log[0]["action"] == "navigate"
    assert log[1]["action"] == "click"
    assert log[2]["action"] == "type"


def test_browser_pilot_secret_masking():
    """Secret masking should mask API keys and passwords"""
    pilot = BrowserPilot()
    
    # Test API key masking
    masked = pilot._mask_secrets("sk-1234567890abcdefghijklmnopqrstuvwxyz")
    assert "sk-***MASKED***" in masked
    assert "1234567890" not in masked
    
    # Test password masking
    masked = pilot._mask_secrets("password=mysecretpass")
    assert "password=***MASKED***" in masked
    assert "mysecretpass" not in masked
