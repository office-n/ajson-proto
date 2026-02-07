"""
Tests for screenshot evidence utility
"""
import pytest
import tempfile
from pathlib import Path
from ajson.hands.screenshot_evidence import ScreenshotEvidence


def test_screenshot_save_basic():
    """Save screenshot with dummy bytes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence = ScreenshotEvidence(output_dir=tmpdir)
        
        # Dummy PNG header bytes
        dummy_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        path = evidence.save_screenshot(dummy_png, name="test_screenshot")
        
        # Verify file exists and path is relative
        assert Path(path).exists()
        assert not path.startswith('/')  # No absolute paths
        assert "test_screenshot.png" in path


def test_screenshot_auto_naming():
    """Screenshot auto-generates name with timestamp"""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence = ScreenshotEvidence(output_dir=tmpdir)
        
        dummy_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        path = evidence.save_screenshot(dummy_png)
        
        assert "screenshot_" in path
        assert path.endswith(".png")


def test_screenshot_categories():
    """Screenshots saved in category subdirectories"""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence = ScreenshotEvidence(output_dir=tmpdir)
        
        dummy_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        path1 = evidence.save_screenshot(dummy_png, name="approval_test", category="approval")
        path2 = evidence.save_screenshot(dummy_png, name="execution_test", category="execution")
        
        assert "approval" in path1
        assert "execution" in path2
        assert Path(path1).exists()
        assert Path(path2).exists()


def test_list_screenshots():
    """List all screenshots"""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence = ScreenshotEvidence(output_dir=tmpdir)
        
        dummy_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        evidence.save_screenshot(dummy_png, name="test1", category="approval")
        evidence.save_screenshot(dummy_png, name="test2", category="execution")
        
        all_screenshots = evidence.list_screenshots()
        assert len(all_screenshots) == 2
        
        approval_screenshots = evidence.list_screenshots(category="approval")
        assert len(approval_screenshots) == 1
        assert "test1" in approval_screenshots[0]


def test_get_screenshot_path():
    """Get path to specific screenshot"""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence = ScreenshotEvidence(output_dir=tmpdir)
        
        dummy_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        evidence.save_screenshot(dummy_png, name="myshot", category="test")
        
        path = evidence.get_screenshot_path("myshot.png", category="test")
        assert path is not None
        assert "myshot.png" in path
        
        # Non-existent screenshot
        path = evidence.get_screenshot_path("nonexistent.png", category="test")
        assert path is None


def test_no_absolute_paths():
    """Verify no absolute paths are returned"""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence = ScreenshotEvidence(output_dir=tmpdir)
        
        dummy_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        path = evidence.save_screenshot(dummy_png, name="test")
        
        # Path should be relative
        assert not path.startswith('/')
        assert not 'Users' in path  # No absolute path indicators
        
        # List should also return relative paths
        screenshots = evidence.list_screenshots()
        for screenshot in screenshots:
            assert not screenshot.startswith('/')


def test_directory_creation():
    """Evidence directory created if not exists"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use non-existent subdirectory
        evidence_dir = Path(tmpdir) / "new_evidence_dir"
        assert not evidence_dir.exists()
        
        evidence = ScreenshotEvidence(output_dir=str(evidence_dir))
        
        # Directory should be created
        assert evidence_dir.exists()
