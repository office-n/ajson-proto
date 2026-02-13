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
