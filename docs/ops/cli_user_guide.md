# AJSON CLI User Guide
Timestamp: 2026-02-12T00:00:00+09:00 (JST)


## 概要
AJSON CLI (`ajson.cli`) は、アプリケーションのネットワーク制御設定 (Allowlist/Approval) を管理するためのコマンドラインツールです。

## コマンド一覧

### 1. 承認リクエスト一覧 (`list`)
保留中 (Pending) の承認リクエストを表示します。

```bash
python -m ajson.cli list
```

**出力例**:
```
Found 1 pending requests:
ID: 15582f3a-xxxx-xxxx
  Operation: connect api.openai.com
  Reason:    Production API Call
  Created:   2026-02-11T12:00:00+00:00
----------------------------------------
```

### 2. リクエスト承認 (`approve`)
リクエストを承認し、通信を許可します。

```bash
python -m ajson.cli approve <request_id> --scope <host> --ttl <seconds>
```

- **request_id**: リクエストID (必須)
- **--scope**: 許可するホスト名 (必須, 複数可)
- **--ttl**: 有効期間 (秒, デフォルト3600)

**実行例**:
```bash
python -m ajson.cli approve 15582f3a-xxxx --scope api.openai.com --ttl 3600
```

### 3. リクエスト拒否 (`deny`)
リクエストを拒否します。

```bash
python -m ajson.cli deny <request_id> --reason <reason>
```

- **request_id**: リクエストID (必須)
- **--reason**: 拒否理由 (必須)

**実行例**:
```bash
python -m ajson.cli deny 15582f3a-xxxx --reason "Security Policy Violation"
```

## エラー時の対応
- `Error initializing approval store`: データベースファイル (`data/approvals.db`) へのアクセス権限を確認してください。
- `Error ...`: エラーメッセージに従い、入力値やシステム状態を確認してください。
