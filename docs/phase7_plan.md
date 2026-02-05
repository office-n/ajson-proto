# phase7_plan.md — AJSON Phase 7 (Architecture Pivot & Cost Optimization)
Timestamp: 2026-02-06T01:04:18+09:00  
SSOT: DECISION-20260206-01 (Boss/Cody Audit)

## 0. Decision SSOT (確定)
- Antigravity: Production Component → Dev-Only Sandbox（運用自動化フローから除外）
- Automation Strategy: API-First
  - Brain: OpenAI(ChatGPT API) + Gemini API が思考・計画
  - Hands: AJSON 内蔵 Tool Runner（File I/O / Shell Command）＋ BrowserPilot（Headless Browser）
- Budget-First Policy（目標: 月額 5,000〜10,000円の範囲で運用）
  - Default Brain(OpenAI): gpt-4o-mini（低コスト）
  - High Cost Fallback(OpenAI): gpt-4o（要承認）
  - Default Eyes(Gemini): flash系（大量読込/ログ解析/全量スキャン等）
  - Circuit Breaker: 日次消費が $3.00 を超える予測が出た時点で自律ループ停止→Approval Required

## 1. Scope (Phase 7 で実装するもの)
### Must
1) LLM Gateway
- Provider: DryRun / OpenAI / Gemini
- Model preset: OpenAI (mini/4o), Gemini (flash/pro) を設定で切替
- 監査ログ: 全リクエストを構造化記録（provider/model/usage/cost/理由/例外/approval）
2) CAMR (Cost-Adaptive Model Routing)
- タスク種別/入力サイズ/失敗回数/品質要件に基づき自動選択
- 高コストモデル（gpt-4o / Gemini Pro）は「要承認」でのみ実行
3) Cost Tracker + Budget Guard
- OpenAI: レスポンスの usage（input/output tokens 等）を記録し、価格表から推計コスト算出
- Gemini: レスポンスの usage_metadata（prompt/candidates/total 等）を記録
- 日次$3.00超過予測で Circuit Breaker 発火 → Approval Required

### Non-goals (Phase 7 では"土台のみ")
- BrowserPilot のフル自律航行（Phase 8 以降で Gate 化）
- Tool Runner の危険操作（削除/課金/不可逆）は Phase 7 では「拒否/承認必須」ポリシーのみ先行

## 2. Architecture Overview
```
AJSON Core
  -> Planner (LLM)  … LLM Gateway 経由
  -> Executor (Hands)
      - Tool Runner (file/shell) [policy-gated]
      - BrowserPilot (headless browser) [policy-gated]
  -> Auditor (post-check)
  -> Cost & Budget Guard (always-on, pre/post)
```

### 2.1 Request/Response 正規化
- LLMRequest:
  - task_id, role (planner/eyes/auditor), system, user_input
  - context_refs (files/logs), constraints (budget/policy), desired_quality
- LLMResponse:
  - text
  - usage: {input_tokens, output_tokens, total_tokens, cached_tokens?} ※providerにより欠損あり
  - provider_request_id
  - cost_estimate_usd (price_table から計算できる場合のみ)

## 3. Pricing & Cost Estimation (設定可能/スナップショット化)
### 3.1 OpenAI (tokenベース)
- gpt-4o-mini: Input $0.15 / 1M, Output $0.60 / 1M
- gpt-4o:      Input $2.50 / 1M, Output $10.00 / 1M

計算式（推計）:
```
cost_usd = (input_tokens/1e6)*price_in + (output_tokens/1e6)*price_out
```

### 3.2 Gemini (token情報は usage_metadata、価格表は provider別に差し替え)
- Gemini Developer API pricing はモデル世代で更新され得るため、price table を設定ファイルで管理する
- 参考: Vertex AI では Gemini 1.5 Flash/Pro の料金が公開されている（単位が文字/秒等）

方針:
- Phase7 では「usage の記録」と「price table による推計」を分離し、
  - usage が取れる → cost推計
  - usage が取れない/単位不一致 → cost_estimate_usd を null とし、Budget Guard は "確定値なし" として保守的に停止（Approval Required）へ

