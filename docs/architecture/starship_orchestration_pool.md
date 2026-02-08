# Starship Orchestration Pool Architecture (Phase 9.1)

## Overview
Phase 9.1 shifts the architecture from a single "Starship" to a "Fleet" model.
- **Commander**: OpenAI (Brain)
- **Sub-AI Pool**: N idle instances (Arms/Legs)

## Components

### 1. AgentRegistry (`ajson.core.registry`)
Manages the lifecycle and state of all agents.
- **Provider**: 'openai', 'gemini', 'anthropic', etc.
- **Pool**: List of agent instances.
- **Status**: IDLE, BUSY, OFFLINE.

### 2. Dispatcher (`ajson.core.dispatcher`)
Decides which agent gets which task.
- **Input**: TaskGraph, Registry.
- **Strategy**: 
  - `capability_match`: Check skill tags.
  - `load_balance`: Round-robin or least busy.
  - `failover`: Retry on another agent if one fails.

### 3. Aggregator (`ajson.core.aggregator`)
Combines results from multiple agents into a single output.
- **Conflict Resolution**: Logic to handle disagreeing outputs (currently "mark as unverified").
- **Quality Gate**: Checks against Policy/Safety rules.

### 4. TaskGraph & WorkItem
- **WorkItem**: A self-contained task unit with clear input/output/constraints.
- **TaskGraph**: DAG of WorkItems (currently flat list for Phase 9.1).

### 5. Policy & Safety (Enhanced)
- **Sanitization**: All outputs must be sanitized (no secrets, no absolute paths).
- **Validation**: Outputs must meet specific evidentiary standards.

## Configuration (`ajson.config`)
- **subagents.json**: Defines the pool. Keys are **References** only (e.g., `ENV:GEMINI_KEY`).
- **Runtime**: Keys are resolved from environment variables only at execution time.

## Flow
1. **User Request** -> Orchestrator
2. Orchestrator -> **Dispatcher** (Plan decomposition)
3. Dispatcher -> **Registry** (Acquire Agents)
4. Agents -> **Execute** (Parallel/Async)
5. Results -> **Aggregator** (Merge & Verify)
6. Aggregator -> **User Response**
