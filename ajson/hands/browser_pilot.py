"""
BrowserPilot: Browser automation with DRY_RUN planning

Expansion: BrowserStep abstraction + plan-based execution
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json


class BrowserAction(Enum):
    """Browser action types"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCREENSHOT = "screenshot"
    WAIT = "wait"
    SCROLL = "scroll"


@dataclass
class BrowserStep:
    """
    Browser step abstraction
    
    Represents a single browser action with parameters
    """
    action: BrowserAction
    params: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action.value,
            "params": self.params
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrowserStep":
        """Create from dictionary"""
        return cls(
            action=BrowserAction(data["action"]),
            params=data["params"]
        )


class BrowserPilot:
    """
    BrowserPilot with approval gates and DRY_RUN planning
    
    Expansion: Step-based planning + optional Playwright driver
    """
    
    def __init__(self, dry_run: bool = True, headless: bool = True):
        """
        Initialize BrowserPilot
        
        Args:
            dry_run: If True, only plan execution (no actual browser)
            headless: Browser headless mode (ignored in DRY_RUN)
        """
        self.dry_run = dry_run
        self.headless = headless
        self.audit_log: List[Dict[str, Any]] = []
        self.screenshots: List[str] = []
        self._driver = None
    
    def run(self, steps: List[BrowserStep]) -> Dict[str, Any]:
        """
        Run browser automation plan
        
        Args:
            steps: List of browser steps to execute
            
        Returns:
            Execution result with audit log
        """
        if self.dry_run:
            return self._plan_execution(steps)
        else:
            return self._execute_plan(steps)
    
    def _plan_execution(self, steps: List[BrowserStep]) -> Dict[str, Any]:
        """
        Plan execution (DRY_RUN mode)
        
        Returns execution plan without actual browser operations
        """
        plan = {
            "dry_run": True,
            "steps": [step.to_dict() for step in steps],
            "total_steps": len(steps),
            "estimated_screenshots": sum(1 for s in steps if s.action == BrowserAction.SCREENSHOT),
            "status": "planned"
        }
        
        # Log planned steps with secret masking
        for i, step in enumerate(steps):
            self.audit_log.append({
                "step_index": i,
                "action": step.action.value,
                "params": self._mask_secrets_in_params(step.params),
                "dry_run": True,
                "status": "planned"
            })
        
        return plan
    
    def _mask_secrets_in_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask secrets in parameters (as separate method for clarity)
        
        Args:
            params: Parameters to mask
            
        Returns:
            Masked parameters
        """
        import re
        
        masked = {}
        for key, value in params.items():
            if isinstance(value, str):
                # Mask API keys
                value = re.sub(r'sk-[A-Za-z0-9]{20,}', 'sk-***MASKED***', value)
                value = re.sub(r'AIza[0-9A-Za-z\-_]{20,}', 'AIza***MASKED***', value)
                # Mask passwords
                if key.lower() in ['password', 'passwd', 'pwd', 'secret', 'text'] and 'password' in str(params.get('selector', '')).lower():
                    value = '***MASKED***'
                elif key.lower() in ['password', 'passwd', 'pwd', 'secret']:
                    value = '***MASKED***'
            
            masked[key] = value
        
        return masked
    
    def _execute_plan(self, steps: List[BrowserStep]) -> Dict[str, Any]:
        """
        Execute plan (non-DRY_RUN mode)
        
        Requires Playwright or similar driver
        """
        # Optional Playwright import
        try:
            from playwright.sync_api import sync_playwright
            driver_available = True
        except ImportError:
            driver_available = False
        
        if not driver_available:
            # Fallback to DRY_RUN if no driver
            return self._plan_execution(steps)
        
        # Actual execution would happen here
        results = []
        for i, step in enumerate(steps):
            result = self._execute_step(step)
            results.append(result)
            self.audit_log.append({
                "step_index": i,
                "action": step.action.value,
                "params": self._mask_secrets(step.params),
                "dry_run": False,
                "status": "executed",
                "result": result
            })
        
        return {
            "dry_run": False,
            "steps": [step.to_dict() for step in steps],
            "total_steps": len(steps),
            "screenshots": self.screenshots,
            "status": "executed",
            "results": results
        }
    
    def _execute_step(self, step: BrowserStep) -> Dict[str, Any]:
        """Execute single browser step"""
        # Placeholder for actual execution
        return {
            "action": step.action.value,
            "status": "executed",
            "screenshot": None
        }
    
    # Convenient methods (legacy compatibility)
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL"""
        step = BrowserStep(
            action=BrowserAction.NAVIGATE,
            params={"url": url}
        )
        return self._execute_step_single(step)
    
    def click(self, selector: str) -> Dict[str, Any]:
        """Click element by selector"""
        step = BrowserStep(
            action=BrowserAction.CLICK,
            params={"selector": selector}
        )
        return self._execute_step_single(step)
    
    def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """Type text into element"""
        step = BrowserStep(
            action=BrowserAction.TYPE,
            params={"selector": selector, "text": text}
        )
        return self._execute_step_single(step)
    
    def _execute_step_single(self, step: BrowserStep) -> Dict[str, Any]:
        """Execute single step (for legacy methods)"""
        result = {
            "action": step.action.value,
            "params": self._mask_secrets_in_params(step.params),
            "dry_run": self.dry_run,
            "screenshot": None,
            "status": "simulated" if self.dry_run else "executed"
        }
        
        # Add top-level keys for backwards compatibility
        if "url" in step.params:
            result["url"] = self._mask_secrets_in_params({"url": step.params["url"]})["url"]
        if "selector" in step.params:
            result["selector"] = step.params["selector"]
        if "text" in step.params:
            result["text"] = self._mask_secrets_in_params({"text": step.params["text"]})["text"]
        
        self.audit_log.append(result)
        return result
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log"""
        return self.audit_log
    
    def get_audit_log_json(self) -> str:
        """Get audit log as JSON"""
        return json.dumps(self.audit_log, indent=2)
    
    def _mask_secrets(self, text: str) -> str:
        """
        Legacy alias for secret masking (string input)
        
        Args:
            text: Text to mask
            
        Returns:
            Masked text
        """
        import re
        
        # Mask API keys
        text = re.sub(r'sk-[A-Za-z0-9]{20,}', 'sk-***MASKED***', text)
        text = re.sub(r'AIza[0-9A-Za-z\-_]{20,}', 'AIza***MASKED***', text)
        # Mask passwords
        text = re.sub(r'password=[^\s&]+', 'password=***MASKED***', text, flags=re.IGNORECASE)
        
        return text
