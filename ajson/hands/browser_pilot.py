"""
BrowserPilot: Execute browser actions with approval gates (DRY_RUN only scaffold)
"""
from typing import Dict, Any, List, Optional


class BrowserPilot:
    """
    BrowserPilot with approval gates
    
    Phase 8 scaffold: DRY_RUN only, screenshot evidence, secret masking
    """
    
    def __init__(self, dry_run: bool = True, headless: bool = True):
        """
        Initialize BrowserPilot
        
        Args:
            dry_run: If True, no actual browser execution (scaffold default)
            headless: Browser headless mode
        """
        self.dry_run = dry_run
        self.headless = headless
        self.audit_log = []
        self.screenshots = []
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to URL
        
        Args:
            url: Target URL
            
        Returns:
            Navigation result with screenshot reference
        """
        result = {
            "action": "navigate",
            "url": self._mask_secrets(url),
            "dry_run": self.dry_run,
            "screenshot": None,
            "status": "simulated" if self.dry_run else "executed"
        }
        
        if not self.dry_run:
            # Real execution would happen here
            # screenshot_path = self._capture_screenshot()
            # result["screenshot"] = screenshot_path
            pass
        
        self.audit_log.append(result)
        return result
    
    def click(self, selector: str) -> Dict[str, Any]:
        """
        Click element by selector
        
        Args:
            selector: CSS selector
            
        Returns:
            Click result with screenshot reference
        """
        result = {
            "action": "click",
            "selector": selector,
            "dry_run": self.dry_run,
            "screenshot": None,
            "status": "simulated" if self.dry_run else "executed"
        }
        
        self.audit_log.append(result)
        return result
    
    def type_text(self, selector: str, text: str) -> Dict[str, Any]:
        """
        Type text into element
        
        Args:
            selector: CSS selector
            text: Text to type (will be masked if contains secrets)
            
        Returns:
            Type result with masked text
        """
        result = {
            "action": "type",
            "selector": selector,
            "text": self._mask_secrets(text),
            "dry_run": self.dry_run,
            "screenshot": None,
            "status": "simulated" if self.dry_run else "executed"
        }
        
        self.audit_log.append(result)
        return result
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log"""
        return self.audit_log
    
    def _mask_secrets(self, text: str) -> str:
        """
        Mask secrets in text (simple version)
        
        Args:
            text: Text to mask
            
        Returns:
            Masked text
        """
        import re
        
        # Mask API keys (sk-*, AIza*)
        text = re.sub(r'sk-[A-Za-z0-9]{20,}', 'sk-***MASKED***', text)
        text = re.sub(r'AIza[0-9A-Za-z\-_]{20,}', 'AIza***MASKED***', text)
        
        # Mask passwords (password=...)
        text = re.sub(r'password=[^\s&]+', 'password=***MASKED***', text, flags=re.IGNORECASE)
        
        return text
    
    def _capture_screenshot(self) -> Optional[str]:
        """
        Capture screenshot (DRY_RUN returns None)
        
        Returns:
            Screenshot path or None
        """
        if self.dry_run:
            return None
        
        # Real implementation would use playwright/selenium
        # timestamp = datetime.now().isoformat()
        # screenshot_path = f"screenshots/screenshot_{timestamp}.png"
        # return screenshot_path
        
        return None
