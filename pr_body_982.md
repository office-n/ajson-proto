## 概要
Phase 9.8.2: Network Security Persistence & CLI Integration.
Phase 9.8.1 (3-Layer Defense) を強化し、永続化と管理機能を追加。

## 目的
- 再起動しても承認状態・Allowlist設定を保持する(SQLite)。
- 管理者がCLI経由で安全に許可/拒否を操作可能にする。

## 実装内容
1.  **Persistence**: `ajson/hands/approval_sqlite.py`, `ajson/hands/allowlist.py` (SQLite schema)
2.  **CLI**: `ajson/cli/approval.py` (Wrapper for approval operations)
3.  **Verification**:
    - `tests/test_cli_approval.py`: CLI Logic Mock Tests
    - `tests/test_network_security.py`: Integration with Persistence

## CLI Usage
```bash
python -m ajson.cli list
python -m ajson.cli approve <req_id> --scope "api.example.com"
```

@jarvisrv レビューをお願いします。
