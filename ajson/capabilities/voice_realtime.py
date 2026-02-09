from typing import Generator, Optional
from ajson.core.tool import Tool

class VoiceRealtimeClient:
    """
    Client for OpenAI Realtime API (Stub).
    """
    def __init__(self, api_key: Optional[str] = None, dry_run: bool = False):
        self.api_key = api_key
        self.dry_run = dry_run
        self.connected = False
        self._buffer = []

    def connect(self):
        """
        Establishes connection to the Realtime API.
        In dry_run, just marks as connected.
        """
        if self.dry_run:
            self.connected = True
            # No network call
            return
        # Real implementation would go here
        raise NotImplementedError("Real connection not implemented yet")

    def send_audio_frame(self, audio_chunk: bytes):
        """
        Sends audio frame to the API.
        In dry_run, buffers the data.
        """
        if self.dry_run:
            self._buffer.append(audio_chunk)
            return
        raise NotImplementedError("Real send not implemented yet")

    def receive_events(self) -> Generator[dict, None, None]:
        """
        Yields events from the API.
        In dry_run, yields mock events.
        """
        if self.dry_run:
            if self.connected:
                yield {"type": "session.created", "event_id": "mock_evt_1"}
                yield {"type": "response.audio.delta", "delta": "b64_mock_audio"}
            return
        raise NotImplementedError("Real receive not implemented yet")

class VoiceRealtime(Tool):
    """
    Stub for Realtime Voice API.
    """
    @property
    def name(self) -> str:
        return "voice_realtime"

    @property
    def description(self) -> str:
        return "Handle realtime voice input/output."

    def execute(self, audio_chunk: bytes) -> bytes:
        # Stub usage of client
        client = VoiceRealtimeClient(dry_run=True)
        client.connect()
        client.send_audio_frame(audio_chunk)
        # Consume one event for demo
        _ = next(client.receive_events())
        return b"processed_audio"
