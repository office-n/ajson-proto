# 補遺: AGI Cockpit転用仕様（Remote Bridge / Cockpit / Approval Gate）
Version: 1.0
Date: 2026-02-18
Status: Proposed (SSOT Appendix)

## 0. 目的
AGI cockpit解析で得た Remote Bridge / Terminal / Skills / Autorun / Secrets の設計要素を、
AJSON v2.1 の実装判断がブレない粒度で固定する。

---

## 1. Remote Bridge（実装仕様）
### 1.1 ペアリング
- `pairing_code` を発行可能にする（再生成可）。
- TTL は短命（目安: 10分）。
- 登録成功時点で旧コードは即時失効。
- 発行/再生成/登録の各イベントを監査に記録する。

### 1.2 認証
- `Authorization: Bearer <short_lived_token>` を既定とする。
- TTL は 5–15分、ローテーションと失効が必須。
- **Viewer / Approver の権限分離**を必須要件とし、別トークン運用を許容する。
- 発行/失効/ローテーション/権限変更を監査に記録する。

### 1.3 ネットワーク既定
- `tailscaleOnly=true` を既定値とする。
- LAN 公開は例外扱いで、承認ゲート（PENDING_APPROVAL）を通過しない限り禁止。

### 1.4 HTTPS 既定
- `httpsEnabled=true` を既定値とする。
- 証明書の生成/更新フローを規定する。
- 証明書の上書きは承認ゲートを必須とする。

### 1.5 監査（Evidence/SSOT）
- pairing 発行/再生成/登録、token 発行/失効/ローテーション、接続元、
  権限操作を Evidence として SSOT チェーンに固定する。

---

## 2. Cockpit 実体（Remote View の実装単位）
### 2.1 Terminal Gateway
- `attach` / `detach` / `write` / `resize` を I/F として公開する（WS または SSE）。
- `terminal:data` 相当のストリーム仕様を規定する。
- attach/detach を監査イベント化（SSOT）する。

### 2.2 History
- 出力履歴は「保存先 + ハッシュ参照」を SSOT に固定する。
- 本文の暗号化、および期限（7/30/90日）をオプション化する。

### 2.3 Status Snapshot
- task 状態のローカルスナップショットを規定する。
- 再起動復元の根拠として SSOT に記録する。

---

## 3. 承認ゲート接続（PENDING_APPROVAL）
以下の操作は必ず PENDING_APPROVAL に接続し、承認後のみ実行可能とする。
- `tailscaleOnly` 解除
- LAN 公開
- 証明書の上書き
- 端末（デバイス）追加/削除
- 永続削除系（ログ・履歴・証跡の削除）

---

## 4. 監査イベント（SSOT）
- 監査イベントは Evidence Chain に記録し、改竄検知（ハッシュ + prev_hash）を維持する。
- 必須フィールド例: event_type, actor, token_id, target_id, request_id, timestamp, result。

