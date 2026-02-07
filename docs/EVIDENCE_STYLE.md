# Evidence & Documentation Style Guide

To ensure portability, security, and cleanliness of our repository, all documentation and evidence files must adhere to the following rules by **PHYSICAL ENFORCEMENT**.

## 1. Forbidden Patterns (Zero Tolerance)
The following patterns are **STRICTLY PROHIBITED** in any file (docs are lint targets):

- ❌ `file`+`://` scheme (e.g., `file`+`:///absolute/path/...`)
- ❌ Absolute paths (e.g., `/path/to/username/...`, `/path/to/tmp/...`)
- ❌ Clickable links to local files (markdown links like `[link](./file.py)`)

## 2. Path Formatting
Always use **relative paths** from the repository root.
Paths must be formatted as **inline code** or **code blocks**, NOT as links.

### Correct ✅
- Modified `ajson/hands/runner.py`
- See `tests/test_approval_e2e.py`
- Evidence: `docs/evidence/evidence_fix_e2e_network_deny.md`

### Incorrect ❌
- Modified [runner.py](ajson/hands/runner.py)
- See `[test_approval_e2e.py](/absolute/path/to/tests/test_approval_e2e.py)` (Absolute path)
- Evidence: `/absolute/path/to/docs/evidence/...` (Absolute path)

## 3. Evidence File Structure
All evidence files in `docs/evidence/` must follow this structure:

1. **Status**: Clear status (e.g., ✅ **Full Green (110/110 passed)**)
2. **Context**: Branch name, commit hash (short)
3. **Verification Results**:
   - `pytest` summary (last line)
   - `lint` summary (pass/fail only, DO NOT list forbidden strings matching the grep pattern)
4. **Key Changes**:
   - Bullet points of changes
   - Reference files using relative paths in backticks

## 4. Lint Enforcement
This style is enforced by `scripts/lint_forbidden_strings.sh`.
Any violation will cause CI failure and `stop-the-line`.
