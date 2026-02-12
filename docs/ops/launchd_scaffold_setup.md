2026-02-13T01:34:00+09:00 (JST)
# macOS launchd Scaffold Setup Guide

## 1. 目的
macOS の `launchd` (WatchPaths) を利用して、特定のディレクトリ配下でフォルダが作成された瞬間に `scripts/scaffold_on_create.sh` を自動発火させる仕組みを導入する。

## 2. LaunchAgent 設定 (plist例)
以下の内容を `~/Library/LaunchAgents/com.ants.scaffold.plist` として作成する（パスは環境に合わせて置換が必要）。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ants.scaffold</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string><REPO_ROOT>/scripts/scaffold_on_create.sh</string>
        <string><REPO_ROOT>/work</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string><REPO_ROOT>/work</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
</dict>
</dict>
</plist>
```

## 3. 導入手順
1. 上記 plist を適切なパス（絶対パス）に修正して保存。
2. 以下のコマンドでロード：
   ```bash
   launchctl load ~/Library/LaunchAgents/com.ants.scaffold.plist
   ```
3. 動作確認：
   `work/` ディレクトリ配下に新規フォルダを作成し、`docs/` や `runlog` が自動生成されるか確認。

## 4. 停止手順
```bash
launchctl unload ~/Library/LaunchAgents/com.ants.scaffold.plist
```

## 5. 注意事項
- `WatchPaths` はディレクトリ内の変更（ファイル追加/フォルダ追加）を検知する。
- スクリプト側で `.scaffolded` スタンプによるガードを行っているため、同一箇所での再実行は防止される。
