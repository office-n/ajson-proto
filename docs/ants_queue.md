# Ants 自走キュー管理

**タイムスタンプ**: 2026-02-07T00:24:00+09:00（Asia/Tokyo）  
**SSOT**: このファイルがAntsの作業キューのSingle Source of Truth

---

## 実行ルール

1. **先頭から順に実行**: 完了したら `[x]` をつけて次へ進む
2. **途中報告禁止**: 06:00 JSTまたは例外停止（2FA/機密検出/pytest失敗）時のみ報告
3. **キュー枯渇時**: 次の改善案を自動補充（不可逆操作は禁止）
4. **優先度**: P0 > P1 > P2 > 改善案

---

## 現在のキュー

### P0: 緊急タスク（完了済み）

- [x] Phase3サニタイズ証跡v4を完成版にする（プレースホルダ削除）
- [x] Phase8証跡v2を作成（規約違反是正、絶対パス参照削除、force push明示）
- [x] Lint導入（scripts/lint_forbidden_strings.sh）
- [x] Phase8 PRをgh CLIで自動作成（進行中）

### P1: Documentation & Quality（完了）

- [x] README.mdにLint実行手順を追記
- [x] .github/workflows/lint.yml を作成（CI/CD統合）
- [x] pytest実行前に自動Lint実行する仕組み追加（conftest.py）
- [ ] Phase 1-3のPRにスクリーンショット追加（UI変更の証拠）

### P2: Code Quality & Testing

- [ ] Phase8 Hands: 失敗テストケース修正（approval_required_when_not_dry_run）
- [ ] Phase8 Hands: BrowserPilot skeleton追加（DRY_RUNのみ）
- [ ] E2E test追加（Console UI: composer拡大、🧾トレース）
- [ ] Coverage測定とバッジ追加

### 改善案（自動補充候補）

- [ ] docs/architecture.md 作成（LLM Gateway, Hands, UI Consoleの構成図）
- [ ] Performance測定（pytest --durations=10）
- [ ] Security audit（bandit, safety）
- [ ] Type hints追加率向上（mypy --strict）
- [ ] Changelog自動生成（conventional-changelog）

---

## 次回定時報告（06:00 JST）用メモ

**今日やったこと**:
1. (ここに自動追記)
2. 
3. 

**Compare URL一覧**:
- (ここに自動追記)

**PR一覧**:
- (ここに自動追記)

**pytest最終1行**:
- (ここに自動追記)

**禁止語/機密Lint結果**:
- (ここに自動追記)

**次に回すキュー（上位3つ）**:
- (ここに自動追記)
