# AJSON Phase 9 Roadmap: "Starship Core"

## Phase 9.0: Core Skeleton (This PR)
- Establish directory structure.
- Define abstract base classes (Agent, Tool).
- Implement basic Policy enforcement (Stub).
- Implement Tracing interface (Stub).

## Phase 9.1: The First Pilot
- Implement a simple "Echo Agent" that uses "FileRead Tool".
- Prove the Orchestrator -> Policy -> Tool loop works.

## Phase 9.2: Realtime Voice
- Integrate OpenAI Realtime API (WebRTC/crypto).
- Connect Voice Input -> Orchestrator -> Voice Output.

## Phase 9.3: Browser Autopilot
- Integrate Browser Tool (Playwright/Puppeteer wrapper).
- Enable "Browse and Extract" capabilities.

## Phase 9.4: Full Cockpit
- Multi-agent coordination.
- Extensive Policy rules (domain whitelisting).
- Production-grade Tracing.
