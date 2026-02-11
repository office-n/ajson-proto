# AJSON Administrator Manual
Timestamp: 2026-02-12T00:00:00+09:00 (JST)


## 運用方針
本アプリケーションは「実通信ゼロ」を原則とし、外部通信はすべて **Network Security Layer** (Allowlist/Approval) によって制御されます。

### 1. セキュリティ境界
- **Allowlist**: 静的に許可された宛先のみ接続可能。
- **Approval**: 動的な許可が必要な場合、管理者による承認が必要。
- **Audit**: 全ての通信試行・許可・拒否はログ (`logs/app.log`) に記録される。

### 2. 承認フロー
1. アプリケーションが未許可の通信を試行 -> `ApprovalRequiredError` 発生、リクエスト作成。
2. 管理者が CLI (`ajson.cli list`) でリクエストを確認。
3. 内容を精査し、 CLI (`approve` / `deny`) で判断。
    - **Approve**: 最小限のスコープとTTLを設定すること。
    - **Deny**: 明確な理由を記録すること。

### 3. データ管理
- **データベース**: `data/approvals.db` (SQLite)
- **バックアップ**: 必要に応じて DB ファイルをバックアップしてください。
- **リセット**: データ破損時は DB ファイルを削除し、再起動することでスキーマが再作成されます（既存データは消失）。

### 4. 禁止事項
- `logs/proof/` 配下の改竄（自動検証により検知されます）。
- 本番環境での `--admin` オプション（存在しない場合も含む）や Bypass 操作。
