# Ants Playbook (外部記憶)

## 概要
Antsはステートレスな実行機であり、記憶（コンテキスト）を保持しない。
本Playbookは、成功パターンや手順を外部記憶として定着させるためのものである。

## 1. 起動手順（Every Boot）
1. **Anchor**: `bash scripts/ants_anchor.sh` (記憶の起点)
2. **Guard**: `bash scripts/ants_guard.sh` (記憶の鮮度確認)
3. **Task**: `task.md` の確認と更新

## 2. Preflight運用（Before Submission）
提出物（PR / Report）を作成する直前に実行する。
1. `echo "報告内容..." > report.md`
2. `bash scripts/ants_preflight.sh report.md`
3. OKなら提出。NGなら修正（特に英語混入）。

## 3. 成功パターン（Reference）

### 3-1. Actions 5xx エラー対策
- **現象**: 500/502/503 エラー (GitHub側の問題)
- **対策**:
  1. `githubstatus.com` API確認
  2. "Minor Service Outage" 等なら **NOGO** (待機)
  3. 回復後、BrowserでRe-run -> Green確認 -> **GO**

### 3-2. PR Merge 手順
- **Role**:
  - `jarvisrv`: Approver (Reviewer)
  - `office-n`: Merger (Author)
- **Sequence**:
  1. Login `jarvisrv` -> Approve
  2. Login `office-n` -> Check Green & Approved -> Squash Merge
- **Bypass**: 禁止。管理者権限が必要な場合はSTOP。

### 3-3. Piloting
- 新規実装や複雑な変更は、まず `tests/` で検証する (Dry Run)。
- いきなり本番コードを触らない。

## 4. 忘却対策（Memory Hardening）
- **Anchor**: 1時間ごとのタイムスタンプ更新で、自身の稼働時間を自覚する。
- **Guard**: 1時間以上経過したAnchorは「記憶喪失」とみなし、再確認を促す。
