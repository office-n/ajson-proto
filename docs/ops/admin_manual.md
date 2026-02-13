# AJSON Administrator Manual
Last Updated: 2026-02-13T21:55:00+09:00 (JST)

## 運用方針
本アプリケーションは「実通信ゼロ」を原則とし、外部通信はすべて **Network Security Layer** (Allowlist/Approval) によって強制制御されます。

### 1. 承認操作の詳細
管理者は CLI を用いて以下の手順でネットワークアクセスを制御します。
- **リクエストの確認**: `python -m ajson.cli list`
  - 通信先 (Host)、理由 (Reason)、作成日時を確認。
- **承認の実施**: `python -m ajson.cli approve --scope <HOST> --ttl <SEC>`
  - 原則として「最小権限」を適用すること。必要以上のドメインや長時間 (TTL) を許可しない。
- **拒否の実施**: `python -m ajson.cli deny --reason <REASON>`
  - 不審な通信や、プロジェクト方針に合わない通信は即座に拒否する。

### 2. 証跡の読み方 (Audit Log & Runlog)
- **Application Logs (`logs/app.log`)**:
  - `[ALLOWED]`: 許可された通信。
  - `[DENIED]`: 遮断された通信。
  - `[REQUESTED]`: 承認待ちリクエストの発生。
- **Runlog (`docs/evidence/runlog_...md`)**:
  - 作業ごとの時刻、コマンド、結果が記録される。
  - **OS_JST** / **MONO** 時刻により、作業の連続性と改ざんの有無を検証する。

---

## 5. トラブルシューティング（環境・端末）

### 5.1 PTY ホストエラー（黄帯）への対処
VS Code 端末で「PTY ホストが予期せず終了しました」という警告（黄帯）が出た場合は、以下の順で復旧を試みること。
1. **最短復旧**: 黄帯内の「PTY ホストを再起動」ボタンをクリック。
2. **ウィンドウ再読込**: `Developer: Reload Window` コマンドを実行。
3. **完全再起動**: VS Code を一旦終了（Quit）し、再起動する。

### 5.2 再発防止策（端末負荷軽減）
PTY ホストのクラッシュは、大量のプロセス起動や過度な端末出力が原因となる。以下を厳守すること。
- **Always run 抑制**: バックグラウンド実行（Always run）は原則 OFF とし、必要な時だけ手動で開始する。
- **プロセス制限**: 同時に走らせるバックグラウンドコマンドは原則「最大1本」とする。
- **出力抑制**: テスト実行時は `-q` (quiet) オプションを使い、詳細はログファイルへ出力する。
  - 例: `pytest -q tests/ > logs/test_result.log 2>&1`
- **バッチ実行**: 長時間のループ検証は、10回程度のバッチ実行＋タイムアウト設定で分割する。

### 3. 禁止事項 (Prohibited Operations)
- **データベースの直接編集**: `approvals.db` をコマンド外の手法で直接書き換える行為。
- **Bypass オプションの使用**: コード内での `allow_network=True` の強制設定や、ガードレールの無効化。
- **Wildcard Allow-All**: `--scope "*"` など、すべての通信を許可する設定。

### 4. 復旧手順 (Recovery Procedures)
- **データベース破損**: 
  - `data/approvals.db` を削除してアプリケーションを再起動。初期スキーマが自動作成される。
- **認証エラー (GitHub)**:
  - `gh auth logout` 後に `gh auth login` を再試行。
- **ガードレールによる意図しない拒否**:
  - プロジェクトの `scripts/ants_preflight.sh` を確認し、禁止文字列やフォーマット違反がないか検査。

### 5. NETWORK DENY 体系
本システムは `ajson/core/network.py` における `socket` レベルのモンキーパッチにより、物理的に外部通信を遮断します。
例外は `ApprovalStore` (SQLite) に登録されたエントリのみです。
この設計により、開発者のミスによる意図しない外部へのデータ流出を未然に防ぎます。
