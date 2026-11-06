# Local Verification Evidence

Run date: 2026-11-07

```powershell
python -m pytest tests\unit tests\integration -q -rA
```

Result: all tests passed.

The suite verifies:

- backend health contract;
- source-code diagnosis of the calculator bug;
- a genuine failing reproduction test against the untouched buggy code;
- a passing test against the proposed patch inside an isolated temporary workspace;
- unapproved and path-traversal patch attempts are blocked;
- end-to-end persistence, patch hash approval, backup/apply and resolution report;
- rejection, mismatched/stale patch approval, and duplicate Switch event blocking.

Live Switch-room delivery and a genuine provider-backed agent run remain separately dependent on configured credentials and a running Switch bridge.
