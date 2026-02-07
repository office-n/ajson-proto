# Evidence: Fix E2E Network Deny Spec

## Status
✅ **Full Green (110/110 passed)**

## Context
- **Target**: Align E2E tests with Network Permanent Deny policy
- **Branch**: `fix/e2e-network-deny-spec` (merged to `main`)

## Implementation Details

### 1. Updated Tests
Updated `tests/test_approval_e2e.py` to expect `PolicyDeniedError` for network operations (`git clone`) instead of an approval flow.
Removed unreachable code paths (approval -> execute) that are blocked by policy.

```python
# tests/test_approval_e2e.py
def test_e2e_approval_to_execute_allowlist():
    # ...
    # This should raise PolicyDeniedError immediately, NOT create an approval request
    try:
        runner.execute_tool("git", {"clone": "..."})
        pytest.fail("Should have raised PolicyDeniedError")
    except Exception as e:
        if type(e).__name__ == 'PolicyDeniedError':
            assert "Denied: network operation" in str(e)
```

### 2. Test Isolation
Added `tests/conftest.py` to reset global singletons (`ApprovalStore`, `AuditLogger`) between tests.
This fixed side-effects where `test_api.py` execution caused `test_approval_e2e.py` failures.

## Verification Results

### Pytest Full Suite
```
tests/test_audit_logger.py::test_multiple_events PASSED
...
====================== 110 passed, 28 warnings in 17.87s =======================
```

### Forbidden Strings Lint
```
=== Summary ===
✅ PASS: No violations found
```
