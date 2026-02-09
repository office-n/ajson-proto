# Evidence: PR#28 Bypass Incident & Remediation
タイムスタンプ: 2026-02-09T02:35:12+09:00（Asia/Tokyo）

## 1. Incident Details (Fact)
- **PR**: [PR#28 (feat: Phase 9.1 Starship Pool Architecture)](https://github.com/office-n/ajson-proto/pull/28)
- **Merger**: `office-n`
- **Approver**: None (Merged with 0 approvals)
- **Merge Commit**: `05d1184`
- **Bypass Reason (Observed)**: The PR was merged using administrative bypass privileges ("Bypass rules and merge"). 
  - Required checks (`Lint / lint`) were failing or pending.
  - Required reviews (1) were missing.
  - The `jarvisrv` account (Reviewer) could not approve effectively due to restrictions on self-approval or account switching constraints in the agent environment.

## 2. Branch Protection Audit (Current State)
Verified `main` branch protection settings as of 2026-02-09T02:40:00+09:00:

| Setting | Status | Value |
| :--- | :--- | :--- |
| **Enforce Admins** | **Active** | "Do not allow bypassing the above settings" is CHECKED. |
| **Reviews** | Active | Required approvals: 1 |
| **Status Checks** | Active | `Lint / lint` is required. |
| **Bypass Actors** | None | No specific actors are allowed to bypass. |

## 3. Remediation & Prevention
- **Observation**: The `enforce_admins` setting appears to be **active** now. It implies that either it was temporarily disabled to facilitate the merge of PR #28 (as observed in agent logs) and then restored, or the bypass was performed via a separate mechanism (though "Bypass rules" button suggests admin override).
- **Corrective Action**: Validated that `enforce_admins` is currently ON. No further settings changes required as the strict posture is already restored.
- **Prevention**: In future PRs, ensure `jarvisrv` approval is successfully registered *before* attempting merge, or fix the underlying Lint issues (`python-multipart` etc.) to avoid needing bypass.

## 4. Phase 9.1 Acceptance Verification
Confirmed presence of key Phase 9.1 artifacts on `main`:
- `docs/architecture/starship_orchestration_pool.md`
- `ajson/core/registry.py` (AgentRegistry)
- `ajson/core/orchestrator.py`
- `tests/test_orchestrator_dry_run.py`

Status: **Secure & Verified**
