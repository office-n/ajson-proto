"""
Tool Runner: Execute tools with approval gates

Expansion: Stable audit logging + policy integration
"""
from typing import Dict, Any, List, Optional
from ajson.hands.policy import (
    ApprovalPolicy,
    PolicyDecision,
    OperationCategory,
    ApprovalRequiredError,
    PolicyDeniedError,
)
import json


class ToolRunner:
    """
    Tool Runner with approval gates and stable audit logging
    
    Expansion: Policy integration + JSON-serializable audit log
    """
    
    def __init__(self, dry_run: bool = True):
        """
        Initialize ToolRunner
        
        Args:
            dry_run: If True, no actual execution (scaffold default)
        """
        self.dry_run = dry_run
        self.audit_log: List[Dict[str, Any]] = []
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with approval gates
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            
        Returns:
            Execution result with audit log
            
        Raises:
            ApprovalRequiredError: If operation requires approval and dry_run is False
            PolicyDeniedError: If operation is denied by policy
        """
        operation_str = f"{tool_name} {json.dumps(args)}"
        
        # Convert args to command-like string for pattern matching
        if isinstance(args, dict):
            args_str = " ".join(f"{k} {v}" if not k.startswith("-") else f"{k} {v}" for k, v in args.items())
            operation_cmd = f"{tool_name} {args_str}"
        else:
            operation_cmd = operation_str
        
        # Evaluate policy
        decision, category, reason = ApprovalPolicy.evaluate(operation_cmd, dry_run=self.dry_run)
        
        # Handle DENY
        if decision == PolicyDecision.DENY:
            error = PolicyDeniedError(operation_cmd, reason, category)
            self._log_audit(operation_str, decision, category, reason, error=str(error))
            raise error
        
        # Handle REQUIRE_APPROVAL (non-dry-run)
        if decision == PolicyDecision.REQUIRE_APPROVAL and not self.dry_run:
            # Map category to legacy ApprovalRequired for backward compatibility
            from ajson.hands.policy import ApprovalRequired
            gate_map = {
                OperationCategory.DESTRUCTIVE: ApprovalRequired.DESTRUCTIVE,
                OperationCategory.PAID: ApprovalRequired.PAID,
                OperationCategory.IRREVERSIBLE: ApprovalRequired.IRREVERSIBLE,
            }
            gate_type = gate_map.get(category, None)
            error = ApprovalRequiredError(operation_str, reason, gate_type)
            self._log_audit(operation_str, decision, category, reason, error=str(error))
            raise error
        
        # Execute (or simulate)
        if self.dry_run or decision == PolicyDecision.DRY_RUN_ONLY:
            result = self._simulate_execution(tool_name, args, decision, category, reason)
        else:
            # ALLOW: actual execution would happen here
            result = self._execute_actual(tool_name, args, decision, category, reason)
        
        # Log audit
        self._log_audit(operation_str, decision, category, reason, result=result)
        
        return result
    
    def _simulate_execution(
        self,
        tool_name: str,
        args: Dict[str, Any],
        decision: PolicyDecision,
        category: OperationCategory,
        reason: str
    ) -> Dict[str, Any]:
        """Simulate execution (DRY_RUN)"""
        return {
            "tool_name": tool_name,
            "args": args,
            "dry_run": True,
            "decision": decision.value,
            "category": category.value,
            "reason": reason,
            "status": "simulated",
            "output": f"DRY_RUN: {tool_name} with {json.dumps(args)}"
        }
    
    def _execute_actual(
        self,
        tool_name: str,
        args: Dict[str, Any],
        decision: PolicyDecision,
        category: OperationCategory,
        reason: str
    ) -> Dict[str, Any]:
        """Execute actual operation (ALLOW in non-dry-run)"""
        # Real execution would happen here
        # For now, return placeholder
        return {
            "tool_name": tool_name,
            "args": args,
            "dry_run": False,
            "decision": decision.value,
            "category": category.value,
            "reason": reason,
            "status": "executed",
            "output": f"EXECUTED: {tool_name} with {json.dumps(args)}"
        }
    
    def _log_audit(
        self,
        operation: str,
        decision: PolicyDecision,
        category: OperationCategory,
        reason: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Log audit entry (JSON-serializable)"""
        entry = {
            "operation": operation,
            "decision": decision.value,
            "category": category.value,
            "reason": reason,
            "dry_run": self.dry_run,
        }
        
        if result:
            entry["result"] = result
        
        if error:
            entry["error"] = error
        
        self.audit_log.append(entry)
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log (JSON-serializable)"""
        return self.audit_log
    
    def get_audit_log_json(self) -> str:
        """Get audit log as JSON string"""
        return json.dumps(self.audit_log, indent=2)
