# AJSON Project Context (Latest)
Last Updated: 2026-02-11 08:00 JST

## Project Overview
- **Name**: AJSON (Agent JSON Orchestrator)
- **Goal**: Build a chaotic-good AI agent orchestrator with reliable "Office-N" business logic enforcement.
- **Current Phase**: Phase 9.6 (Realtime API Integration - Skeleton)

## Git Context
- **Repository**: office-n/ajson-proto
- **Main Branch**: `main` (Last stable: `4f5830b`)
- **Working Branch**: `feat/phase9-6-realtime-integration-skeleton-v2` (Head: `c14f415`)
  - **Status**: PR #48 Approved (Pending Merge due to Branch Protection)
  - **Contains**: RealtimeClient Mock, Stub, Tests, Evidence.

## Recent Changes (Phase 9.6)
- **Implemented**: `RealtimeClient` interface, `RealtimeMock` (loopback), `RealtimeOpenAI` (stub with NETWORK DENY).
- **Refactored**: `RealtimeVoice` to use Dependency Injection for client.
- **Tests**: Added `tests/test_realtime_mock_e2e.py` for mock flow verification.
- **Documentation**: Added Roadmap and Kickoff Evidence.

## Key Files
- `ajson/core/realtime_client.py`: Base interface.
- `ajson/core/realtime_mock.py`: In-memory mock implementation.
- `ajson/core/realtime_openai.py`: Safe stub for OpenAI (Network Deny).
- `ajson/core/voice.py`: Updated orchestrator using DI.

## Next Steps
1. **Manual Merge**: Merge PR #48 to `main`.
2. **Phase 9.6 Completion**: Proceed to implementation of actual Realtime API logic (Phase 9.7+).
