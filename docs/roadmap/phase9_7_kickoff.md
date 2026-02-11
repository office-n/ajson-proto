# Phase 9.7 Kickoff: Realtime API Logic (No Network)

## 1. 目的
Reference: AJSON Spec v2.1
Realtime API (WebSocket) 接続を行うための「セッション状態管理ロジック」を実装し、
**実際に外部接続することなく** プロセスの健全性とエラーハンドリングを確立する。

## 2. スコープ (Kickoff)
- **Session State Machine**: `INIT` -> `CONNECTING` -> `READY` -> `ERROR` -> `CLOSED`
- **Dependency Injection**: `RealtimeClient` (Mock/Stub) を注入可能にする。
- **Feature Flag**: `ENABLE_REALTIME_NETWORK` (Default: False)
  - `False` の場合、`connect()` は即座にMock動作（またはNo-op）となり、物理ソケットは開かない。

## 3. 非ゴール
- 実際の OpenAI Realtime API への接続 (Phase 9.8 以降)。
- 音声の双方向ストリーミング (Logicのみ先行実装)。

## 4. 実装計画
1. `ajson/core/realtime_session.py`: `RealtimeSession` クラス実装。
2. `tests/test_realtime_session.py`: 状態遷移の単体テスト。

以上
