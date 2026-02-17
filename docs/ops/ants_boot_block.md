# Ants Boot Block (起動手順・遵守事項)

## 0. 基本原則（Must Maintain）
- **日本語のみ**: 思考プロセス・報告は全て日本語で行う。
- **タイムスタンプ**: `date`コマンド等でその場で生成する（手入力・流用禁止）。
- **進捗報告禁止**: 途中報告はせず、最終報告のみ行う。
- **Bypass禁止**: `--admin` や `Override` は使用せず、正規の手順を守る。

## 1. 起動時（Boot）
1. **SSOT確認**: `git remote -v` で `office-n/ajson-proto` であることを確認。
2. **Anchor更新**: `bash scripts/ants_anchor.sh` を実行。
3. **Guard確認**: `bash scripts/ants_guard.sh` を実行（OKなら進行）。

## 2. 作業中（Runtime）
- **Hourly Anchor**: 長時間作業時は `scripts/ants_hourly_anchor.sh` を裏で回すか、手動で定期的にAnchor更新。
- **Preflight**: PR作成や報告前に `scripts/ants_preflight.sh` で自己検査。
- **Merge Check**: マージ実行前に「ログイン中のアカウント」を必ず確認。`office-n` でない場合は **STOP**。

## 3. 停止条件（Immediate Stop）
- Remote不一致
- 2FA/認証要求
- 権限不足
- Checks Red（原因不明）

## 4. 最終報告フォーマット
```text
【完了報告】<タイトル>
Timestamp (JST): <生成したTS>

<PR情報 / Merge結果>
- Status: ...
- Approver: ...
- Merger: ...

<成果物 / 変更点>
...

【リスク】
...
```
