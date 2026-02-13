# ChainRun vX.Y <Phase Name>
Timestamp: 202X-XX-XXTXX:XX:XX+09:00 (JST)

## 0. Time Audit (SSOT)
- **OS JST**: <TIMESTAMP>
- **Monotonic Start**: <FLOAT>
- **Boss Issued At**: <TIMESTAMP>
- **Diff**: <SECONDS>

## 1. 実施内容 (Summary)
- What was done?
- Key changes?

## 2. 検証結果 (Verification)
### 2.1 Code Verification
- Command: `bash scripts/verify_post_merge.sh`
- Result: **PASS** / **FAIL**

### 2.2 Test Results
- Unit Tests: `pytest`
- Manual Tests: `ajson.cli`

## 3. 成果物 (Artifacts)
- `docs/ops/...`
- `scripts/...`

## 4. 課題・リスク (Risks)
- Pending items?
- Known bugs?
