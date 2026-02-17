## 受入条件（要点）
- SQLite SchedulerStore によるタスク永続化の実現
- 状態遷移 (READY, RUNNING, DONE, etc.) の整合
- 証跡ハッシュ (SHA256) による改竄防止基盤

## 実装範囲
- SQLite SchedulerStore: enqueue, dequeue, ack, nack, hold
- WAITING_APPROVAL 状態の検出と迂回ロジック
- **証跡チェーン**: `evidence_chain` テーブルによる改竄検知 (SHA256 + prev_hash 連結)

## 検証結果
- **ベースラインSSOT**: 146 passed (PR #60/#61)
  - 証跡: runlog_v1_3_2026-02-11.md (Archived in evidence-archive/m3-runlogs-keep)
- **M3 (feat/m3-scheduler)**: **152 passed** (新規テスト6件込み)
  - 証跡: `docs/evidence/walkthrough_m3_final.md`
- **boot/preflight/phase10_audit**: **PASS**
  - 証跡ログ: `docs/evidence/audit_report_20260217_192455.md`

## 変更ファイルの要約
- `ajson/core/scheduler_store_sqlite.py`: SQLite 永続化層の新規実装
- `ajson/core/scheduler.py`: 永続化層への切り替え
- `docs/evidence/boss_op_card_m3_merge.md`: ボス操作カードの追加

@jarvisrv レビュー依頼
判断点：
1) SSOT表記（146 baseline / 151 M3追加）をこの形で固定して良いか
2) scheduler_tasks schema（最小項目）と state 遷移がMVPとして妥当か
3) evidence_hash 正規化ルール（何を含め/除外するか）が監査目的に合うか
- **Runlog**: docs/evidence/runlog_m3_truegreen_20260217_205552.md
- **Audit**: ALL PASS (Exit 0)
