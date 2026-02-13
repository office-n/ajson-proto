## 概要
Phase 9.8.1: Network Security Layer (Allowlist + Approval + Evidence) の実装。

## 目的
Realtime API等の外部接続において、アプリケーションレベルでのセキュリティ制御を確立し、「実通信ゼロ」を論理的・物理的に保証する。

## 実装内容
1.  **Design**: `docs/design/phase9.8.1_allowlist_approval.md`
2.  **Layer 1 (Allowlist)**: `ajson/hands/allowlist.py` (Static check)
3.  **Layer 2 (Approval) & 3 (Evidence)**: `ajson/core/network.py` (SecureNetworkConnector)
    - `Allowlist` -> `ApprovalStore` -> `AuditLogger` の順でチェック。
4.  **Verification**: `tests/test_network_security.py`
    - Allowlist外接続の拒否確認
    - Approvalなし接続の拒否確認
    - 正常系（Mock）の確認

@jarvisrv レビューをお願いします。
