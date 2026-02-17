# M3: Scheduler & SSOT Persistence Design

## 1. 目的
AJSON の自律実行において、タスクのキューイング、非同期実行状態の管理、および操作結果（Evidence）の永続化を実現する。特に「承認待ち」状態を安全に保持し、再開可能にすることを主眼とする。

## 2. 要件
- **タスクキュー管理**: 複数の WorkItem を順次・並列に制御。
- **状態遷移の永続化**: PENDING, RUNNING, COMPLETED, FAILED, WAITING_APPROVAL の各状態を SQLite に保存。
- **エビデンスハッシュ**: 生成された証跡ファイルのハッシュ値を記録し、改竄を検知。
- **再開 (Resume) 機能**: 中断、クォータ切れ、再起動後に特定のタスクから再開可能とする。

## 3. 設計アーキテクチャ

### 3.1 永続化スキーマ (SQLite)
`ajson.db` (またはタスク固有DB) に以下のテーブルを定義：

- **tasks**:
  - `id` (TEXT, PK): Task UUID
  - `parent_id` (TEXT): 親タスクID
  - `status` (TEXT): 状態
  - `objective` (TEXT): 達成目標
  - `created_at` (DATETIME)
  - `updated_at` (DATETIME)
- **evidence_log**:
  - `task_id` (TEXT, FK): 紐づくタスク
  - `file_path` (TEXT): 証跡ファイルの相対パス
  - `sha256` (TEXT): ファイルのハッシュ値
  - `timestamp` (DATETIME)

### 3.2 Scheduler インターフェース
`ajson/core/scheduler.py` に `Scheduler` クラスを実装：

- `enqueue(task: WorkItem)`: キューへの追加。
- `get_next()`: 次に実行すべきタスクの取得。
- `update_status(task_id: str, status: TaskStatus)`: 状態更新。
- `checkpoint(task_id: str)`: 現在の状態とエビデンスの即時保存。

## 4. 受入条件 (Acceptance Criteria)
- [ ] タスクを登録し、再起動後もそのタスク情報が取得できること。
- [ ] 状態が `WAITING_APPROVAL` になった際に、実行が一時停止し DB に保存されること。
- [ ] エビデンスファイルが変更された場合、ハッシュ不一致を検知できること。

## 5. テスト方針
- **Unit Test**: `Scheduler` クラスの DB 操作とロジック検証。
- **Integration Test**: `Orchestrator` との結合、承認フローの擬似再現。
- **Scenarios**: 実行中のプロセス強制終了 → 再起動後の Resume 検証。
