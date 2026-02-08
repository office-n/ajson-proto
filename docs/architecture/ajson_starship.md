# AJSON "Starship" Architecture (Cockpit Model)

## Philosophy
The "Starship Cockpit" model separates high-level directives from low-level execution, ensuring safety and observability at the boundary.

- **Directives (Orchestrator)**: The decision maker.
- **Controls (Agents/Tools)**: The interfaces to the world.
- **Safety (Policy)**: The hard limits (Allowlist/Denylist).
- **Black Box (Trace)**: The immutable record of actions.

## Core Components

### Orchestrator (`ajson.core.orchestrator`)
The heart of the system.
- Accepts high-level requests.
- Dispatches tasks to Agents.
- Enforces Policy on every Tool execution.
- Records Trace.

### Agent (`ajson.core.agent`)
Abstract interface for intelligent workers.
- Specialized roles (e.g., CodingAgent, PlanningAgent).
- Can use Tools.

### Tool (`ajson.core.tool`)
Abstract interface for capabilities.
- Atomic actions (e.g., FileRead, WebSearch).
- Must have strict input schema.

### Policy (`ajson.core.policy`)
Security enforcement layer.
- **Filesystem**: Relative paths only, Allowlist root only.
- **Network**: HTTPS only, Allowlist domains only.
- **Secrets**: Redaction in logs.

### Trace (`ajson.core.trace`)
Structured JSON logging.
- Every action (Input -> Decision -> Tool Call -> Result) is recorded.

## Directory Structure
```
ajson/
  core/
    orchestrator.py
    agent.py
    tool.py
    policy.py
    trace.py
  capabilities/
    filesystem_allowlist.py  # Wrapper for Policy-compliant FS access
    browser_autopilot.py     # Wrapper for Browser access
    voice_realtime.py        # Wrapper for Realtime Voice API
```
