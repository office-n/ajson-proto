from abc import ABC, abstractmethod
from typing import Optional
from ajson.core.voice import AudioFrame

class NetworkAdapter(ABC):
    """
    Abstract base class for Realtime API network interactions.
    Decouples logic from specific network implementations (WebSocket, Loopback, etc).
    """
    
    @abstractmethod
    def connect(self):
        """Establish connection."""
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
