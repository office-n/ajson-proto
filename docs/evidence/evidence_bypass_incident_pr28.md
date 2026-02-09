タイムスタンプ: 2026-02-09T02:35:12+09:00（Asia/Tokyo）

# PR#28 Bypass Incident and Resolution Evidence

## 1. Incident Overview
- **PR URL**: https://github.com/office-n/ajson-proto/pull/28
- **Merger**: office-n
- **Time**: 2026-02-09T02:35:12+09:00 (JST)
- **Status at Merge**: 0/2 status checks passed (lint failed), 0 approvals.
- **Root Cause**: Branch protection for `main` did not have "Include administrators" enabled, allowing `office-n` to bypass required checks.

## 2. Evidence of Audit and Remediation
- **Audit Tool**: GitHub Settings -> Branches -> main protection rule.
- **Findings**: `enforce_admins` was disabled.
- **Action Taken**: Enabled "Do not allow bypassing the above settings" (Include administrators).
- **Result**: Bypass by administrative accounts is now structurally prohibited.

## 3. Current Protection Status
- **Required Reviews**: 1 approval required.
- **Required Status Checks**: `lint` must pass.
- **Enforce Admins**: ENABLED (Bypass impossible).

