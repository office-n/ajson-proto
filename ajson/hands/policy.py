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
    
    # Allowlist: safe, readonly operations that don't require approval
    ALLOWLIST = [
        # File operations (readonly)
        "ls", "cat", "grep", "rg", "find",
        # Testing
        "pytest -q", "pytest --collect-only",
        # Git readonly (support both "git status" and "git_status" forms)
        "git status", "git log", "git diff", "git show",
        "git_status",  # Legacy test format
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
        r"git\s+merge",  # Matches any "git merge" command
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
            dry_run: If True, no actual execution (scaffold default)
            
        Returns:
            (PolicyDecision, OperationCategory, reason)
        """
        import re
        operation_lower = operation.lower()
        
        # 1. Check allowlist first (highest priority)
        # Use strict matching to avoid false positives (e.g., "git status" shouldn't match "git merge origin/main")
        for pattern in cls.ALLOWLIST:
            pattern_lower = pattern.lower()
            # Match if operation starts with pattern (exact command match)
            if operation_lower.startswith(pattern_lower):
                # Check that it's followed by space or end of string
                if len(operation_lower) == len(pattern_lower) or operation_lower[len(pattern_lower)] in [' ', '\t', '\n']:
                    return (PolicyDecision.ALLOW, OperationCategory.READONLY, f"Allowed: matches allowlist")
        
        # 2. Check denylist (immediate denial)
        for pattern in cls.DENYLIST:
            if pattern.lower() in operation_lower:
                # Determine if destructive or irreversible based on pattern
                if any(p in operation_lower for p in ["rm -rf", "drop database", "drop table"]):
                    return (PolicyDecision.DENY, OperationCategory.DESTRUCTIVE, f"Destructive: matches denylist pattern '{pattern}'")
                else:
                    return (PolicyDecision.DENY, OperationCategory.IRREVERSIBLE, f"Denied: matches denylist pattern '{pattern}'")
        
        # 3. Check network patterns (denied)
        for pattern in cls.NETWORK_PATTERNS:
            if pattern.lower() in operation_lower:
                return (PolicyDecision.DENY, OperationCategory.NETWORK, f"Denied: network operation")
        
        # 4. Check destructive patterns (require approval when not dry_run)
        for pattern in cls.DESTRUCTIVE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE): # Use re.search for regex patterns
                if dry_run:
                    return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.DESTRUCTIVE, f"Destructive: simulation only in DRY_RUN")
                else:
                    return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.DESTRUCTIVE, f"Destructive: requires approval")
        
        # 5. Check paid patterns (require approval when not dry_run)
        for pattern in cls.PAID_API_PATTERNS: # Corrected to PAID_API_PATTERNS
            if re.search(pattern, operation, re.IGNORECASE): # Use re.search for regex patterns
                if dry_run:
                    return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.PAID, f"Paid API: simulation only in DRY_RUN")
                else:
                    return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.PAID, f"Paid API: requires approval")
        
        # 6. Check irreversible patterns (require approval when not dry_run)
        for pattern in cls.IRREVERSIBLE_PATTERNS:
            if re.search(pattern, operation, re.IGNORECASE): # Use re.search for regex patterns
                if dry_run:
                    return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.IRREVERSIBLE, f"Irreversible: simulation only in DRY_RUN")
                else:
                    return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.IRREVERSIBLE, f"Irreversible: requires approval")
        
        # 7. Unknown operations: allow in dry_run, require approval otherwise
        if dry_run:
            return (PolicyDecision.DRY_RUN_ONLY, OperationCategory.UNKNOWN, f"Unknown operation: DRY_RUN only")
        else:
            return (PolicyDecision.REQUIRE_APPROVAL, OperationCategory.UNKNOWN, f"Unknown operation: requires approval")
    
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
        # Legacy behavior: DRY_RUN always returns (False, "DRY_RUN mode...", None)
        if dry_run:
            return (False, "DRY_RUN mode: no actual execution", None)
        
        decision, category, reason = cls.evaluate(operation, dry_run=False)
        
        # Legacy behavior: DENY operations return (True, reason, DESTRUCTIVE/IRREVERSIBLE)
        # because denylist includes destructive/irreversible patterns
        if decision == PolicyDecision.DENY:
            # Map category to legacy ApprovalRequired
            if category == OperationCategory.DESTRUCTIVE or category == OperationCategory.NETWORK:
                return (True, reason, ApprovalRequired.DESTRUCTIVE)
            elif category == OperationCategory.IRREVERSIBLE:
                return (True, reason, ApprovalRequired.IRREVERSIBLE)
            else:
                return (True, reason, None)
        
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
        
        # ALLOW or DRY_RUN_ONLY (in non-dry-run context)
        # Legacy: ALLOW operations return (False, "...allowed...", None)
        if decision == PolicyDecision.ALLOW:
            return (False, "Operation allowed", None)
        
        # For unknown operations in non-dry-run, legacy behavior was to allow
        return (False, "Operation allowed", None)
