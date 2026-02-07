# Evidence: Branch Protection Audit

**タイムスタンプ**: 2026-02-08T03:55:00+09:00（Asia/Tokyo）

## 1. 監査対象
- **Repo**: `office-n/ajson-proto`
- **Branch**: `main`
- **Method**: `gh api repos/:owner/:repo/branches/main/protection` (Read-only)

## 2. 現状 (Current Status)
**Status**: ❌ **UNPROTECTED** (404 Not Found)

| Setting | Current Value | Risk |
| :--- | :--- | :--- |
| **Branch Protection** | **OFF** | 🚨 **High** |
| Require PR | N/A | Direct push allowed |
| Require Status Checks | N/A | CI failure ignored |
| Allow Force Pushes | **Allowed** (Default) | History rewrite risk |
| Allow Deletions | **Allowed** (Default) | Branch deletion risk |

## 3. 推奨設定 (Recommendations)
> [!IMPORTANT]
> This audit provided **read-only** findings. No settings were changed.
> To secure the branch, the following configuration is recommended.

- [ ] **Enable Branch Protection** for `main`
- [ ] **Require a pull request before merging**
  - [ ] Require approvals: 1
- [ ] **Require status checks to pass**
  - [ ] Search & Select: `lint` (found in `.github/workflows/lint.yml`)
- [ ] **Include administrators** (Enforce rules for admins too)
- [ ] **Restrict who can push** (Disable direct push)

## 4. 参照情報
- Workflow: `.github/workflows/lint.yml` (Job: `lint`)
