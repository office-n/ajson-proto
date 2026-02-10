Timestamp (JST): 2026-02-10T13:55:00+09:00

# Phase 9.5 Kickoff: Voice & Ops Stability

## 1. 背景 (Background)
- **Incident**: PR#39にて `jarvisrv` がMerger代行を行う運用逸脱が発生。
- **Fix**: PR#40 (Policy) / PR#41 (Evidence) により、`office-n` によるマージ強制を技術的・運用的に確立。
- **Current Status**: main HEAD (`dfe3aeb...`) は整合しており、Merger Policy は遵守されています。

## 2. ゴール (Goal)
- **Voice実装の深化**: Phase 9.4のStubから、最小限の実装（受け入れ条件を満たすレベル）へ移行。
- **運用ポリシーの定着**: "Merger=office-n" ルールの継続的な遵守と、物理的STOP機構の運用実績作り。

## 3. 進め方 (Process)
- **禁止事項**: Bypass (--admin), `jarvisrv` によるマージ, 外部ネットワーク接続。
- **承認フロー**: `jarvisrv` (Approve) → `office-n` (Squash Merge)。
- **Network**: 永続DENY（ローカル作業＋GitHub UI確認のみ）。

## 4. 提案 (Proposals)
ボス判断をお願いします（A/B いずれかを選択）。

### A案: Voice 実装深化 (Deep Dive)
- **内容**: Stub化されている `RealtimeVoice` クラスを、実際の音声入出力（または模擬データによるE2E）が可能になるよう実装を進める。
- **メリット**: Phase 9 の核心機能であるVoice対話の具体化。
- **リスク**: 外部API（OpenAI Realtime API等）への依存設計が必要（Mock前提で進める）。

### B案: 次ロードマップ項目 (Next Roadmap)
- **内容**: Dispatcherの強化、あるいは監査ログの堅牢化など、Voice以外の周辺機能を固める。
- **メリット**: 足回りの強化により、後のVoice実装がスムーズになる。
- **リスク**: Voice機能の可視化が遅れる。

## 5. ボス判断ポイント
- [ ] **A案**: Voice 実装深化
- [ ] **B案**: 次ロードマップ項目

## 6. 完了条件
- 選択された案に基づく実装PRが作成され、新ポリシー通りにマージされること。
