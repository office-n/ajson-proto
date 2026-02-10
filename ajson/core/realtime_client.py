from abc import ABC, abstractmethod
from typing import Optional

# Re-export AudioFrame for convenience
# Ideally this would be in a common types module, 
# but for now we keep it simple.
from ajson.core.voice import AudioFrame

class RealtimeClient(ABC):
    """Abstract base class for Realtime API clients."""
    
    @abstractmethod
    def connect(self):
        """Establish connection (mock or real)."""
        pass

    @abstractmethod
    def send_audio(self, frame: AudioFrame):
        """Send audio frame to the API."""
        pass

    @abstractmethod
    def receive_audio(self) -> Optional[AudioFrame]:
        """Receive audio frame from the API."""
        pass

    @abstractmethod
    def close(self):
        """Close connection."""
        pass
