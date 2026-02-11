import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

@dataclass
class AudioFrame:
    """Represents a chunk of audio data."""
    data: bytes
    timestamp: float = field(default_factory=time.time)
    duration_ms: int = 20 # Default frame duration

class AudioSource(ABC):
    """Abstract base class for audio input sources."""
    @abstractmethod
    def read(self) -> Optional[AudioFrame]:
        """Reads the next audio frame. Returns None if EOF."""
        pass

class AudioSink(ABC):
    """Abstract base class for audio output sinks."""
    @abstractmethod
    def write(self, frame: AudioFrame):
        """Writes an audio frame."""
        pass

if TYPE_CHECKING:
    from ajson.core.network_adapter import NetworkAdapter

class RealtimeVoice:
    """
    RealtimeVoice processing orchestrator.
    Uses an injected NetworkAdapter (default: Mock) to handle API communication.
    """
    def __init__(self, client: Optional['NetworkAdapter'] = None):
        if client is None:
            from ajson.core.realtime_mock import RealtimeMock
            self.client = RealtimeMock()
        else:
            self.client = client
        self._shutdown = False

    def process(self, source: AudioSource, sink: AudioSink, max_frames: int = 100):
        """
        Processes audio frames from source -> client -> sink.
        """
        self.client.connect()
        try:
            frame_count = 0
            while not self._shutdown and frame_count < max_frames:
                # 1. Read from Source
                input_frame = source.read()
                if input_frame is None:
                    break
                
                # 2. Send to Client (Mock or Real)
                self.client.send_audio(input_frame)

                # 3. Receive from Client
                output_frame = self.client.receive_audio()
                
                # 4. Write to Sink (if we got something back)
                if output_frame:
                    sink.write(output_frame)
                
                frame_count += 1
        finally:
            self.client.close()
            
    def shutdown(self):
        self._shutdown = True
