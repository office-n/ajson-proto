# RUNBOOK_USER.md

## 429エラー発生時の運用手順

### 1. 429エラー（RateLimit / Resource exhausted）が発生した場合
- 直ちにシステムをPAUSE状態にすること。
- PAUSE解除はBossの「再開」指示があるまで行わない。
- 再試行は行わず、別モデルまたは別プロバイダへ切替を検討すること。

### 2. 使用モデルの表記
- 運用上のモデル表記はOpenAIに統一すること。
  - Provider: OpenAI
  - ACT: gpt-4.1-mini
  - PLAN: gpt-4.1
- 内部識別子としての禁止モデルは別途付録に記載し、ユーザー向け文書にはGemini名を出さない。

### 3. 設定ファイルの座標設定
- Vision座標（`model_menu_xy`や`model_items`の座標）は必ず設定すること。
- 未設定の場合はPAUSE状態となるため、設定漏れに注意。

### 4. 監視とログ
- 429エラーの発生源は`/tmp/429_origin.md`に記録されている。
- ログファイル`logs/bridge_daemon.log`を定期的に確認し、異常がないか監視すること。

### 5. PR作成
- 変更内容は`chore/update-model-refs-openai`ブランチで管理し、PRを作成してレビューを受けること。

---

以上の運用手順を遵守し、429エラーによるシステム停止を防止してください。

### 付録：禁止モデル（Google側識別子）
- 禁止モデル（Google側識別子）として管理

### 追記コマンド使用例
- 例（Python版）：
  - `python tools/log_model_switch.py --from "OpenAI:gpt-4.1" --to "Claude:Sonnet" --reason "diff_fail_2x" --result "ok"`