# Phase 9.6 Kickoff: Realtime API Integration Skeleton

**Timestamp (JST):** 2026-02-11T07:30:00+09:00

## 1. 背景 (Context)
Phase 9.5 にて、音声I/Oの抽象化 (`AudioSource`, `AudioSink`) と Mock `RealtimeVoice` 実装が完了し、E2Eテストの基盤が整いました。
Phase 9.6 では、OpenAI Realtime API への接続準備として、クライアントのインターフェース定義と骨格実装を行います。

## 2. ゴール (Goal)
**「Realtime API接続を安全に導入するための“IF差し替え＋契約テスト＋段階許可”」**

## 3. 制約 (Constraints)
- **NETWORK永続DENY**: 実装中およびテスト実行中、外部APIへの実通信は一切行わない。
- **Mock First**: 全てのリクエスト/レスポンスは Mock で完結させる。
- **Feature Flag**: 実装は `REALTIME_PROVIDER=mock` をデフォルトとし、`openai` 選択時も通信直前でガードする。

## 4. 受け入れ条件 (Acceptance Criteria)
1. **Interfaces Defined**: `RealtimeClient` 等の抽象インターフェースが定義されていること。
2. **Skeleton Implemented**: `RealtimeOpenAI` の骨格（メソッド定義のみ、通信なし）が存在すること。
3. **Dependency Injection**: `RealtimeVoice` が `RealtimeClient` を利用する形にリファクタリングされていること。
4. **Mock E2E PASS**: 新しい構成での Mock E2E テスト (`tests/test_realtime_mock_e2e.py`) がネットワークなしで PASS すること。
5. **Evidence**: 設計とテスト結果が証跡として残されていること。
