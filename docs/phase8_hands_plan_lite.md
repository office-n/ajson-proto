# Phase 8: Hands導入計画（Lite版）

**タイムスタンプ**: 2026-02-06T23:10:57+09:00（Asia/Tokyo）  
**目的**: Tool Runner + BrowserPilotの導入（DRY_RUN優先）

---

## 概要

Phase 8では"手を動かす"機能を段階的に導入します。DRY_RUNとログ証跡を優先し、実行は最小限から開始します。

---

## Approval Required対象（明文化）

以下の操作は**必ず承認ゲート**を経由します:

### 削除系
- ファイル/ディレクトリ削除
- git履歴改変（force push, rebase, tag移動）
- データベース削除

### 課金系
- 外部API課金コール（LLM, ストレージ, 決済等）
- クラウドリソース作成/削除

### 不可逆系
- 本番環境への変更
- mainブランチへのマージ
- タグ付け/リリース

---

## Tool Runner設計

### 基本方針
1. **DRY_RUN優先**: 全ツールはデフォルトでDRY_RUN
2. **ログ証跡**: 全実行をauditsテーブルに記録
3. **Allowlist厳守**: 許可リストに無いコマンドは実行不可

### 許可ツール（初期版）
```python
SAFE_TOOLS = [
    "git status",
    "git log",
    "git diff",
    "ls",
    "cat",
    "grep",
    "pytest --co",  # テスト一覧のみ
]
```

### Denylist（絶対禁止）
```python
DENY_TOOLS = [
    "rm -rf",
    "git push --force",
    "git reset --hard",
    "docker rm",
    "npm publish",
]
```

---

## BrowserPilot設計

### 基本方針
1. **Screenshot証跡**: 全ページ遷移でスクリーンショット
2. **機密マスク**: パスワード/トークン入力は自動マスク
3. **Read-Only優先**: 初期はナビゲーション+読み取りのみ

### 許可操作（初期版）
- ページ遷移（GET）
- スクロール
- スクリーンショット
- テキスト抽出

### 禁止操作（初期版）
- フォーム送信（POST）
- ファイルアップロード
- Cookie操作
- LocalStorage書き込み

---

## 実装フェーズ

### Phase 8.1: DRY_RUN + ログ型固定
- Tool Runnerの`execute_tool(tool_name, args, dry_run=True)`
- BrowserPilotの`navigate(url, screenshot=True)`
- auditsテーブルへの記録フォーマット確定

### Phase 8.2: Allowlist実行（承認付き）
- SAFE_TOOLSのみ実行可能
- Approval Gateを経由

### Phase 8.3: BrowserPilot本格稼働
- ナビゲーション+読み取り実装
- Screenshot証跡の自動生成

---

## セキュリティ原則

1. **機密情報の非露出**:
   - API Key/Tokenは環境変数またはKeychain経由
   - ログにパスワード/機密情報を記録しない

2. **可逆性の確保**:
   - 不可逆操作は承認ゲート必須
   - git操作は常に可逆（force禁止）

3. **課金の明示**:
   - 課金APIコールは事前承認必須
   - 日次予算上限の強制

---

## ボス確認事項

- [ ] Approval Required対象は妥当か
- [ ] SAFE_TOOLS初期リストは妥当か
- [ ] BrowserPilot禁止操作は妥当か
- [ ] Phase 8.1（DRY_RUN）から開始でOKか

---

## 次ステップ

Phase 8.1の実装後、evidence_phase8_1_impl.md で証跡を提出します。
