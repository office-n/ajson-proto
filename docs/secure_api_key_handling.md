# API キーの安全な設定方法

**作成日**: 2026-02-06  
**対象**: macOS Keychain を使った API キーの安全な保存

---

## はじめに

このガイドでは、OpenAI および Gemini の API キーを安全に保存・管理する方法を説明します。

### 重要な原則

❌ **絶対にしてはいけないこと**:
- API キーをチャットに貼り付ける
- API キーをファイル（`.env`等）に直接書く
- API キーをGitリポジトリにコミットする
- API キーをターミナルに直接入力する（コマンド履歴に残る）

✅ **推奨する方法**:
- macOS Keychain（キーチェーンアクセス）にGUIで保存
- AJSON は実行時に Keychain から自動取得
- API キーの値は画面に表示されない（「設定済み」「未設定」のみ）

---

## 手順1: Keychain Access でAPIキーを保存

### OpenAI API キー

1. **Keychain Access（キーチェーンアクセス）**を開く
   - アプリケーション → ユーティリティ → キーチェーンアクセス
   - または Spotlight で「keychain」と検索

2. メニューバーから **「ファイル」→「新規パスワード項目」** を選択

3. 以下を入力:
   - **キーチェーン項目名**: `AJSON_OPENAI_API_KEY`
   - **アカウント名**: あなたの Macユーザー名
     - 確認方法: ターミナルで `whoami` を実行
     - 例: `nakamurashingo`
   - **パスワード**: あなたの OpenAI API キー
     - 形式: `sk-proj-...` または `sk-...`
     - コピー&ペーストで入力（手入力は避ける）

4. **「追加」** をクリック

### Gemini API キー

上記と同様に、もう1つのパスワード項目を作成:
- **キーチェーン項目名**: `AJSON_GEMINI_API_KEY`
- **アカウント名**: あなたの Macユーザー名（同じ）
- **パスワード**: あなたの Gemini API キー

---

## 手順2: 設定を確認

保存後、Keychain Access で以下を確認:
1. 左側の「ログイン」キーチェーンを選択
2. 検索ボックスで `AJSON` と入力
3. 以下の2項目が表示されることを確認:
   - `AJSON_OPENAI_API_KEY`
   - `AJSON_GEMINI_API_KEY`

### 確認方法（値は表示されません）

ターミナルで以下を実行:
```bash
cd ajson-proto
source venv/bin/activate
python -m scripts.verify_paid_min --check-keys
```

出力例:
```
OPENAI_API_KEY: ✅ 設定済み
GEMINI_API_KEY: ✅ 設定済み
```

または:
```
OPENAI_API_KEY: ❌ 未設定
GEMINI_API_KEY: ✅ 設定済み
```

**重要**: API キーの値は表示されません（「設定済み」「未設定」のみ）。

---

## トラブルシューティング

### キーが見つからない（❌ 未設定）

**原因1: アカウント名が違う**
- Keychain で保存した「アカウント名」と現在のユーザー名が一致しているか確認
- ターミナルで `whoami` を実行して確認

**対処**:
1. Keychain Access で該当項目を削除
2. 正しいアカウント名で再作成

**原因2: キーチェーン項目名のタイプミス**
- 項目名が正確に `AJSON_OPENAI_API_KEY` になっているか確認
- 大文字・小文字、アンダースコアの位置を確認

### 権限エラー

**症状**: `security: SecKeychainSearchCopyNext: The specified item could not be found in the keychain.`

**対処**:
1. Keychain Access で該当項目をダブルクリック
2. 「アクセス制御」タブを選択
3. 「すべてのアプリケーションにこの項目へのアクセスを許可」にチェック
4. 「変更を保存」をクリック

---

## セキュリティに関する注意

### キーチェーンのバックアップ

- Time Machine や iCloud キーチェーンを使用している場合、API キーも自動的にバックアップされます
- セキュリティ上問題ない場合は、そのまま利用してください
- 不安な場合は、アクセス制御で「このアプリケーションのみ」に制限することも可能

### キーの更新

API キーを更新（ローテーション）する場合:
1. Keychain Access で該当項目をダブルクリック
2. 「パスワードを表示」にチェック（システムパスワード入力が必要）
3. 新しい API キーを入力
4. 「変更を保存」

### キーの削除

AJSON を使用しなくなった場合:
1. Keychain Access で該当項目を選択
2. 右クリック →「削除」
3. 確認ダイアログで「削除」

---

## 次のステップ

API キーの設定が完了したら、以下で実際に使用できます:

### DRY_RUN モード（デフォルト）
```bash
cd ajson-proto
source venv/bin/activate
uvicorn ajson.app:app --reload
```
- ブラウザで http://localhost:8000/console を開く
- メッセージを送信→ DEMO（DRY_RUN）で返答が返る
- API キーは使用されない（課金なし）

### 実API呼び出し（ボス承認後のみ）
```bash
# 環境変数で有効化
export LLM_ENABLE_PAID=1
export LLM_DAILY_BUDGET_USD=3.00

# 検証スクリプト実行
python -m scripts.verify_paid_min --provider OPENAI --max_calls 1
```

**注意**: 実API呼び出しはボスの承認が必要です。

---

## まとめ

- ✅ API キーは Keychain にのみ保存
- ✅ AJSON は実行時に自動取得
- ✅ キー の値は画面に表示されない
- ✅ 安全性が最優先

ご不明点があれば、ドキュメントを確認するか、開発者にお問い合わせください。
