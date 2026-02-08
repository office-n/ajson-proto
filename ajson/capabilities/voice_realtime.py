# ajson/capabilities/voice_realtime.py
from ajson.core.tool import Tool

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
        # Stub
        return b"processed_audio"
