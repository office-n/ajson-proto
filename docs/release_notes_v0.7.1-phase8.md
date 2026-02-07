# Release Notes: v0.7.1-phase8

**タイムスタンプ**: 2026-02-07T02:30:00+09:00（Asia/Tokyo）  
**Tag**: v0.7.1-phase8  
**PR**: #5

---

## Highlights

### Phase8 Hands Expansion (PR #5)
- **Policy Engine**: Expanded allowlist/denylist with PolicyDecision enumeration (ALLOW/DENY/REQUIRE_APPROVAL/DRY_RUN_ONLY)
- **Network Operations**: Network operations (curl/wget/nc/telnet) are now consistently DENY with category=NETWORK
- **Audit Logging**: JSON-serializable audit logs for all tool runner operations
- **BrowserPilot**: Scaffold implementation with DRY_RUN planning mode, secret masking, and step abstraction

### Compatibility Fixes
- **Backwards Compatibility**: Restored compatibility with existing tests (12 failing → 0 failing)
- **Legacy API**: Maintained legacy return values (url/selector/text/requires_approval/output fields)
- **DRY_RUN Semantics**: Preserved DRY_RUN = no execution + planning only

---

## Verification

**Lint**: ✅ PASS (No violations)  
**Pytest**: ✅ 61 passed (0 failed)  
**Network Calls**: ✅ 0 (all DRY_RUN)  
**Main Branch**: ✅ Green

---

## Technical Details

### Files Changed (8 files, +839/-209 lines)
- `ajson/hands/policy.py`: PolicyDecision/OperationCategory, allowlist/denylist separation, NETWORK_PATTERNS priority
- `ajson/hands/runner.py`: JSON audit logs, PolicyDeniedError for NETWORK, legacy compatibility
- `ajson/hands/browser_pilot.py`: BrowserStep abstraction, secret masking, legacy API compatibility
- `tests/test_*.py`: 3 new test files for policy/runner/browser_pilot

### Key Commits
- **62166b2**: Initial expansion (allowlist/denylist/BrowserPilot scaffold)
- **cfa13ff**: Backwards compatibility fix (12 failed → 0 failed)
- **cbbf8cb**: Network DENY semantics alignment (2 failed → 0 failed)

---

## Notes

**DRY_RUN Default**: All operations default to DRY_RUN mode (planning + audit logs only)  
**Approval Gates**: Actual execution requires explicit approval (future phase)  
**Network Denial**: Network operations are permanently DENY (no approval possible)  

---

## Next Steps

**Phase 8.2**: Enable actual tool execution with approval gates (requires boss approval)  
**Paid API Verification**: Minimal paid verification script (requires BOSS_PAID_OK=Yes)
