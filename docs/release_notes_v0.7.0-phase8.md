# Release Notes: v0.7.0-phase8

**タイムスタンプ**: 2026-02-07T01:34:00+09:00（Asia/Tokyo）  
**Tag**: v0.7.0-phase8  
**Main commit**: 3dd1f92

---

## Highlights

### Phase 1-3統合完了 ✅

**Phase 1: Ants起動ルール日本語化**
- JST タイムスタンプ恒久化
- 日本語応答ルール確立
- 証跡規約統一（禁止文字列ゼロ化）

**Phase 2: Keychain安全APIキー導線**
- macOS Keychain統合（`ajson/llm_gateway/keychain.py`）
- セキュアなAPIキー取得・マスク表示
- DRY_RUN Provider実装（APIキー不要で動作）
- `scripts/verify_paid_min.py`（最小有料検証スクリプト、未実行）

**Phase 3: Console UX v2 Lite**
- モバイルファーストComposer（sticky bottom、viewport基準）
- iOS safe-area対応
- 返答可視化（DRY_RUNでもassistant応答）
- Voice入力（Web Speech API）
- History/Traceボタン追加

### Phase 8: Hands Scaffold（DRY_RUN） ✅

**Tool Runner**
- Approval gates実装（DESTRUCTIVE/PAID/IRREVERSIBLE検出）
- DRY_RUNデフォルト（安全優先）
- Audit logging

**BrowserPilot**
- navigate/click/type_text scaffold
- Secret masking（APIキー・パスワード自動マスク）
- Screenshot証跡準備（未実装）

### Lint/CI統合 ✅

**禁止文字列検査**
- `scripts/lint_forbidden_strings.sh`作成
- 検査項目: `file://`、`/Users/`、APIキーパターン、force push
- GitHub Actions統合（`.github/workflows/lint.yml`）
- pytest hook統合（`conftest.py`、全テスト前に自動Lint）

---

## Verification

### Test Results

**pytest**: 51 passed in 15.70s
- Main branch: 34 tests
- Phase 8 (Hands): 17 tests

**Lint**: ✅ PASS (禁止語0件)

**PRs merged**:
- #1: Console UX v2 Lite
- #2: Ants boot rule (JP) + JST
- #3: Keychain API key injection
- #4: Phase 8 Hands scaffold

---

## Notes

### DRY_RUN優先

Phase 8実装はすべてDRY_RUNモードデフォルト。実実行は承認後に拡張予定。

### 実API未実行

Keychain統合完了済みだが、実API呼び出しは未実施（別途ボス承認必要）。

### 次フェーズ

**Phase 8拡張**:
- Tool Runner実実行（allowlist/denylist）
- BrowserPilot実実行（Playwright統合）
- Screenshot証跡自動保存

**実API最小検証**:
- `scripts/verify_paid_min.py`実行
- 1 call/provider、最小コスト
- BOSS_PAID_OK承認待ち

---

## Contributors

- nakamurashingo (Ants自走システム)

---

## Full Changelog

https://github.com/office-n/ajson-proto/compare/411b76c...v0.7.0-phase8
