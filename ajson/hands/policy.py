"""
Approval Policy: Defines which operations require approval

Expansion: allowlist/denylist + explicit policy decisions
"""
from typing import Tuple, Optional
from enum import Enum


class PolicyDecision(Enum):
    """Policy decision for an operation"""
    ALLOW = "allow"  # Safe readonly operation, execute immediately
    DRY_RUN_ONLY = "dry_run_only"  # Can simulate but not execute
    REQUIRE_APPROVAL = "require_approval"  # Needs explicit approval before execution
    DENY = "deny"  # Forbidden operation, never execute


class OperationCategory(Enum):
    """Category of operation based on risk"""
    READONLY = "readonly"  # Read-only, no state change
    DESTRUCTIVE = "destructive"  # Deletes/modifies data
    IRREVERSIBLE = "irreversible"  # Cannot be undone
    PAID = "paid"  # External API with billing
    NETWORK = "network"  # External network call
    UNKNOWN = "unknown"  # Cannot classify


class ApprovalRequired(Enum):
    """Operations that require approval (legacy compatibility)"""
    DESTRUCTIVE = "destructive"
    PAID = "paid"
    IRREVERSIBLE = "irreversible"


class ApprovalRequiredError(Exception):
    """Raised when an operation requires approval"""
    def __init__(self, operation: str, reason: str, gate_type: ApprovalRequired):
        self.operation = operation
        self.reason = reason
        self.gate_type = gate_type
        super().__init__(f"Approval required for {operation}: {reason}")


class PolicyDeniedError(Exception):
    """Raised when an operation is denied by policy"""
    def __init__(self, operation: str, reason: str, category: OperationCategory):
        self.operation = operation
        self.reason = reason
        self.category = category
        super().__init__(f"Operation denied: {operation} ({reason})")


class ApprovalPolicy:
    """
    Policy engine for approval gates
    
    Expansion: allowlist/denylist + explicit policy decisions
    """
    
    # Allowlist: Safe readonly operations
    ALLOWLIST = [
        "ls",
        "cat",
        "grep",
        "rg",
        "find",
        "pytest -q",
        "pytest --collect-only",
        "git status",
        "git log",
        "git diff",
    ]
    
    # Denylist: Forbidden operations
    DENYLIST = [
        "rm -rf",
        "git push --force",
        "git push -f",
        "git tag -d",
        "git reset --hard",
        "docker rm",
        "DROP DATABASE",
        "DROP TABLE",
        "curl",
        "wget",
        "nc ",
        "telnet",
    ]
    
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
    
    # Network patterns
    NETWORK_PATTERNS = [
        r"curl\s+",
        r"wget\s+",
        r"http://",
        r"https://",
        r"requests\.",
        r"urllib\.",
    ]
    
    @classmethod
    def evaluate(cls, operation: str, dry_run: bool = True) -> Tuple[PolicyDecision, OperationCategory, str]:
        """
        Evaluate operation and return policy decision
        
        Args:
            operation: Command or operation string
            dry_run: If True, DRY_RUN context (scaffold default)
            
        Returns:
            (decision, category, reason)
        """
        import re
        
        # Normalize operation
        op_normalized = cls._normalize_operation(operation)
        
        # Check denylist first
        for denied_pattern in cls.DENYLIST:
            if denied_pattern.lower() in op_normalized.lower():
                category = cls._classify_category(operation)
                return (PolicyDecision.DENY, category, f"Denied: matches denylist pattern '{denied_pattern}'")
        
        # Check allowlist
        for allowed_pattern in cls.ALLOWLIST:
            if allowed_pattern.lower() in op_normalized.lower():
                return (PolicyDecision.ALLOW, OperationCategory.READONLY, "Allowed: matches allowlist")
        
        # Check destructive
        for pattern in cls.DESTRUCTIVE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                if dry_run:
                    return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.DESTRUCTIVE, "DRY_RUN: destructive operation")
                return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.DESTRUCTIVE, f"Destructive operation: {pattern}")
        
        # Check paid
        for pattern in cls.PAID_API_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                if dry_run:
                    return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.PAID, "DRY_RUN: paid API call")
                return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.PAID, f"Paid API call: {pattern}")
        
        # Check irreversible
        for pattern in cls.IRREVERSIBLE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                if dry_run:
                    return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.IRREVERSIBLE, "DRY_RUN: irreversible operation")
                return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.IRREVERSIBLE, f"Irreversible operation: {pattern}")
        
        # Check network
        for pattern in cls.NETWORK_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return (PolicyDecision.DENY, OperationCategory.NETWORK, f"Network operation denied: {pattern}")
        
        # Unknown operation
        if dry_run:
            return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.UNKNOWN, "DRY_RUN: unknown operation")
        return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.UNKNOWN, "Unknown operation requires approval")
    
    @classmethod
    def _normalize_operation(cls, operation: str) -> str:
        """Normalize operation for matching"""
        # Remove extra whitespace
        return " ".join(operation.split())
    
    @classmethod
    def _classify_category(cls, operation: str) -> OperationCategory:
        """Classify operation into category"""
        import re
        
        for pattern in cls.DESTRUCTIVE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return OperationCategory.DESTRUCTIVE
        
        for pattern in cls.PAID_API_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return OperationCategory.PAID
        
        for pattern in cls.IRREVERSIBLE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return OperationCategory.IRREVERSIBLE
        
        for pattern in cls.NETWORK_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE):
                return OperationCategory.NETWORK
        
        return OperationCategory.UNKNOWN
    
    @classmethod
    def check_approval_required(cls, operation: str, dry_run: bool = True) -> Tuple[bool, str, Optional[ApprovalRequired]]:
        """
        Check if operation requires approval (legacy compatibility)
        
        Args:
            operation: Command or operation string
            dry_run: If True, no actual execution (scaffold default)
            
        Returns:
            (requires_approval, reason, gate_type)
        """
        decision, category, reason = cls.evaluate(operation, dry_run)
        
        if decision == PolicyDecision.DENY:
            # Denied operations are not "approval required", they are forbidden
            return (False, reason, None)
        
        if decision == PolicyDecision.REQUIRE_APPROVAL:
            # Map category to legacy ApprovalRequired
            if category == OperationCategory.DESTRUCTIVE:
                return (True, reason, ApprovalRequired.DESTRUCTIVE)
            elif category == OperationCategory.PAID:
                return (True, reason, ApprovalRequired.PAID)
            elif category == OperationCategory.IRREVERSIBLE:
                return (True, reason, ApprovalRequired.IRREVERSIBLE)
            else:
                return (True, reason, None)
        
        # ALLOW or DRY_RUN_ONLY
        return (False, reason, None)
