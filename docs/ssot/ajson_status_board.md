# AJSON SSOT Status Board
Last Updated: 2026-02-12T10:25:00+09:00 (JST)

## 1. Repository Status
- **Repo**: `office-n/ajson-proto`
- **Main Branch**: `main`
- **Current Main SHA**: `709772138eb151cf57b85fbfd00b91d2c67b0903`

### Status Definitions (Merge Integrity)
1. **MERGED**: GitHub PR UI shows "Merged" with timestamp and SHA.
2. **Implied Merge**: Code exists in `main` (verified by `git log`/`grep`), but PR metadata is missing or broken (GH CLI failure).
   - *Action*: Treat as Merged for logic, but record "Context Loss" in Capacity SSOT.
3. **OPEN**: PR exists and is not merged.


## 2. Active PRs (Review/Merge Queue)
| PR | Branch | Status | Description | Note |
|---|---|---|---|---|
| **#58** | `fix/datetime...` | **OPEN** | Datetime + Boot Fix | **Draft** |
| **#59** | `feat/phase9.8.1...` | **OPEN** | Phase 9.8.1 (3-Layer) | **Draft** |
| **#60** | `maint/v1.9-chainrun` | **OPEN** | ChainRun v1.9 Refactor | 作成完了 (CI FAILED) |

## 3. Phase Status
- **Phase 9.8**: Complete (Network/Persistence/CLI).
- **Phase 9.9**: Docs & Guardrails (Merged).
- **Phase 10**: Production Readiness (Checklist Created).

## 4. Governance Compliance
- **Network**: DENY (Strict).
- **Command**: Wrapped Only.
- **Workflow**: PR Required (No Main Direct).
- **Docs**: JST Timestamp Enforced.