## 4. CAMR (Model Router) Policy
### 4.1 Roles
- planner (Brain): OpenAI gpt-4o-mini default
- eyes (大量読込/解析): Gemini flash default
- auditor (検証/差分レビュー): 原則 flash/mini、必要時のみ上位（要承認）

### 4.2 Auto-routing ルール（初期・決定論）
```python
if task.class == "bulk_read/scan/log_analyze":
    use Gemini flash (eyes)
elif task.class in ["code_change","refactor","bugfix","plan"]:
    use OpenAI gpt-4o-mini (planner)

# upgrade candidates（要承認）:
#   - 失敗が連続（例: 2回）かつ原因が「能力不足」と分類された場合
#   - 仕様上「高精度が必須」と明示された場合
# -> OpenAI gpt-4o / Gemini pro を候補にし、ApprovalRequired を発行して停止
```

※「能力不足判定」は Phase7 では"ヒューリスティック"固定（例: 連続失敗 + same-constraint + test fails）とし、学習的最適化は Phase8 以降で Gate 化。

## 5. Budget Guard (Circuit Breaker)
- 日次集計キー: {date, provider, model}
- 予測: 当日累積 + 直近N回の平均コスト × 予想残リクエスト数
- 発火条件: predicted_daily_cost_usd > 3.00
- 発火時動作:
  1) 自律ループ停止
  2) ApprovalRequired を発行（理由: budget_breaker）
  3) 監査ログに記録（現在累積/予測/根拠）

OpenAI 側の usage 集計/照合は、将来的に Usage API と突合できる（Phase7では"内部SSOT"優先）

## 6. File Layout (提案)
```
ajson/
  llm_gateway/
    __init__.py
    config.py           # env + model presets + price tables
    types.py            # LLMRequest/LLMResponse/Usage/ApprovalRequired
    gateway.py          # entrypoint (guard + provider select + audit)
    router.py           # CAMR policy
    budget_guard.py     # daily budget + prediction + breaker
    cost_tracker.py     # usage normalize + cost estimate + aggregation
    audit.py            # structured audit events (jsonl or DB adapter)
    providers/
      dry_run.py
      openai_provider.py
      gemini_provider.py
  tools/
    runner.py           # tool runner interface (Phase7: policy-only)
    policy.py           # allow/deny + approval gate
  browser_pilot/
    __init__.py
    policy.py           # allow/deny + approval gate (Phase7: stub)

tests/
  test_llm_gateway_dry_run.py
  test_budget_guard_breaker.py
  test_router_policy.py
  test_no_network_calls.py

docs/
  phase7_plan.md        # ←この文書
```

## 7. Execution Steps (Gate)
### Gate-7.1 (Phase7-1)
- LLM Gateway skeleton + DryRun default
- 監査ログ（最低限） + usage記録（OpenAI/Geminiは"取得できる範囲"）
- Cost Tracker + Budget Guard（$3 breaker）
- Router（決定論）
- pytest: 完全オフライン、ネットワーク呼び出しなし

Acceptance Criteria:
- DRY_RUN で end-to-end が動く
- LLM_ENABLE_PAID != "1" の時、外部API呼び出しを必ず遮断し監査に理由が残る
- predicted_daily_cost_usd > 3.00 で ApprovalRequired になる
- 監査ログに (provider, model, usage, cost_estimate, decision, breaker_reason) が残る

### Gate-7.2 (Phase7-2)
- OpenAI/Gemini の実接続（ただし要承認・最小検証のみ）
- 価格表のスナップショット固定（モデル名/単価を config で固定、変更はPRレビュー必須）

## 8. Open Questions (SSOT更新が必要なもの)
- Gemini の「flash/pro」モデル名（Gemini API で運用する正式名）と価格表の確定
- BrowserPilot の権限境界（ログイン/決済/削除/デプロイ等の禁止領域と承認条件）

## 9. References
- OpenAI Platform: Models GPT-4o-mini, GPT-4o (pricing and capabilities)
- Google Gemini API: Developer pricing and usage metadata structure
- DECISION-20260206-01: Boss/Cody audit confirming API-First strategy

---

**Next Steps**: Implement Gate-7.1 (LLM Gateway baseline) on this branch.
