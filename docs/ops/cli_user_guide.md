# AJSON CLI User Guide
Last Updated: 2026-02-13T21:50:00+09:00 (JST)

## 概要
AJSON CLI (`ajson.cli`) は、アプリケーションのネットワーク制御設定 (Allowlist/Approval) を管理するためのコマンドラインツールです。
本システムは **NETWORK DENY** (既定拒否) を原則としており、明示的な許可なしに外部通信を行うことはできません。

## 典型的な利用フロー
1. **通信遮断の発生**: アプリケーションが未許可の外部接続を試行し、`ApprovalRequiredError` が発生して停止またはリトライ待ちになります。
2. **リクエスト確認**: 管理者が `python -m ajson.cli list` を実行し、保留中のリクエスト ID を取得します。
3. **内容精査**: 接続先ホスト、理由、および発生元コードを確認します。
4. **承認実行**: 正当性が認められる場合、`python -m ajson.cli approve <ID> --scope <HOST> --ttl <SEC>` を実行します。
5. **再試行/継続**: インメモリキャッシュまたは DB が更新され、アプリケーションの通信が可能になります。

## コマンド一覧

### 1. 承認リクエスト一覧 (`list`)
保留中 (Pending) の承認リクエストを表示します。

```bash
python -m ajson.cli list
```

### 2. リクエスト承認 (`approve`)
リクエストを承認し、一定期間の通信を許可します。

```bash
python -m ajson.cli approve <request_id> --scope <host> --ttl <seconds>
```

- **--scope**: 許可するホスト名 (完全一致または `*` ワイルドカード)。
- **--ttl**: 有効期間 (秒)。0 指定で無期限（非推奨）。

### 3. リクエスト拒否 (`deny`)
リクエストを拒否し、通信を永続的に遮断します（再試行には再リクエストが必要）。

```bash
python -m ajson.cli deny <request_id> --reason <reason>
```

### 4. 許可リスト管理 (`allowlist`)
静的な許可ルールを追加します。アプリケーション起動時から有効になります。

```bash
python -m ajson.cli allowlist add <host> <port> --reason <reason>
```

---

## 失敗例とトラブルシューティング
- **"Invalid Request ID"**: 指定された ID が存在しないか、既に処理済みです。`list` コマンドで最新の ID を確認してください。
- **"Missing required argument"**: `--scope` や `--reason` など、必須フラグが漏れています。
- **"Database is locked"**: 他のプロセスが書き込み中です。時間を置いて再試行してください。
- **"Network Deny Violation"**: CLI 自体が未許可のネットワーク操作を試行した場合に発生します（CLI はローカル DB 操作のみを行う設計です）。

## 終了コード (Exit Codes)
- **0**: 成功 (Success)
- **1**: 致命的エラー (Fatal Error / Exception)
- **2**: バリデーションエラー (Input Validation Fail / Invalid arguments)
- **130**: ユーザーによる中断 (SIGINT)

## NETWORK DENY ポリシー
本 CLI を介した操作はすべてログに記録されます。
「理由」の入力は必須であり、監査証跡として `docs/evidence/` に残ることが期待されます。
既定で外部へのあらゆる `socket.connect` はフックされ、本 CLI で許可された例外のみが通過します。
