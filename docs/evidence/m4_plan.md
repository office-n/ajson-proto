# M4: Phase 4 Implementation Plan

## 1. 目的 (Objective)
- 永続化されたタスクのスケジューリングと実行（本格運用）
- リトライ、タイムアウト、並行実行制御の実装
- 堅牢なエラーハンドリングとリカバリ

## 2. スコープ (Scope)
### In-Scope
- `Scheduler` クラスの拡張（Retry, Timeout）
- `Worker` クラスの実装（タスク消化）
- 異常系テスト（Crash recovery）
- SQLite上のトランザクション制御強化

### Out-Scope
- 分散実行（Workerの複数台構成）
- GUIダッシュボード
- 外部KVS (Redis等) の導入

## 3. 依存関係 (Dependencies)
- **M3成果物**:
    - `SchedulerStore` (SQLite / `scheduler_store_sqlite.py`)
    - 証跡基盤 (SHA256 / `evidence_hash`)
- **外部ライブラリ**:
    - 特になし（標準 `sqlite3`, `threading` で完結予定）

## 4. テスト方針 (Test Strategy)
- **ユニットテスト**: `tests/test_scheduler_retry.py` 等を追加
- **統合テスト**: `tests/test_scheduler_worker_integration.py`（Producer-Consumerパターン）
- **カオスエンジニアリング**: 
    - `SchedulerStore` の強制ロックや遅延挿入
    - Workerプロセスの擬似クラッシュ

## 5. リスク & Gate (Risk & Gates)
- **Risk**: 
    - トランザクション競合（SQLiteのロック待ちタイムアウト）
    - 再送重複（At-least-once vs Exactly-once のトレードオフ）
- **Gate**: 
    - M3のマージ完了（`feat/m3-scheduler` -> `docs/flash-resume-closeout`）
    - BossのGoサイン (Yes/No)
