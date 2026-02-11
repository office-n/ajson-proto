import pytest
from unittest.mock import MagicMock
from ajson.core.realtime_client import RealtimeClient
from ajson.core.realtime_session import RealtimeSession, SessionState

class MockClient(RealtimeClient):
    def connect(self): pass
    def send_audio(self, frame): pass
    def receive_audio(self): return None
    def close(self): pass

@pytest.fixture
def mock_client():
    return MockClient()

def test_initial_state(mock_client):
    session = RealtimeSession(mock_client)
    assert session.state == SessionState.INIT

def test_connect_no_network(mock_client):
    # Network disallowed (default)
    session = RealtimeSession(mock_client, allow_network=False)
    
    # Spy on client
    mock_client.connect = MagicMock()
    
    session.connect()
    
    # Should simulate READY without hitting client
    assert session.state == SessionState.READY
    mock_client.connect.assert_not_called()

def test_connect_with_network(mock_client):
    # Network allowed
    session = RealtimeSession(mock_client, allow_network=True)
    
    mock_client.connect = MagicMock()
    
    session.connect()
    
    assert session.state == SessionState.READY
    mock_client.connect.assert_called_once()

def test_connect_error(mock_client):
    session = RealtimeSession(mock_client, allow_network=True)
    
    mock_client.connect = MagicMock(side_effect=Exception("Connection failed"))
    
    session.connect()
    
    assert session.state == SessionState.ERROR

def test_send_text_no_network(mock_client):
    session = RealtimeSession(mock_client, allow_network=False)
    session.connect() # Transitions to READY
    
    # Text sending should be safe (no-op or log)
    session.send_text("Hello")
    assert session.state == SessionState.READY

def test_close(mock_client):
    session = RealtimeSession(mock_client)
    session.close()
    assert session.state == SessionState.CLOSED
