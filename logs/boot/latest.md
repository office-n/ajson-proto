## BOOT PACK
- timestamp: 2026-02-11 23:30:55 +0900
- pwd: ajson-proto

### PACK LINK CHECK
- .cursorrules: OK
- .githooks/pre-commit: OK
- scripts/guardrails.sh: OK
- scripts/proof_pack.sh: OK

### GIT
- hooksPath: .githooks

### git status (porcelain)
A  ajson/cli/__init__.py
A  ajson/cli/__main__.py
A  ajson/cli/approval.py
A  ajson/hands/allowlist.py
M  ajson/hands/approval_sqlite.py
A  docs/design/phase9.8.2_schema_v1.md
AM docs/ops/admin_manual.md
AM docs/ops/cli_user_guide.md
 M docs/ssot/ajson_status_board.md
 M logs/boot/latest.md
M  logs/proof/latest.md
M  scripts/ants_preflight.sh
A  tests/test_cli_approval.py
AM tests/test_network_security.py
?? ajson/core/network.py
?? docs/design/phase9.8.2_persistence_cli.md
?? docs/evidence/evidence_phase9_8_2_persistence_cli_v1_6.md
?? docs/evidence/evidence_pr54_55_56_merge_facts_v1_4.md
?? docs/evidence/evidence_pr54_55_56_merge_or_applied_facts_v1_5.md
?? docs/evidence/runlog_v1_3_2026-02-11.md
?? docs/evidence/runlog_v1_5_2026-02-11T22:57:00+09:00.md
?? docs/evidence/runlog_v1_6_2026-02-11T23:08:27+09:00.md
?? docs/evidence/runlog_v1_7_2026-02-11T23:26:38+09:00.md
?? docs/reports/ants_crop_v1_2_report.md
?? docs/reports/ants_crop_v1_3_report.md
?? docs/reports/chainrun_v1_7_final_2026-02-11T23:26:38+09:00.md
?? docs/reports/crop_v1_4_final_2026-02-11.md
?? docs/reports/crop_v1_5_final_2026-02-11.md
?? docs/reports/crop_v1_6_final_2026-02-11.md
?? pr_body.md
?? pr_body_981.md
?? pr_body_982.md
?? run/requirements.hash

### git log -5
9d98e59 docs: add single SSOT status board (#56)
c51772e feat: Phase9.7 realtime session logic (no-network, tests, evidence) (#55)
4c1ad45 docs: SSOT for PR#53 merge facts (#54)
eae4efe docs: add AJSON spec v2.1 (cockpit + governance) (#53)
e7a7134 docs: finalize SSOT with PR#50/49 merges and timestamp fix (#51)

### NOTE
- non-git folders are 'All Green' if PACK LINK CHECK is OK and logs update.
