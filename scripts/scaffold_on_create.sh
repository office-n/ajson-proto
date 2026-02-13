#!/bin/bash
# scripts/scaffold_on_create.sh
# フォルダ新規作成を検知し、起動ファイル群を自動生成する。

set -e

# 引数チェック: 検知されたパス
TARGET_PATH="$1"

if [ -z "$TARGET_PATH" ]; then
    echo "Usage: $0 <target_directory_path>"
    exit 1
fi

# フォルダであること、および .scaffolded が未存在であることを確認
if [ -d "$TARGET_PATH" ] && [ ! -f "$TARGET_PATH/.scaffolded" ]; then
    RUNID=$(export TZ=Asia/Tokyo; date +%Y-%m-%dT%H:%M:%S+09:00)
    
    echo "Scaffolding starting for: $TARGET_PATH at $RUNID"
    
    # 必要なディレクトリの作成
    mkdir -p "$TARGET_PATH/docs/evidence"
    mkdir -p "$TARGET_PATH/docs/reports"
    mkdir -p "$TARGET_PATH/docs/ssot"
    
    # 1. Runlog 雛形生成
    cat <<EOF > "$TARGET_PATH/docs/evidence/runlog_${RUNID}.md"
# Runlog: ${RUNID}

## 1. 時刻SSOT (Start)
- **RUNID**: ${RUNID}
- **OS_JST**: $(export TZ=Asia/Tokyo; date -Iseconds)
- **MONO_START**: (ここへ time.monotonic() を転記)

## 2. 作業ログ
- [ ] 起動確認
EOF

    # 2. Evidence 雛形生成
    cat <<EOF > "$TARGET_PATH/docs/evidence/evidence_${RUNID}.md"
# Evidence: ${RUNID}

## 概要
本作業における証跡を記録する。
EOF

    # 3. Report 雛形生成 (日本語)
    cat <<EOF > "$TARGET_PATH/docs/reports/report_${RUNID}.md"
# 最終報告: ${RUNID}

## 概要
作業内容のサマリー。

## 結果
- PASS/FAIL
EOF

    # 4. Status Board 雛形 (未存在時のみ)
    if [ ! -f "$TARGET_PATH/docs/ssot/ajson_status_board.md" ]; then
        cat <<EOF > "$TARGET_PATH/docs/ssot/ajson_status_board.md"
# AJSON SSOT Status Board
生成時刻: ${RUNID}
EOF
    fi

    # 二重生成防止スタンプ
    touch "$TARGET_PATH/.scaffolded"
    echo "Scaffolding completed."
else
    echo "Skipping: Path is not a directory or already scaffolded."
fi
