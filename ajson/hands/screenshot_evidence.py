"""
Screenshot evidence utility

Saves screenshot bytes to data/screenshots/ directory.
DRY_RUN mode - no actual external screenshot capture.
"""
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class ScreenshotEvidence:
    """Utility for saving screenshot evidence"""
    
    def __init__(self, output_dir: str = "data/screenshots"):
        """
        Initialize screenshot evidence utility
        
        Args:
            output_dir: Relative path to screenshot directory
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_screenshot(
        self,
        image_data: bytes,
        name: Optional[str] = None,
        category: str = "general"
    ) -> str:
        """
        Save screenshot bytes to file
        
        Args:
            image_data: Raw image bytes (PNG format)
            name: Optional custom name (auto-generated if not provided)
            category: Category subdirectory (e.g., 'approval', 'execution')
            
        Returns:
            Relative path to saved screenshot
        """
        # Create category subdirectory
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if not name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            name = f"screenshot_{timestamp}.png"
        elif not name.endswith('.png'):
            name = f"{name}.png"
        
        # Save file
        filepath = category_dir / name
        filepath.write_bytes(image_data)
        
        # Return relative path (no absolute paths)
        return str(filepath.relative_to(Path.cwd()))
    
    def list_screenshots(self, category: Optional[str] = None) -> list:
        """
        List saved screenshots
        
        Args:
            category: Optional category filter
            
        Returns:
            List of relative paths to screenshots
        """
        if category:
            search_dir = self.output_dir / category
            if not search_dir.exists():
                return []
        else:
            search_dir = self.output_dir
        
        screenshots = []
        for filepath in search_dir.rglob("*.png"):
            screenshots.append(str(filepath.relative_to(Path.cwd())))
        
        return sorted(screenshots)
    
    def get_screenshot_path(self, filename: str, category: str = "general") -> Optional[str]:
        """
        Get relative path to screenshot
        
        Args:
            filename: Screenshot filename
            category: Category subdirectory
            
        Returns:
            Relative path if exists, None otherwise
        """
        filepath = self.output_dir / category / filename
        if filepath.exists():
            return str(filepath.relative_to(Path.cwd()))
        return None


# Global instance
_screenshot_evidence: Optional[ScreenshotEvidence] = None


def get_screenshot_evidence() -> ScreenshotEvidence:
    """Get global screenshot evidence instance"""
    global _screenshot_evidence
    if _screenshot_evidence is None:
        _screenshot_evidence = ScreenshotEvidence()
    return _screenshot_evidence
