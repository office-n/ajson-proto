import pytest
from ajson.core.voice import RealtimeVoice, AudioSource, AudioSink, AudioFrame

class MockSource(AudioSource):
    def __init__(self, frames: list[AudioFrame]):
        self.frames = frames
        self.index = 0

    def read(self):
        if self.index < len(self.frames):
            frame = self.frames[self.index]
            self.index += 1
            return frame
        return None

class MockSink(AudioSink):
    def __init__(self):
        self.received_frames = []

    def write(self, frame: AudioFrame):
        self.received_frames.append(frame)

def test_voice_process_mock():
    # Setup
    input_frames = [
        AudioFrame(data=b"chunk1"),
        AudioFrame(data=b"chunk2"),
        AudioFrame(data=b"chunk3")
    ]
    source = MockSource(input_frames)
    sink = MockSink()
    # Updated: No model_name arg, use default mock client or inject one
    voice = RealtimeVoice()

    # Execute
    voice.process(source, sink)

    # Verify
    assert len(sink.received_frames) == 3
    assert sink.received_frames[0].data == b"chunk1"
    assert sink.received_frames[2].data == b"chunk3"

def test_voice_process_limit():
    # Setup
    input_frames = [AudioFrame(data=b"0")] * 10
    source = MockSource(input_frames)
    sink = MockSink()
    voice = RealtimeVoice()

    # Execute with limit
    # We set max_frames=5 to verify the loop terminates correctly
    voice.process(source, sink, max_frames=5)

    # Verify
    assert len(sink.received_frames) == 5
    assert len(source.frames) == 10 # Source had more frames than consumed
