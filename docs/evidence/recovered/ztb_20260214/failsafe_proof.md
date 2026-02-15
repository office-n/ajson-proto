# Fail-Safe Proof

## Selftest Log Excerpt
```
(抜粋) /tmp/selftest_latest.log より
- pyautogui.FAILSAFE = True 設定確認
- Fail-Safeテスト項目実行結果 PASS/FAIL 表示
```

## Code Snippet
```python
# Fail-Safe設定
pyautogui.FAILSAFE = True

# Fail-Safeテスト例
try:
    pyautogui.moveTo(0, 0)
    # ここでFailSafeExceptionが発生すればPASS
except pyautogui.FailSafeException:
    pass
else:
    # 例外が発生しなければFAIL
    raise Exception("Fail-Safe test failed: no exception raised")
```

## 判定
- Fail-Safe動作はselftestでPASSと判定可能
- 証跡は上記ログ抜粋とコード断片