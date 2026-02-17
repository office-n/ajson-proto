# Phase 9.8.2 Design: Persistence & CLI Integration

## 概要
Phase 9.8.1 の "3-Layer Defense" を永続化し、CLIから安全に許可/拒否を管理できるようにする。

## 1. Persistence (SQLite)
`ajson/hands/approval_sqlite.py` は既に実装済み(PR #59でimport修正済)。
これを利用して、再起動後も Approval Grant を維持する。

- **Database**: `data/approvals.db` (gitignored)
- **Tables**: `requests`, `grants`

## 2. Allowlist Persistence (Future)
現在は `ajson/hands/allowlist.py` の静的リストのみ。
将来的に `data/allowlist.json` 等で動的管理可能にするか検討。
Draft段階では **Env Var Override** (`AJSON_ALLOWED_HOSTS`) で十分か。

## 3. CLI Integration (`ajson-cli`)
管理者が承認操作を行うためのCLIツール。

```bash
# List pending requests
python -m ajson.cli approval list

# Approve a request
python -m ajson.cli approval approve <request_id> --scope "api.openai.com" --ttl 3600

# Deny a request
python -m ajson.cli approval deny <request_id> --reason "Security policy"
```

## 4. Test Plan
- CLI経由で Grant を発行し、`NetworkConnector` が通過することを確認。
- DB削除後の挙動確認。
