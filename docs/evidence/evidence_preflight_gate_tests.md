# Preflight Script Test Evidence

## Test Case 1: Forbidden Phrase "Progress Updates"
Input: A file containing "Progress Updates"
Expected Output: NG message and exit code 1
Result:
```bash
$ echo "Progress Updates are here" > test_ng.md
$ bash scripts/ants_preflight.sh test_ng.md
NG: Forbidden phrase 'Progress Updates' found in test_ng.md. Use 'Final Report Only'.
$ echo $?
1
```

## Test Case 2: English Only (High ASCII Ratio)
Input: A file with English text only.
Expected Output: NG message (ASCII ratio > 90%) and exit code 1
Result:
```bash
$ echo "This is a purely English report." > test_eng.md
$ bash scripts/ants_preflight.sh test_eng.md
NG: Report content seems to be English-only (ASCII ratio: 100%). Use Japanese.
$ echo $?
1
```

## Test Case 3: Japanese Content (Low ASCII Ratio)
Input: A file with Japanese text.
Expected Output: OK message and exit code 0
Result:
```bash
$ echo "これは日本語のレポートです。" > test_jp.md
$ bash scripts/ants_preflight.sh test_jp.md
OK: Preflight passed for test_jp.md (ASCII: 0%)
$ echo $?
0
```
