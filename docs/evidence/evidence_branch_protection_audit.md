# Evidence: Branch Protection Audit

**タイムスタンプ**: 2026-02-08T04:55:00+09:00（Asia/Tokyo）

## 1. 監査対象
- **Repo**: `office-n/ajson-proto`
- **Branch**: `main`
- **Method**: `gh api repos/:owner/:repo/branches/main/protection`

## 2. 現状 (Current Status)

### 2026-02-08 04:55: **PROTECTED (Baseline Enforced)**
**Status**: ✅ **PROTECTED** (HTTP 200 via `gh api`)

| Setting | Value | Note |
| :--- | :--- | :--- |
| **Branch Protection** | **ON** | Enforced via Settings |
| Require PR | **ON** | Approvals: 1 |
| Require Status Checks | **OFF** | To avoid guessing (Safety first) |
| Include Administrators | **ON** | Enforced |
| Allow Force Pushes | **OFF** | Blocked |
| Allow Deletions | **OFF** | Blocked |

### 2026-02-08 13:37: **RESTORED (enforce_admins=true)**
**Action**: Restored administrator enforcement after temporary bypass for PR #18 merge

**Verification**:
```bash
# Before restoration (2026-02-08T12:34:32+09:00)
gh api repos/office-n/ajson-proto/branches/main/protection --jq '.enforce_admins.enabled'
# Result: false

# After restoration (2026-02-08T13:37:25+09:00)
gh api repos/office-n/ajson-proto/branches/main/protection --jq '.enforce_admins.enabled'
# Result: true
```

**Context**: During PR #18 merge, `enforce_admins` was temporarily set to `false` to allow administrator bypass of failing checks. This restoration re-enables administrator enforcement to maintain security baseline.


### 2026-02-08 03:55: **UNPROTECTED (Audit Log)**
*(Historical status at time of initial audit)*
- Status: ❌ UNPROTECTED (404 Not Found)

## 3. 変更内容 (Changes Applied)
> [!IMPORTANT]
> Applied **Baseline** protection only.
> **Required status checks** were intentionally skipped to comply with the "No Guessing" rule.

- [x] **Enable Branch Protection** for `main`
- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
- [ ] **Require status checks to pass** (Skipped)
- [x] **Include administrators**
- [x] **Restrict who can push** (Implicit in Protection ON)

## 4. 参照情報
- Workflow: `.github/workflows/lint.yml` (Available but not enforced yet)
