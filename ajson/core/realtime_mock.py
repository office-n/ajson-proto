from typing import Optional, List
from ajson.core.network_adapter import NetworkAdapter
from ajson.core.voice import AudioFrame

class RealtimeMock(NetworkAdapter):
    """
    In-memory mock implementation of RealtimeClient.
    Echoes input audio back as output (loopback), simulating processing.
    """
    def __init__(self):
        self._connected = False
        self._buffer: List[AudioFrame] = []

    def connect(self):
        self._connected = True

    def send_audio(self, frame: AudioFrame):
        if not self._connected:
            raise RuntimeError("RealtimeMock not connected")
        # Echo logic: buffer the frame to be "received" later
        self._buffer.append(frame)

    def receive_audio(self) -> Optional[AudioFrame]:
        if not self._connected:
            raise RuntimeError("RealtimeMock not connected")
        if self._buffer:
            return self._buffer.pop(0)
        return None

    def close(self):
        self._connected = False
        self._buffer.clear()
