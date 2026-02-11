import pytest
import os
from unittest.mock import MagicMock, patch
from ajson.hands.allowlist import Allowlist, NetworkDeniedError
from ajson.core.network import SecureNetworkConnector, ApprovalRequiredError
from ajson.hands.approval_sqlite import ApprovalGrant
from ajson.hands.approval import ApprovalDecision


class TestNetworkSecurity:
    
    @pytest.fixture
    def mock_allowlist(self):
        return Allowlist(allowed_hosts=["api.example.com"], allowed_ports=[443])

    @pytest.fixture
    def mock_approval(self):
        store = MagicMock()
        store.get_active_grants.return_value = []
        return store

    @pytest.fixture
    def mock_logger(self):
        return MagicMock()

    def test_allowlist_check_success(self, mock_allowlist):
        # Should not raise
        mock_allowlist.check("api.example.com", 443)

    def test_allowlist_check_failure_host(self, mock_allowlist):
        with pytest.raises(NetworkDeniedError):
            mock_allowlist.check("evil.com", 443)

    def test_allowlist_check_failure_port(self, mock_allowlist):
        with pytest.raises(NetworkDeniedError):
            mock_allowlist.check("api.example.com", 8080)

    def test_connector_denied_by_allowlist(self, mock_allowlist, mock_approval, mock_logger):
        connector = SecureNetworkConnector(
            allowlist=mock_allowlist,
            approval_store=mock_approval,
            audit_logger=mock_logger
        )
        
        with pytest.raises(NetworkDeniedError):
            connector.connect("evil.com", 443, "Testing")
        
        # Verify log
        mock_logger.log_event.assert_called()
        calls = mock_logger.log_event.call_args_list
        assert calls[0][0][0] == "network.connect.attempt"
        assert calls[1][0][0] == "network.connect.denied"

    def test_connector_denied_by_approval(self, mock_allowlist, mock_approval, mock_logger):
        connector = SecureNetworkConnector(
            allowlist=mock_allowlist,
            approval_store=mock_approval, # returns [] grants
            audit_logger=mock_logger
        )

        with pytest.raises(ApprovalRequiredError):
            connector.connect("api.example.com", 443, "Testing")

        calls = mock_logger.log_event.call_args_list
        assert calls[1][0][0] == "network.connect.denied"

    def test_connector_success(self, mock_allowlist, mock_approval, mock_logger):
        # Setup mock grant
        grant = ApprovalGrant(
            grant_id="test", request_id="req", scope="api.example.com", 
            expires_at="future", created_at="now"
        )
        mock_approval.get_active_grants.return_value = [grant]
        
        connector = SecureNetworkConnector(
            allowlist=mock_allowlist,
            approval_store=mock_approval,
            audit_logger=mock_logger
        )

        assert connector.connect("api.example.com", 443, "Testing") is True
        
        calls = mock_logger.log_event.call_args_list
        assert calls[1][0][0] == "network.connect.allowed"
