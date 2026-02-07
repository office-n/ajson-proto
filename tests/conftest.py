import pytest
import logging
from ajson.hands.approval import ApprovalStore
import ajson.hands.approval
from ajson.hands.audit_logger import AuditLogger
import ajson.hands.audit_logger
from ajson.hands.screenshot_evidence import ScreenshotEvidence
import ajson.hands.screenshot_evidence

@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state between tests to prevent side effects"""
    
    # 1. Reset ApprovalStore
    original_store = ajson.hands.approval._global_store
    ajson.hands.approval._global_store = ApprovalStore()
    
    # 2. Reset AuditLogger (clear handlers and global instance)
    logger = logging.getLogger("ajson.audit")
    for h in logger.handlers[:]:
        logger.removeHandler(h)
        h.close()
    ajson.hands.audit_logger._audit_logger = None
    
    # 3. Reset ScreenshotEvidence
    ajson.hands.screenshot_evidence._screenshot_evidence = None
    
    yield
    
    # Restore original store (optional, mainly for safety)
    ajson.hands.approval._global_store = original_store
