# AJSON Initial Prototype MVP

**AJSON (Agent-driven JSON Orchestration System)** の初期プロトタイプMVP実装です。

## MVP範囲

- **デフォルト動作**: DRY_RUN（モック応答）で全フローが動作
- **OpenAI API**: 環境変数`OPENAI_API_KEY`設定時のみ有効（オプショナル）
- **機能**:
  - Mission Console（Web UI）でミッション入力
  - 状態機械による自動実行（CREATED→DONE）
  - 承認ゲート検出（Deploy/Delete/DB/権限/請求/外部公開）で自動停止
  - SQLiteベースのSSOT（全操作を追跡）
  - 安全なツール実行（allowlist/denylist方式）

## 安全ルール（絶対厳守）

### 禁止事項
- **破壊コマンド**: `rm`, `rd`, `del`, `format` 実行禁止
- **権限変更**: `chmod`, `chown`, `sudo` 実行禁止
- **ディスク操作**: ディスクフォーマット、パーティション変更禁止
- **外部公開**: 本番デプロイ、外部公開、課金処理禁止
- **作業ディレクトリ**: 指定ディレクトリ外へのアクセス禁止

### 保護機構
- **Denylist**: 禁止コマンドを検出時、即座にエラーで中断
- **Allowlist**: 許可されたコマンドのみ実行可能
- **承認ゲート**: 危険操作検出時はPENDING_APPROVALで必ず停止

## 起動手順

### 1. 仮想環境の有効化
```bash
source venv/bin/activate
```

### 2. サーバー起動
```bash
uvicorn ajson.app:app --reload --port 8000
```

### 3. ブラウザで確認
```
http://localhost:8000/console
```

### 4. テスト実行
```bash
pytest tests/ -v
```

## プロジェクト構成

```
ajson-proto/
├── ajson/
│   ├── app.py              # FastAPI エントリーポイント
│   ├── db.py               # SQLite CRUD
│   ├── models.py           # Pydantic モデル
│   ├── orchestrator.py     # 状態機械
│   ├── roles/
│   │   ├── jarvis.py       # プランニングロール
│   │   └── cody.py         # 監査ロール
│   ├── tools/
│   │   └── runner.py       # ツール実行（allow/deny）
│   └── llm/
│       ├── mock.py         # モック応答
│       └── openai_responses.py  # OpenAI API
├── tests/
│   ├── test_state_machine.py
│   └── test_denylist.py
├── missions/
│   └── sample_mission.json
├── .env.example
├── README.md
└── requirements.txt
```

## 状態遷移

```
CREATED → PLANNED → PRE_AUDIT → EXECUTE → POST_AUDIT → FINALIZE → DONE
                                   ↓
                          PENDING_APPROVAL (承認が必要な場合)
```

## 環境変数

`.env`ファイルを作成し、必要に応じて設定：

```bash
cp .env.example .env
```

- `LLM_MODE`: `DRY_RUN` または `OPENAI`（デフォルト: DRY_RUN）
- `OPENAI_API_KEY`: OpenAI APIキー（オプショナル）
- `LLM_MODEL`: モデル名（デフォルト: gpt-4）
- `WORK_DIR`: 作業ディレクトリ（デフォルト: ./workspace）

## サンプル実行

### Python Demo Script (推奨)
```bash
# ターミナル1: サーバー起動
cd ajson-proto
source venv/bin/activate
uvicorn ajson.app:app --reload --port 8000

# ターミナル2: デモ実行
source venv/bin/activate
python demo.py
```

### curl Examples
```bash
# サンプルミッション作成
curl -X POST http://localhost:8000/missions \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Mission","description":"Run pytest tests","attachments":[]}'

# ミッション状態確認
curl http://localhost:8000/missions/1

# 承認（必要な場合）
curl -X POST http://localhost:8000/missions/1/approve \
  -H "Content-Type: application/json" \
  -d '{"decision":"yes"}'
```


## 開発ガイド

### データベース確認
```bash
sqlite3 ajson.db "SELECT * FROM missions;"
sqlite3 ajson.db "SELECT * FROM steps;"
sqlite3 ajson.db "SELECT * FROM tool_runs;"
```

### ログ
すべての操作は`steps`および`tool_runs`テーブルに記録されます。

## ライセンス

MIT License
