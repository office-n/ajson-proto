# Ants Capacity Limits (SSOT)
Last Updated: 2026-02-13T02:15:00+09:00 (JST)

## 概要
ChainRun における連鎖タスク処理能力（キャパシティ）の限界値を定義・記録する文書。
各RUNの結果に基づき、次回のタスク積載量を決定する根拠 (Single Source of Truth) とする。

## 1. Current Capacity Limit (現在値)
- **TimeBudget**: **90-150分** (Max Duration)
  - 時間ベース運用に完全移行。
- **Bottleneck**: **AI Model Quota / External API Constraints**

## 2. 稼働実績ログ (Recent Runs)

| RUNID | Tasks | Bridge (中断) | Limit Reached (終了要因) | Result |
| :--- | :--- | :--- | :--- | :--- |
| v1.8 | 8 | 0 | Toolchain (GH API) | Success (Manual PR) |
| v1.9 | Loop 5 | 0 | TimeBudget (90min) | Success (Manual PR) |
| **v2.1** | **Full** | **0** | **TimeBudget (InProgress)** | **Running** |

## 3. Limit Factors (限界要因パターン)

### A. Context Window (トークン不足)
- 発生: v1.6 (High Load)
- 特徴: 会話履歴の圧縮により指示を忘れる。

### B. Time Budget (時間切れ)
- 発生: v1.9 (Scheduled)
- 特徴: 予定時間を使い切る。

### C. Toolchain Stability (ツール破損)
- 発生: v1.8, v1.9
- 特徴: `gh` CLI が PR を作成できない。

### E. AI Capacity (外部クォータ)
- 発生: 2026-02-12
- 特徴: Gemini 1.5 Pro (High) quota exceeded.
- 再開予定: 2026/02/15 01:00:12 (JST)
- 対策: `flash` (Fast) モデルへの切り替え、または待機。

## 4. Next Run Strategy (次回戦略)
- **Mode**: Maintenance Loop (TimeBudget 90-150min)
- **Tasks**: Backlog Loop 継続 (Documentation, Test Coverage)。
