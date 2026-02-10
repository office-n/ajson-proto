## PROOF PACK
- timestamp: 2026-02-10 12:11:21 +0900
- pwd: ajson-proto

### GIT
- hooksPath: .githooks

### git status (porcelain)
M  .gitignore
A  docs/evidence/evidence_ants_memory_hardening_2026_02_10.md
A  docs/evidence/evidence_github_actions_5xx_2026_02_10.md
A  docs/ops/ants_boot_block.md
A  docs/ops/ants_playbook.md
 M logs/boot/latest.md
MM logs/proof/latest.md
A  run/uvicorn.pid
A  scripts/ants_anchor.sh
A  scripts/ants_guard.sh
A  scripts/ants_hourly_anchor.sh
A  scripts/ants_preflight.sh

### git log -5
732e753 docs: Phase 9 Status Board (SSOT) (#37)
2e7067c docs(evidence): add Phase9.4 PR merge facts (#36)
38ae54b fix: dispatcher failover KeyError in DRY_RUN tests (#38)
fc92a4c feat: Phase 9.4 Realtime Voice stub + DRY_RUN tests (#35)
420817f feat: Phase 9.3 Dispatcher Minimal (#34)

### staged diff (stat)
 .gitignore                                         |  1 +
 .../evidence_ants_memory_hardening_2026_02_10.md   | 34 ++++++++++++++++++
 .../evidence_github_actions_5xx_2026_02_10.md      | 26 ++++++++++++++
 docs/ops/ants_boot_block.md                        | 39 ++++++++++++++++++++
 docs/ops/ants_playbook.md                          | 42 ++++++++++++++++++++++
 logs/proof/latest.md                               | 33 +++++++++++++----
 run/uvicorn.pid                                    |  1 +
 scripts/ants_anchor.sh                             |  9 +++++
 scripts/ants_guard.sh                              | 34 ++++++++++++++++++
 scripts/ants_hourly_anchor.sh                      |  8 +++++
 scripts/ants_preflight.sh                          | 34 ++++++++++++++++++
 11 files changed, 254 insertions(+), 7 deletions(-)

### NOTE
- このログが出せない作業は「未検証/未完了」扱い
