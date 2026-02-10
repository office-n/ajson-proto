from typing import Optional
from ajson.core.realtime_client import RealtimeClient
from ajson.core.voice import AudioFrame

class RealtimeOpenAI(RealtimeClient):
    """
    Stub implementation for OpenAI Realtime API.
    Does NOT perform any network calls.
    Raises RuntimeError if used, enforcing "NETWORK DENY".
    """
    def __init__(self, api_key: str = "mock-key"):
        self.api_key = api_key

    def connect(self):
        # GUARD: Verify internal safe flag or config before allowing connection.
        # For Phase 9.6, this is strictly forbidden.
        raise RuntimeError("NETWORK DENY: RealtimeOpenAI connection is not yet enabled.")

    def send_audio(self, frame: AudioFrame):
        raise RuntimeError("NETWORK DENY: RealtimeOpenAI send_audio is not yet enabled.")

    def receive_audio(self) -> Optional[AudioFrame]:
        raise RuntimeError("NETWORK DENY: RealtimeOpenAI receive_audio is not yet enabled.")

    def close(self):
        pass
