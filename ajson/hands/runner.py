"""
Tool Runner: Executes tools with approval gates + audit logging

Expansion: JSON audit logs + PolicyDecision enforcement
"""
from typing import Dict, Any, List, Optional
import json
import os
import subprocess
from ajson.hands.fs_connector import FileSystemConnector
from ajson.hands.policy import (
    ApprovalPolicy,
    PolicyDecision,
   OperationCategory,
    ApprovalRequiredError,
    PolicyDeniedError,
    ApprovalRequired,  # Legacy compatibility
)


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
        self.policy = ApprovalPolicy()  # Initialize policy for execute_tool_limited
    
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
        # Legacy operation string format: "tool_name {args}"
        operation_str = f"{tool_name} {str(args)}"
        
        # Convert args to command-like string for pattern matching
        if isinstance(args, dict):
            args_str = " ".join(f"{k} {v}" if not k.startswith("-") else f"{k} {v}" for k, v in args.items())
            operation_cmd = f"{tool_name} {args_str}"
        else:
            operation_cmd = operation_str
        
        # Evaluate policy
        decision, category, reason = ApprovalPolicy.evaluate(operation_cmd, dry_run=self.dry_run)
        
        # Legacy compatibility: use check_approval_required for requires_approval field
        requires_approval, legacy_reason, gate_type = ApprovalPolicy.check_approval_required(operation_cmd, dry_run=self.dry_run)
        
        # Handle DENY (legacy: convert to ApprovalRequiredError ONLY for destructive/irreversible denylist items)
        if decision == PolicyDecision.DENY:
            # Network denials should always raise PolicyDeniedError
            if category == OperationCategory.NETWORK:
                error = PolicyDeniedError(operation_cmd, reason, category)
                self._log_audit(operation_str, decision, category, reason, error=str(error))
                raise error
            
            # Legacy behavior: destructive/irreversible denylist items raised ApprovalRequiredError
            if category in [OperationCategory.DESTRUCTIVE, OperationCategory.IRREVERSIBLE]:
                if not self.dry_run:
                    gate_map = {
                        OperationCategory.DESTRUCTIVE: ApprovalRequired.DESTRUCTIVE,
                        OperationCategory.IRREVERSIBLE: ApprovalRequired.IRREVERSIBLE,
                    }
                    error = ApprovalRequiredError(operation_str, reason, gate_map.get(category))
                    self._log_audit(operation_str, decision, category, reason, error=str(error))
                    raise error
                else:
                    # DRY_RUN mode: log but don't raise
                    self._log_audit(operation_str, decision, category, reason, result={"dry_run": True, "status": "blocked"})
                    return {"dry_run": True, "status": "blocked", "decision": decision.value, "category": category.value, "reason": reason, "requires_approval": requires_approval, "output": f"DRY_RUN: operation blocked: {reason}"}
            else:
                # Other denies (e.g., unknown category) raise PolicyDeniedError
                error = PolicyDeniedError(operation_cmd, reason, category)
                self._log_audit(operation_str, decision, category, reason, error=str(error))
                raise error
        
        # Handle REQUIRE_APPROVAL (non-dry-run)
        if decision == PolicyDecision.REQUIRE_APPROVAL and not self.dry_run:
            # Create approval request
            try:
                from ajson.hands.approval import get_approval_store
                store = get_approval_store()
                approval_request = store.create_request(
                    operation=operation_cmd,
                    category=category.value,
                    reason=reason,
                    metadata={"tool_name": tool_name, "args": args}
                )
                # Include request_id in exception for client to track
                gate_map = {
                    OperationCategory.DESTRUCTIVE: ApprovalRequired.DESTRUCTIVE,
                    OperationCategory.PAID: ApprovalRequired.PAID,
                    OperationCategory.IRREVERSIBLE: ApprovalRequired.IRREVERSIBLE,
                }
                gate_type = gate_map.get(category, None)
                error = ApprovalRequiredError(operation_str, f"{reason} (request_id: {approval_request.request_id})", gate_type)
                self._log_audit(operation_str, decision, category, reason, error=str(error), result={"approval_request_id": approval_request.request_id})
                raise error
            except ImportError:
                # Fallback if approval module not available
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
            # Special handling for M2 FS Tools
            if tool_name.endswith("_worktree"):
                result = self._execute_fs_tool(tool_name, args)
            else:
                result = self._execute_actual(tool_name, args, decision, category, reason)
        
        # Add legacy fields for backwards compatibility
        result["requires_approval"] = requires_approval
        if "output" not in result:
            result["output"] = result.get("output", f"DRY_RUN: {tool_name} with {json.dumps(args)}" if self.dry_run else f"EXECUTED: {tool_name}")
        
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
    
    def execute_tool_limited(self, grant_id: str, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with approval grant (LIMITED mode)
        
        Features:
        - Requires valid approval grant
        - Operation in ALLOWLIST only
        - NETWORK永続DENY (even with grant)
        
        Security:
        - Verifies grant before execution
        - Enforces subprocess restrictions (shell=False, timeout, cwd)
        """
        import subprocess
        
        # Verify grant
        from ajson.hands.approval import get_approval_store
        store = get_approval_store()
        
        operation_cmd = f"{tool_name} {args}"
        if not store.verify_grant(grant_id, operation_cmd):
            raise ValueError(f"Invalid or expired grant, or operation not in scope: {grant_id}")
        
        # Evaluate policy using correct API
        decision, category, reason = ApprovalPolicy.evaluate(operation_cmd, dry_run=False)
        
        # NETWORK永久DENY (even with approval)
        if category == OperationCategory.NETWORK:
            raise PolicyDeniedError(
                operation_cmd,
                "NETWORK operations永久DENY (policy override)",
                OperationCategory.NETWORK
            )
        
        # Check if operation is in allowlist
        is_in_allowlist = any(
            operation_cmd.lower().startswith(p.lower()) 
            for p in ApprovalPolicy.ALLOWLIST
        )
        
        if not is_in_allowlist:
            raise ValueError(
                f"Operation not in allowlist: {operation_cmd}",
            )
        
        # Execute with subprocess restrictions
        try:
            result = subprocess.run(
                [tool_name] + [str(v) for v in args.values()],
                capture_output=True,
                text=True,
                shell=False,  # Security: no shell injection
                timeout=10,   # Safety: prevent infinite hangs
                cwd="/tmp"    # Isolation: fixed working directory
            )
            
            return {
                "executed": True,
                "tool": tool_name,
                "args": args,
                "grant_id": grant_id,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            error_data = {"error": "timeout", "grant_id": grant_id}
            self._log_audit(f"{tool_name} {args}", decision, category, reason, error="timeout", result=error_data)
            return error_data
    
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

    def _execute_fs_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute File System Connector tools for M2"""
        # In a real implementation, worktree_root would come from context
        # For MVP, we use a default or task-specific one if provided
        worktree_root = args.get("worktree_root", "worktrees/default")
        connector = FileSystemConnector(worktree_root)
        
        try:
            if tool_name == "ls_worktree":
                out = connector.list_dir(args.get("path", "."))
                msg = f"Files: {out}"
            elif tool_name == "read_worktree":
                out = connector.read_file(args.get("path"))
                msg = f"Content of {args.get('path')}:\n{out}"
            elif tool_name == "write_worktree":
                connector.write_file(args.get("path"), args.get("content", ""))
                msg = f"Wrote to {args.get('path')}"
            elif tool_name == "mkdir_worktree":
                connector.mkdir(args.get("path"))
                msg = f"Created directory {args.get('path')}"
            elif tool_name == "move_worktree":
                connector.move(args.get("src"), args.get("dst"))
                msg = f"Moved {args.get('src')} to {args.get('dst')}"
            elif tool_name == "remove_worktree":
                connector.remove(args.get("path"), permanent=args.get("permanent", False))
                msg = f"Removed {args.get('path')} (permanent={args.get('permanent', False)})"
            else:
                raise ValueError(f"Unknown FS tool: {tool_name}")
                
            return {
                "executed": True,
                "tool": tool_name,
                "output": msg,
                "status": "success"
            }
        except Exception as e:
            return {
                "executed": False,
                "tool": tool_name,
                "error": str(e),
                "status": "error"
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
