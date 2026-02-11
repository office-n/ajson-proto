# Evidence: AJSON Spec v0.2 SSOT v2.0 Patch
Timestamp: 2026-02-11T12:35:00+09:00 (JST)

## 1. 変更の目的 (Rationale)
ボス提示の「AJSON 統合仕様書（SSOT v2.0）」に基づき、開発方針を最新化するため。
特に「スマホから自宅PCを操作する」という利用シーンの明確化と、Google Antigravity機能への依存排除（自前実装）を定義する。

## 2. 変更内容の要約 (Summary)
1.  **Product Definition**:
    -   コンセプトを「スマホ→自宅PC物理操作OS」へ再定義。
    -   Ants連携をNon-Goalとし、自前実装路線を確定。
    -   AI Brain構成（Main: ChatGPT, Sub: Gemini）を明記。
2.  **Cockpit UX**:
    -   ChatGPT公式アプリ相当のUX（履歴、音声、添付）を基準として設定。
3.  **Remote Bridge (New Section)**:
    -   外出先スマホ（Client）と自宅PC（Host）の安全な接続アーキテクチャ定義。
    -   VPN/Relay + 短命トークン + Approval Queueの必須化。
4.  **Command Execution**:
    -   任意シェルの禁止を維持しつつ、Allowlistベースのラップ関数提供（Git/Python等）を明記。
5.  **Terminology**:
    -   "Antigravity-like" を "Self-implemented" に統一。

## 3. 整合性確認 (Non-contradiction Check)
- **v0.1 MVPとの整合**: v0.1の機能（State Machine, Runners）はそのまま維持されており、v0.2での拡張定義（File I/O, Remote）とも矛盾しない。
- **Security**: "NETWORK DENY" ポリシーはRemote Bridge（Secure Transport）の定義により、「許可されたエンドポイントのみ」という形で整合性を保っている。
- **Worktree**: Task単位のWorktree運用は、Command ExecutionのWorkspace固定要件と整合する。

## 4. 承認フロー
本EvidenceおよびSpec変更は、PR作成後に `jarvisrv` の承認を経て `office-n` によりマージされる（Bypass禁止）。

以上
