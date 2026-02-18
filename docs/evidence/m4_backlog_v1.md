# Backlog v1 (M4 / M3.1 / X)
Date: 2026-02-18
Status: Draft (SSOT Backlog)

## M4 (Remote Bridge)
- M4-1 pairing_code API（発行/再生成/TTL/無効化）
  受入条件: TTL 10分前後で発行され、再生成で旧コードが即時失効し、発行/再生成/登録が監査に残る。
  依存: 監査イベントの共通スキーマ（X-3）。
  工数: 6h
- M4-2 短命Bearer（発行/失効/ローテ、viewer/approver分離）
  受入条件: 5–15分TTLのトークンが発行/失効/ローテ可能で、viewer/approver が分離される。
  依存: M4-1, X-3。
  工数: 8h
- M4-3 tailscaleOnly 既定＋例外は承認ゲート
  受入条件: 既定が `tailscaleOnly=true` で固定され、解除は PENDING_APPROVAL を経由する。
  依存: 承認ゲート実装（M4-4 or 既存機構）。
  工数: 6h
- M4-4 HTTPS 既定＋証明書生成/更新（上書き承認）
  受入条件: `httpsEnabled=true` が既定で、証明書生成/更新フローが実装され、上書きは承認が必須。
  依存: 承認ゲート実装（M4-3）。
  工数: 10h
- M4-5 Terminal Gateway（attach/detach/write/resize + stream）
  受入条件: WS/SSEで attach/detach/write/resize が可能、`terminal:data` ストリームが提供される。
  依存: M4-2, X-3。
  工数: 16h
- M4-6 Remote View（最小UI/API、閲覧権限制御）
  受入条件: 最小UI/APIで閲覧が可能で、Viewer 権限のみの閲覧が制御される。
  依存: M4-2, M4-5。
  工数: 12h

## M3.1 (Scheduler / Autorun 拡張)
- M3.1-1 autorun テーブル（SQLite永続、再起動復元）
  受入条件: SQLite に永続化され、再起動後に状態復元できる。
  依存: 既存 SSOT テーブル定義。
  工数: 8h
- M3.1-2 OS scheduler 同期（許可制、削除/更新は承認）
  受入条件: OS スケジューラへ同期でき、削除/更新は承認ゲートを通過する。
  依存: 承認ゲート実装（既存）。
  工数: 12h
- M3.1-3 autorun→task生成→証跡固定
  受入条件: autorun から task が生成され、証跡が SSOT に固定される。
  依存: M3.1-1, X-3。
  工数: 10h

## X (横断)
- X-1 Skills Global/Project API（参照ログ/削除承認）
  受入条件: Global/Project スコープで参照可能、削除は承認ゲートを必須とする。
  依存: 承認ゲート実装（既存）。
  工数: 10h
- X-2 Secrets を Keychain 層へ分離（SSOTに秘密値を残さない）
  受入条件: Secret 値は Keychain に保存され、SSOT には参照IDのみ残る。
  依存: Keychain 利用可能環境。
  工数: 8h
- X-3 Remote 操作を監査イベント化（attach/detach/approval/token）
  受入条件: attach/detach/approval/token 操作が監査イベントとして SSOT に固定される。
  依存: 監査イベント基盤（既存）。
  工数: 10h

---

## 工数合計
- M4: 58h
- M3.1: 30h
- X: 28h
- Total: 116h
