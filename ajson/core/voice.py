import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List, Optional

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

class RealtimeVoice:
    """
    Mock implementation of RealtimeVoice processing.
    Passes audio from source to sink with simulated processing delay.
    """
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name
        self._shutdown = False

    def process(self, source: AudioSource, sink: AudioSink, max_frames: int = 100):
        """
        Processes audio frames from source and writes to sink.
        Stops after max_frames or when source returns None.
        """
        frame_count = 0
        while not self._shutdown and frame_count < max_frames:
            frame = source.read()
            if frame is None:
                break
            
            # Simulate processing (e.g. VAD, STT, LLM, TTS latency)
            # For mock, we just pass through.
            # In a real implementation, this would involve network calls.
            # Here, we ensure NO network calls are made.
            
            sink.write(frame)
            frame_count += 1
            
    def shutdown(self):
        self._shutdown = True
