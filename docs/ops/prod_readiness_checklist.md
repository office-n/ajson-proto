# Production Readiness Checklist (Phase 10)
Timestamp: 2026-02-12T10:30:00+09:00 (JST)

## 概要
本番稼働 (Production Launch) に向けた最終確認リスト。
すべての項目が `[x]` であることを確認してからリリースを行うこと。
`scripts/prod_readiness.sh` を実行することで、可能な項目を自動検証できる。

## 1. Security & Network
- [ ] **Network Default**: `DENY` 確認
  - Command: `grep "allow_network=False" ajson/core/network.py`
  - Expect: `allow_network=False`
- [ ] **Allowlist**: 許可リスト確認
  - Command: `sqlite3 data/approvals.db "SELECT * FROM allowlist_rules;"`
  - Expect: No unexpected entries.
- [ ] **Secrets Log**: ログ内の秘密情報混入チェック
  - Command: `grep -iE "key|token|secret" logs/app.log | grep -v "masked"`
  - Expect: Empty output.

## 2. Infrastructure & Data
- [ ] **Persistence**: DBファイル存在確認
  - Command: `test -f data/approvals.db && echo "Exists"`
  - Expect: "Exists"
- [ ] **Backup**: バックアップ対象確認
  - Command: `ls -l data/`
- [ ] **Logs**: ログディレクトリ確認
  - Command: `ls -l logs/`

## 3. Operations
- [ ] **Verification**: マージ後整合性チェック
  - Command: `bash scripts/verify_post_merge.sh`
  - Expect: `VERIFICATION SUCCESS`
- [ ] **Admin Manual**: `docs/ops/admin_manual.md` 存在確認
  - Command: `test -f docs/ops/admin_manual.md && echo "OK"`

## 4. Final Sign-off
- [ ] __Product Owner (Boss) Approval__
- [ ] __Security Audit PASS__
