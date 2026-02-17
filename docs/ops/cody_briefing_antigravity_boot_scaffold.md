2026-02-13T01:34:00+09:00 (JST)
# Cody Briefing: Antigravity Boot & Scaffold

## 概要
本ドキュメントは、AIアシスタント（Cody等）が本リポジトリで作業を開始する際に、Antigravity（Ants）の自動化エコシステムを理解し、そのルールを遵守するための指示書である。

## 1. 起動トリガーの遵守 (Boot Rules)
作業開始時には必ず以下のシーケンスを走らせること。
- `ants_boot.sh` (FAST) での環境確認。
- `pytest` での機能確認（Deprecation Warning は Error とする）。
- `runlog_<RUNID>.md` の生成と開始時刻（JST）の記録。

## 2. 自動雛形生成 (Launchd Scaffolding)
本環境では macOS の `launchd` による自動雛形生成が導入されている。
- 新規プロジェクトフォルダを作成すると、`scripts/scaffold_on_create.sh` が自動実行される。
- `docs/evidence/runlog_*.md` 等のファイルが自動で用意されるため、これらを「正」として作業記録を開始すること。

## 3. 監査ポイント (Self-Audit)
Cody が自律的に行動する際、以下の 3 点が欠落していないか常に確認せよ。
1. **日本語限定**: すべての入出力は日本語。
2. **JST/Monotonic**: 時刻SSOTは必ず日本時間 + Monotonic秒。
3. **最終報告1回**: 進捗の小出しは厳禁。最後に1回、全ての成果を集約して報告する。

## 4. 証跡と構造
- 全ての証跡は `docs/evidence/` に集約。
- ステータス確認は `docs/ssot/ajson_status_board.md` を参照。
- 作業ログの雛形には必ず `JST ISO8601(+09:00)` を先頭行に含める。
