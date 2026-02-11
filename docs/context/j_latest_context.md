# AJSON Project Context (Latest)
Last Updated: 2026-02-11 09:05 JST

## Project Overview
- **Name**: AJSON (Agent JSON Orchestrator)
- **Goal**: Build a chaotic-good AI agent orchestrator with reliable "Office-N" business logic enforcement.
- **Current Phase**: Phase 9.6 (Realtime API Integration - Skeleton)

## Git Context
- **Repository**: office-n/ajson-proto
- **Main Branch**: `main` (Last stable: `e7a7134`)
- **Previous HEAD**: `46b624f`

## Recent Changes (Phase 9.7 Prep -> v2.1 SSOT)
- **Merged PR #52**: SSOT v2.0 Patch for Spec v0.2.
- **Current Status**: Spec v2.1 Enforced (Cockpit + Governance).
- **Next Phase**: Phase 9.7 (Realtime API / Remote Bridge Implementation).

## Key Files
- `ajson/core/realtime_client.py`: Base interface.
- `ajson/core/realtime_mock.py`: In-memory mock implementation.
- `ajson/core/realtime_openai.py`: Safe stub for OpenAI (Network Deny).
- `ajson/core/voice.py`: Updated orchestrator using DI.

## Next Steps
1. **Spec v0.2 Review**: Review and merge PR #49.
2. **Phase 9.7**: Implement Realtime API logic based on v0.2 spec.
