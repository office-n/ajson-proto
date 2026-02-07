# Development Workflow

**タイムスタンプ**: 2026-02-08T01:57:00+09:00（Asia/Tokyo）

## Git Workflow

### Main Branch Protection

**絶対厳守**: main ブランチへの変更は **PR経由のGitHubマージのみ** を許可

#### 禁止事項
- ローカルで `main` への `merge` 後に `push` すること
- main ブランチへの直接 `commit` → `push`
- main ブランチでの強制プッシュ (`--force`, `-f`)

#### 正しい手順

1. **フィーチャーブランチを作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **変更をコミット**
   ```bash
   git add .
   git commit -m "feat: your change"
   ```

3. **ブランチをプッシュ**
   ```bash
   git push -u origin feature/your-feature-name
   ```

4. **GitHub上でPRを作成**
   ```bash
   gh pr create --base main --head feature/your-feature-name \
     --title "Your PR Title" \
     --body "Description"
   ```

5. **CI/テストパスを確認**
   - pytest 全件パス
   - lint チェックパス
   - 禁止文字列チェックパス

6. **GitHub UIまたはCLIでマージ**
   ```bash
   # レビュー後、GitHubで承認
   gh pr merge <PR番号> --merge
   ```

#### ローカル検証の推奨手順

PR作成前に以下を実行してください：

```bash
# Lintチェック（禁止文字列検査）
bash scripts/lint_forbidden_strings.sh

# テスト実行
python3 -m pytest -v

# ブランチ確認（main以外であることを確認）
git branch --show-current
```

#### 誤って main で作業してしまった場合

```bash
# 変更をstash
git stash

# フィーチャーブランチを作成
git checkout -b feature/rescued-changes

# 変更を戻す
git stash pop

# 通常の手順に従ってPR作成
```

---

## Lint/CI

### Pre-commit Check

すべてのコミット前に以下を確認：

```bash
bash scripts/lint_forbidden_strings.sh
```

### pytest Hook

`pytest` 実行時、自動的に禁止文字列チェックが実行されます（`conftest.py`）。

---

## Branch Naming

推奨命名規則：

- `feature/` : 新機能追加
- `fix/` : バグ修正
- `chore/` : リファクタリング、ドキュメント更新等
- `test/` : テスト追加・修正
- `docs/` : ドキュメント専用

---

## References

- [README.md](./README.md) : プロジェクト概要
- [scripts/lint_forbidden_strings.sh](./scripts/lint_forbidden_strings.sh) : 禁止文字列検査
