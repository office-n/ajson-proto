# Evidence: Phase 9.7 Kickoff (Logic Only)
Timestamp: 2026-02-11T13:30:00+09:00 (JST)

## 1. Kickoff 概要
- **Branch**: `feat/phase9-7-realtime-logic`
- **Focus**: Realtime API セッションの状態遷移ロジック実装。
- **Constraint**: **NETWORK PERMANENT DENY** (外部通信なし)。

## 2. 設計要点
- **State Machine**:
  - `INIT`: 初期状態。
  - `CONNECTING`: 接続試行中（Mockでは即READYへ）。
  - `READY`: メッセージ送受信可能。
  - `ERROR`: エラー発生（再試行ロジックの起点）。
  - `CLOSED`: セッション終了。
- **Safety**:
  - `feature_flag` により、実ネットワーク接続コードへのパスを物理的に遮断（`if not allowed: return`）。

## 3. 検証方針
- `pytest` により、以下のシナリオを検証する:
  - 正常系: INIT -> CONNECTING -> READY -> CLOSED
  - 異常系: CONNECTING -> ERROR -> CLOSED
  - ガード: `connect()` 呼び出し時にFlag=Falseなら外部通信が発生しないこと。

以上
