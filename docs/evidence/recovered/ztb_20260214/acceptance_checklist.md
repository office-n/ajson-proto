# Acceptance Checklist (Spec v1.0) — PASS/FAIL/未確認
1) selftest全項目PASS：FAIL/要確認（/tmp/selftest_proof.md参照）
2) jarvis無人1ループ完走：PASS（根拠=/tmp/e2e_proof.md）
3) pottsも同様：除外（jarvis限定MVPのため）
4) Fail-Safe動作：PASS（根拠=/tmp/failsafe_proof.md）
5) 失敗時ログで原因一意：PASS（根拠=/tmp/log_uniqueness_proof.md）