
import os
import json
import pytest
import shutil
from ajson.hands.history_manager import HistoryManager
from ajson.cli.cockpit import Cockpit

@pytest.fixture
def temp_history_dir(tmp_path):
    d = tmp_path / "history"
    d.mkdir()
    return str(d)

@pytest.fixture
def history_mgr(temp_history_dir):
    return HistoryManager(history_dir=temp_history_dir)

def test_history_manager_masking(history_mgr):
    home = os.path.expanduser("~")
    path = os.path.join(home, "secret.txt")
    history_mgr.add_entry("user", f"Read {path}")
    
    entry = history_mgr.get_entries(1)[0]
    assert "[USER_HOME]" in entry["content"]
    assert home not in entry["content"]

def test_history_manager_persistence(history_mgr):
    history_mgr.add_entry("user", "Hello")
    history_mgr.flush()
    
    assert os.path.exists(history_mgr.log_path)
    with open(history_mgr.log_path, "r") as f:
        data = json.load(f)
        assert data["entries"][0]["content"] == "Hello"

def test_cockpit_multi_line_logic(history_mgr):
    cp = Cockpit(history_mgr=history_mgr)
    
    # Start multi-line
    cp.process_line('"""')
    assert cp.multi_line_mode is True
    
    cp.process_line("Line 1")
    cp.process_line("Line 2")
    
    # End multi-line
    cp.process_line('"""')
    assert cp.multi_line_mode is False
    
    entries = history_mgr.get_entries(1)
    assert entries[0]["content"] == "Line 1\nLine 2"

def test_cockpit_attach_validation(history_mgr, tmp_path):
    cp = Cockpit(history_mgr=history_mgr)
    
    # Non-existent file
    cp.process_line("attach /tmp/non_existent_file_999")
    assert len(history_mgr.get_entries()) == 0
    
    # Real file
    real_file = tmp_path / "test.txt"
    real_file.write_text("content")
    cp.process_line(f"attach {str(real_file)}")
    
    entries = history_mgr.get_entries(1)
    assert entries[0]["role"] == "system"
    assert "Attached file: test.txt" in entries[0]["content"]
    assert entries[0]["metadata"]["size"] == 7
