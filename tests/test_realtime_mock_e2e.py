import pytest
from ajson.core.voice import RealtimeVoice, AudioFrame, AudioSource, AudioSink
from ajson.core.realtime_mock import RealtimeMock
from ajson.core.realtime_openai import RealtimeOpenAI

class SimpleSource(AudioSource):
    def __init__(self, data: list[bytes]):
        self.data = data
        self.index = 0
    def read(self):
        if self.index < len(self.data):
            frame = AudioFrame(data=self.data[self.index])
            self.index += 1
            return frame
        return None

class SimpleSink(AudioSink):
    def __init__(self):
        self.captured = []
    def write(self, frame: AudioFrame):
        self.captured.append(frame.data)

def test_mock_e2e_flow():
    """Verify data flows Source -> Mock Client -> Sink."""
    source = SimpleSource([b"one", b"two", b"three"])
    sink = SimpleSink()
    
    # DI: Inject Mock Client
    client = RealtimeMock()
    voice = RealtimeVoice(client=client)
    
    voice.process(source, sink)
    
    assert sink.captured == [b"one", b"two", b"three"]

def test_openai_safe_failure():
    """Verify OpenAI client stubs raise RuntimeError (NETWORK DENY enforcement)."""
    client = RealtimeOpenAI(api_key="dummy")
    
    # Connect should fail
    with pytest.raises(RuntimeError, match="NETWORK DENY"):
        client.connect()
    
    # Send should fail
    with pytest.raises(RuntimeError, match="NETWORK DENY"):
        client.send_audio(AudioFrame(data=b"test"))
        
    # Receive should fail
    with pytest.raises(RuntimeError, match="NETWORK DENY"):
        client.receive_audio()
