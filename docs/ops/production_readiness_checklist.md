# Phase 10 Production Readiness Checklist

本ドキュメントは、AJSON プロジェクトが本番稼働相当の品質（Production Readiness）に達しているかを物理的に検証するための監査チェックリストである。

## 1. ガバナンス・ゲート
- [ ] **PR 経由の変更**: すべての変更は Pull Request を経由しており、`main` ブランチへの直接操作が禁止されていること。
- [ ] **Bypass 禁止**: 管理者権限によるブランチ保護のバイパスが行われていないこと。
- [ ] **レビュー承認**: マージには最低 1 名（原則 `@jarvisrv`）の承認が必要であること。

## 2. ネットワーク・セキュリティ
- [ ] **既定 DENY**: 明示的な許可がない限り、すべての外部ネットワーク接続が遮断されていること。
- [ ] **例外手順の遵守**: ネットワーク接続が必要な場合、以下の 3 点が揃っていること。
  - [ ] **Allowlist**: `ajson/hands/allowlist.py` へのホスト登録。
  - [ ] **Approval**: 責任者による承認証跡。
  - [ ] **Evidence**: 接続の必要性と安全性のエビデンス記録。

## 3. 必須検証（Automated Tests）
- [ ] **pytest**: `pytest -q` が ALL PASS すること。
- [ ] **DeprecationWarning**: `pytest -q -W error::DeprecationWarning` で警告が 1 件も発生しないこと。
- [ ] **Boot Check**: `bash scripts/ants_boot.sh` で `BOOT OK` が返ること。
- [ ] **Preflight**: `bash scripts/ants_preflight.sh <report>` で最終報告書の形式が合格すること。
- [ ] **Forbidden Strings**: 以下の文字列が製品コード・ドキュメントに含まれていないこと。
  - `file:///`, `/Users/`, `\Users\`, `/mnt/`, `sandbox:`

## 4. 証跡（Evidence Quality）
- [ ] **Runlog 必須項目**: 各作業の `runlog` 先頭に以下の OS タイムスタンプが含まれていること。
  - `OS_JST` (ISO8601 +09:00)
  - `OS_UTC`
  - `MONO_START` / `MONO_END`
- [ ] **SSOT 情報**: `main HEAD` (40桁SHA) および関連 PR の状態が正しく記録されていること。

## 5. マージ後検証（Post-Merge）
- [ ] **Regression Test**: マージ後の `main` ブランチで `bash scripts/verify_post_merge.sh` 相当の検証が実施されていること。

---
### 不足項目・今後の課題
- 現時点での自動監査スクリプトとの完全な連結ロジック。
- CI 上での「禁止文字列スキャン」の強制終了オプション（現在は警告レベル）。
