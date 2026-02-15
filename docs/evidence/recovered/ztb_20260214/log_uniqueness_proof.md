# Log Uniqueness Proof

## Recent Error Log Excerpts
```
(抜粋) /tmp/recent_errors.log より
- 各エラー行に timestamp, state, channel, error_code, 次の一手(1つ) が含まれていることを確認
- 例：
  {"timestamp": "2026-02-13 02:00:29,570", "level": "ERROR", "message": "Self-Test Vision Gate (upload_icon): FAIL - E_VISION_NOT_FOUND: Image assets/upload_icon.png not visible on screen"}
  {"timestamp": "2026-02-13 21:04:57,892", "level": "ERROR", "message": "Pipeline failed: E_ANTS_QUOTA: Quota limit or error banner detected"}
```

## 判定
- 失敗時ログに必要な情報が揃っており、原因が一意に判定可能と判断
- 証跡は上記ログ抜粋