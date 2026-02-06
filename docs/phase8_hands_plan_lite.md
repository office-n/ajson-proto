# Phase 8: Hands導入計画（拡張版）

**タイムスタンプ**: 2026-02-07T01:54:00+09:00（Asia/Tokyo）  
**拡張内容**: Policy強化（allowlist/denylist）+ Tool Runner監査ログ安定化 + BrowserPilot抽象化

---

## 概要

Phase 8拡張では、DRY_RUN優先の原則を維持しながら、Policy決定ロジックと監査ログを強化しました。

---

## 拡張内容

### 1. Policy強化（allowlist/denylist）

**PolicyDecision enum追加**:
- `ALLOW`: 安全なreadonly操作、即座に実行可能
- `DRY_RUN_ONLY`: シミュレーション可能だが実行不可
- `REQUIRE_APPROVAL`: 実行前に明示的な承認が必要
- `DENY`: 禁止操作、実行不可

**OperationCategory enum追加**:
- `READONLY`: 読み取り専用、状態変更なし
- `DESTRUCTIVE`: データ削除・変更
- `IRREVERSIBLE`: 取り消し不可
- `PAID`: 課金API
- `NETWORK`: 外部ネットワーク呼び出し
- `UNKNOWN`: 分類不能

**Allowlist（安全操作）**:
```python
ALLOWLIST = [
    "ls", "cat", "grep", "rg", "find",
    "pytest -q", "pytest --collect-only",
    "git status", "git log", "git diff",
]
```

**Denylist（禁止操作）**:
```python
DENYLIST = [
    "rm -rf",
    "git push --force", "git push -f",
    "git tag -d", "git reset --hard",
    "docker rm",
    "DROP DATABASE", "DROP TABLE",
    "curl", "wget", "nc", "telnet",  # ネットワーク操作禁止
]
```

### 2. Tool Runner監査ログ安定化

**JSON-serializable audit log**:
- 全監査ログをJSON形式で保存可能
- テストで比較・検証可能な安定した形式

**PolicyDeniedError追加**:
- denylist違反時に専用エラーを投げる
- 監査ログに違反理由を記録

**監査ログ例**:
```json
{
  "operation": "ls {'-la': true}",
  "decision": "allow",
  "category": "readonly",
  "reason": "Allowed: matches allowlist",
  "dry_run": true,
  "result": {...}
}
```

### 3. BrowserPilot抽象化

**BrowserStep抽象化**:
- アクション型（NAVIGATE, CLICK, TYPE, SCREENSHOT等）
- パラメータのマスキング自動化（API key, password）

**DRY_RUN planning**:
```python
steps = [
    BrowserStep(BrowserAction.NAVIGATE, {"url": "..."}),
    BrowserStep(BrowserAction.CLICK, {"selector": "#button"}),
]
result = pilot.run(steps)  # DRY_RUN: 実行計画のみ返す
```

**Playwright optional**:
- Playwright存在時のみ実実行
- 非存在時は自動的にDRY_RUNへフォールバック

---

## テスト追加

### 追加テスト数: 10個

**test_hands_policy_allowdeny.py** (4 tests):
- Allowlist操作がALLOW判定
- Denylist操作がDENY判定
- Network操作がDENY判定
- Unknown操作がDRY_RUN_ONLY判定

**test_hands_runner_audit.py** (3 tests):
- JSON-serializable監査ログ
- Allowlist操作の実行
- Denylist操作のPolicyDeniedError

**test_browserpilot_dryrun.py** (3 tests):
- DRY_RUN execution plan
- JSON-serializable監査ログ
- Secret masking（API key, password）

---

## セキュリティ原則（継続）

1. **機密情報の非露出**: API key/tokenは環境変数またはKeychain経由のみ
2. **可逆性の確保**: 不可逆操作は承認ゲート必須、force禁止
3. **課金の明示**: 課金APIコールは事前承認必須、日次予算上限強制
4. **ネットワーク禁止**: 外部ネットワーク呼び出し（curl, wget等）は一律DENY

---

## 次ステップ

**Phase 8.2**: Approval UI連携
- フロントエンドからの承認フロー実装
- 監査ログのUI表示

**Phase 8.3**: BrowserPilot実行器追加
- Playwright統合
- Screenshot証跡の自動保存
