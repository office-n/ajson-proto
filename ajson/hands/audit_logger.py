"""
Enhanced audit logging for approval workflow

Provides structured logging for:
- Approval request creation
- Grant issuance
- Denial decisions  
- Grant verification attempts
- Execution with grants
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class AuditLogger:
    """Structured audit logger for approval workflow"""
    
    def __init__(self, log_dir: str = "data/audit"):
        """
        Initialize audit logger
        
        Args:
            log_dir: Directory for audit logs (relative path)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger("ajson.audit")
        self.logger.setLevel(logging.INFO)
        
        # File handler (daily rotation)
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)
        
        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        else:
            # Clear existing handlers to prevent duplication/leaks in tests
            for h in self.logger.handlers[:]:
                self.logger.removeHandler(h)
                h.close()
            self.logger.addHandler(handler)
    
    def _log(self, event_type: str, data: Dict[str, Any]):
        """Log audit event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            **data
        }
        self.logger.info(json.dumps(event))
    
    def log_request_created(self, request_id: str, operation: str, category: str, reason: str):
        """Log approval request creation"""
        self._log("approval_request_created", {
            "request_id": request_id,
            "operation": operation,
            "category": category,
            "reason": reason
        })
    
    def log_request_approved(self, request_id: str, grant_id: str, scope: list, ttl_seconds: int, decided_by: str):
        """Log request approval and grant issuance"""
        self._log("approval_granted", {
            "request_id": request_id,
            "grant_id": grant_id,
            "scope": scope,
            "ttl_seconds": ttl_seconds,
            "decided_by": decided_by
        })
    
    def log_request_denied(self, request_id: str, reason: str, decided_by: str):
        """Log request denial"""
        self._log("approval_denied", {
            "request_id": request_id,
            "reason": reason,
            "decided_by": decided_by
        })
    
    def log_grant_verification(self, grant_id: str, operation: str, valid: bool, reason: Optional[str] = None):
        """Log grant verification attempt"""
        self._log("grant_verification", {
            "grant_id": grant_id,
            "operation": operation,
            "valid": valid,
            "reason": reason
        })
    
    def log_execution(self, grant_id: str, tool: str, args: Dict[str, Any], result: str, returncode: Optional[int] = None):
        """Log tool execution with grant"""
        self._log("tool_execution", {
            "grant_id": grant_id,
            "tool": tool,
            "args": args,
            "result": result,
            "returncode": returncode
        })
    
    def log_security_violation(self, violation_type: str, details: str, context: Dict[str, Any]):
        """Log security policy violation"""
        self._log("security_violation", {
            "violation_type": violation_type,
            "details": details,
            "context": context
        })


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
