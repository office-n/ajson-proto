# Evidence: AJSON Spec v2.1 (SSOT Fixed)
Timestamp: 2026-02-11T13:00:00+09:00 (JST)

## 1. 変更の目的
AJSONの開発フェーズを「プロトタイプ拡張 (v0.2)」から「統合仕様 (v2.1)」へ移行し、全開発のSSOTとして固定するため。
これまでの「生産性キット (v0.2)」と「統制パッチ (SSOT v2.0)」を単一の仕様書に統合し、AGI Cockpit級のUI生産性と厳格な統制（Governance）を両立させる。

## 2. 変更内容概要
- **統合**: v0.2 + SSOT v2.0 Patch -> Spec v2.1
- **新機能定義**:
  - **Cockpit UI**: Multi-line / Voice / Attachments / History / Resume
  - **Remote Bridge**: Secure Transport / Auth / Approval Queue
- **Governance**:
  - **Command Execution**: Wrapped Functions Only (No Shell)
  - **Worktree**: Task Isolation
  - **Network**: DENY (Allowlist Only)

## 3. 非ゴール (Non-Goal)
- **既存AIアプリUI RPA**: 信頼性欠如のため、API連携を唯一の解とする。
- **Google Antigravity (Ants) 連携**: 依存せず、同等機能を自前実装する。

## 4. 整合性確認
- Spec v0.2 (Productivity Kit) の全機能は v2.1 に包含されており、機能低下はない。
- SSOT v2.0 Patch (Security/Remote) の要件は v2.1 にて強化・詳細化されている。

以上
