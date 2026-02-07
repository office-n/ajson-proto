# Release Notes: v0.7.2-phase8

**タイムスタンプ**: 2026-02-07T18:20:00+09:00（Asia/Tokyo）  
**Tag**: v0.7.2-phase8  
**Repository**: office-n/ajson-proto

---

## Highlights

### Approval Queue System
- **ApprovalStore**: In-memory storage for approval requests, decisions, and grants
- **API Endpoints**: 
  - `GET /api/approvals/pending` - List pending approval requests
  - `POST /api/approvals/{id}/approve` - Approve with reason, scope, and TTL
  - `POST /api/approvals/{id}/deny` - Deny with reason
  - `GET /api/approvals/grants/active` - List active grants
- **Auto-Registration**: REQUIRE_APPROVAL operations automatically create approval requests
- **Grant Management**: Scope matching, expiration tracking, verification

### Limited Execute Mode
- **Approval-Gated Execution**: `execute_tool_limited` requires valid, non-expired grant
- **ALLOWLIST-Only**: Only operations in allowlist can execute (git status, ls, etc.)
- **Network永続DENY**: Network operations (curl, wget, nc, telnet) always denied, even with approval
- **Subprocess Restrictions**:
  - `shell=False` (never shell=True)
  - Hard timeout: 10 seconds
  - Restricted cwd: /tmp
  - Output truncation: 500 chars

---

## Security Posture

### Approval Workflow
1. Operation triggers REQUIRE_APPROVAL → approval request created
2. Admin reviews via API → approve/deny with reason
3. Approved grant has scope + expiration
4. Execute requires valid grant + operation matches scope

### Execution Safeguards
- **DRY_RUN Default**: No execution without explicit grant
- **Grant Verification**: Scope matching, expiration check before execution
- **Policy Re-evaluation**: Even with grant, policy is re-evaluated (ALLOW only)
- **Network永久DENY**: NETWORK category operations永続DENY
- **Subprocess Safety**: shell=False, timeout, cwd restrictions

---

## Verification

**Main Branch**:
- Lint: ✅ PASS (No violations found)
- Pytest: ✅ 75 passed
- Network: 0 external calls

**Test Coverage**:
- Approval queue: CRUD, state transitions, grant expiration, scope matching
- Limited execute: grant verification, allowlist enforcement, network DENY, subprocess mocking

---

## Breaking Changes

None. DRY_RUN remains default behavior.

---

## Notes

- **DRY_RUN Maintained**: Default behavior unchanged (planning + audit only)
- **Execution Requires Approval**: Real execution only with valid grant in LIMITED mode
- **Future Enhancements**: 
  - UI panel for approval queue in console
  - Persistent storage (SQLite/Redis) for approvals
  - Configurable approval workflows

---

## Files Changed

- `ajson/hands/approval.py`: Approval store, request, grant, decision models
- `ajson/api/approvals.py`: Approval API router
- `ajson/api/execute.py`: Limited execute API endpoint
- `ajson/hands/runner.py`: Integration + execute_tool_limited method
- `tests/test_approval_queue.py`: 8 tests for approval queue
- `tests/test_execute_limited.py`: 6 tests for limited execute

**Total**: 6 new files, 2 modified files
