import pytest
from ajson.capabilities.voice_realtime import VoiceRealtimeClient

def test_instantiation():
    """Verify client creates with dry_run flag."""
    client = VoiceRealtimeClient(api_key="mock_key", dry_run=True)
    assert client.dry_run is True
    assert client.api_key == "mock_key"
    assert client.connected is False

def test_connect_dry_run():
    """Verify connect() does not raise errors and sets internal state."""
    client = VoiceRealtimeClient(dry_run=True)
    client.connect()
    assert client.connected is True

def test_io_simulation():
    """Verify send_audio_frame buffers and receive_events yields mock data."""
    client = VoiceRealtimeClient(dry_run=True)
    client.connect()
    
    # Send
    mock_audio = b"\x00\x01\x02"
    client.send_audio_frame(mock_audio)
    assert len(client._buffer) == 1
    assert client._buffer[0] == mock_audio
    
    # Receive
    events = list(client.receive_events())
    assert len(events) >= 1
    assert events[0]["type"] == "session.created"
