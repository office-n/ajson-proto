"""
Approval Policy: Defines which operations require approval
"""
from typing import List, Tuple
from enum import Enum


class ApprovalRequired(Enum):
    """Operations that require approval"""
    DESTRUCTIVE = "destructive"  # File deletion, git force, db drop
    PAID = "paid"  # External API calls with billing
    IRREVERSIBLE = "irreversible"  # Main merge, tag, release


class ApprovalRequiredError(Exception):
    """Raised when an operation requires approval"""
    def __init__(self, operation: str, reason: str, gate_type: ApprovalRequired):
        self.operation = operation
        self.reason = reason
        self.gate_type = gate_type
        super().__init__(f"Approval required for {operation}: {reason}")


class ApprovalPolicy:
    """
    Policy engine for approval gates
    
    Determines which operations require approval based on:
    - Operation type (delete, external call, etc.)
    - Target (file, branch, resource)
    - Context (environment, dry_run flag)
    """
    
    # Destructive patterns
    DESTRUCTIVE_PATTERNS = [
        r"rm\s+-rf",
        r"git\s+push\s+.*--force",
        r"git\s+reset\s+--hard",
        r"docker\s+rm",
        r"DROP\s+DATABASE",
    ]
    
    # Paid API patterns
    PAID_API_PATTERNS = [
        r"openai\.ChatCompletion",
        r"anthropic\.Completion",
        r"gemini\.generate",
    ]
    
    # Irreversible patterns
    IRREVERSIBLE_PATTERNS = [
        r"git\s+merge\s+.*main",
        r"git\s+tag\s+-a",
        r"npm\s+publish",
    ]
    
    @classmethod
    def check_approval_required(cls, operation: str, dry_run: bool = True) -> Tuple[bool, str, ApprovalRequired]:
        """
    Check if operation requires approval
        
        Args:
            operation: Command or operation string
            dry_run: If True, no actual execution (scaffold default)
            
        Returns:
            (requires_approval, reason, gate_type)
        """
        import re
        
        # DRY_RUN scaffold: all operations are allowed (no real execution)
        if dry_run:
            return (False, "DRY_RUN mode: no actual execution", None)
        
        # Check destructive
        for pattern in cls.DESTRUCTIVE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return (True, f"Destructive operation detected: {pattern}", ApprovalRequired.DESTRUCTIVE)
        
        # Check paid
        for pattern in cls.PAID_API_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return (True, f"Paid API call detected: {pattern}", ApprovalRequired.PAID)
        
        # Check irreversible
        for pattern in cls.IRREVERSIBLE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return (True, f"Irreversible operation detected: {pattern}", ApprovalRequired.IRREVERSIBLE)
        
        return (False, "Operation allowed", None)
