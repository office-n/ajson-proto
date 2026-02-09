# AJSON Phase 9 Roadmap: "Starship Core"

## Phase 9.0: Core Skeleton (This PR)
- Establish directory structure.
- Define abstract base classes (Agent, Tool).
- Implement basic Policy enforcement (Stub).
- Implement Tracing interface (Stub).

## Phase 9.1: The First Pilot
- Implement a simple "Echo Agent" that uses "FileRead Tool".
- Prove the Orchestrator -> Policy -> Tool loop works.

## Phase 9.2: Sub-AI Pool Management (Done)
- Integrates `subagents.json` configuration.
- Registry enhancements (unified store, model attribute).
- Dry-Run testing for pool lifecycle.

## Phase 9.3: Dispatcher Minimal (Next)
- **Goal**: Implement intelligence dispatcher logic.
- **Features**:
  - `capability_match`: Route tasks based on agent capabilities.
  - `load_balance`: Simple round-robin or least-busy strategy.
  - `failover`: Retry with different agent on failure.
- **Testing**:
  - DRY_RUN tests for dispatch logic (mock agents).
  - Verify failover sequences without external calls.

## Phase 9.4: Realtime Voice (Future)
- Integrate OpenAI Realtime API (WebRTC/crypto).


## Phase 9.4: Full Cockpit
- Multi-agent coordination.
- Extensive Policy rules (domain whitelisting).
- Production-grade Tracing.
