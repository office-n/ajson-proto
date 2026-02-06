#!/bin/bash
# 安全な Keychain 経由API検証スクリプト
# 
# セキュリティ:
# - set +x でtrace無効化（キー値がターミナルに出ない）
# - Keychain取得は verify_paid_min.py 内で実施
# - stdout/stderrにキー値を出力しない

set -euo pipefail
set +x  # trace無効（最重要）

echo \"=== Keychain経由の安全なAPI検証実行 ===\"

# プロジェクトルート確認
SCRIPT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"
PROJECT_ROOT=\"$(cd \"$SCRIPT_DIR/..\" && pwd)\"

cd \"$PROJECT_ROOT\"

# venv有効化
if [ ! -d \"venv\" ]; then
    echo \"[Error] venv not found. Run 'python -m venv venv' first.\"
    exit 1
fi

source venv/bin/activate

# Keychain取得は verify_paid_min.py 内で自動実行される
# ここでは環境変数の汚染を防ぐためsubshellで実行
(
    echo \"\"
    echo \"[Step 1] Keychainからのキー取得試行...\"
    python -m scripts.verify_paid_min --check-keys
    
    echo \"\"
    echo \"[Step 2] 実API呼び出しテスト（Phase 2では未実装）\"
    echo \"    -> Gate承認後に有効化されます\"
    echo \"\"
)

echo \"=== 検証完了 ===\"
echo \"\"
echo \"重要: このスクリプトは実APIを呼び出しません。\"
echo \"     Keychain統合とキー取得のみ検証しました。\"
echo \"\"
