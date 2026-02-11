
import pytest
from unittest.mock import MagicMock, patch
import os
import json
from ajson.cli.approval import main
from ajson.hands.approval_sqlite import SQLiteApprovalStore, ApprovalRequest

@pytest.fixture
def mock_store():
    with patch('ajson.cli.approval.SQLiteApprovalStore') as MockStore:
        store = MockStore.return_value
        store.get_pending.return_value = []
        yield store

def test_list_pending_empty(mock_store, capsys):
    with patch('sys.argv', ['ajson-cli', 'list']):
        main()
    captured = capsys.readouterr()
    assert "No pending requests." in captured.out

def test_list_pending_items(mock_store, capsys):
    mock_store.get_pending.return_value = [
        ApprovalRequest(
            request_id="req-123",
            operation="connect google.com",
            category="network",
            reason="testing",
            status="pending",
            metadata={},
            created_at="2026-01-01T00:00:00"
        )
    ]
    with patch('sys.argv', ['ajson-cli', 'list']):
        main()
    captured = capsys.readouterr()
    assert "Found 1 pending requests" in captured.out
    assert "req-123" in captured.out
    assert "connect google.com" in captured.out

def test_approve_request(mock_store, capsys):
    mock_grant = MagicMock()
    mock_grant.grant_id = "grant-abc"
    mock_grant.expires_at = "2026-01-01T01:00:00"
    mock_store.approve_request.return_value = mock_grant

    with patch('sys.argv', ['ajson-cli', 'approve', 'req-123', '--scope', 'google.com']):
        main()
    
    captured = capsys.readouterr()
    assert "Approving request req-123" in captured.out
    assert "Granted: grant-abc" in captured.out
    
    mock_store.approve_request.assert_called_once()
    call_args = mock_store.approve_request.call_args
    assert call_args[0][0] == "req-123"
    assert call_args[0][1].scope == ["google.com"]

def test_deny_request(mock_store, capsys):
    with patch('sys.argv', ['ajson-cli', 'deny', 'req-123', '--reason', 'policy']):
        main()
    
    captured = capsys.readouterr()
    assert "Denying request req-123" in captured.out
    assert "Denied." in captured.out
    
    
    mock_store.deny_request.assert_called_once_with("req-123", "policy")

def test_cli_error_handling(mock_store, capsys):
    mock_store.get_pending.side_effect = Exception("Database error")
    with patch('sys.argv', ['ajson-cli', 'list']):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
    
    captured = capsys.readouterr()
    assert "Error listing requests: Database error" in captured.err

