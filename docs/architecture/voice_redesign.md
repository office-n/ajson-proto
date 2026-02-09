# Voice Architecture Redesign (Phase 9.4)

## Overview
Moving from legacy polling/REST voice implementation to **OpenAI Realtime API** (WebRTC/WebSocket).

## Core Components

### VoiceRealtimeClient
- **Responsibility**: Manages the persistent connection to OpenAI Realtime API.
- **Protocol**: WebSocket (initially) / WebRTC (future).
- **Model**: `gpt-4o-realtime-preview` (implied).

### Integration
- **TTS/STT**: The Realtime API handles raw audio input and output directly. Legacy separate TTS/STT APIs are fallback/auxiliary only.
- **Tools**: The client will handle function calling (tool use) directly via the realtime session.

## Testing Strategy
- **Stub + DRY_RUN**: Current implementation is a stub.
- **No Network**: `dry_run=True` ensures no external connections are attempted.
- **Mock Events**: The client yields predefined mock events ("session.created", "audio.delta") to simulate the protocol flow.
