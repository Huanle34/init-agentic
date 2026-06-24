---
name: debug
description: >
  Analyze errors systematically: reproduce, isolate, fix, verify.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Debug

## When to use
Use when there is a bug, unexpected behavior, or failing test that needs
systematic root-cause analysis — not a quick guess-and-check.

## Steps

1. **Log to registry** — if `.claude/registry.md` exists, add `FIX-NNN | In Progress` before touching any code
2. **Read context** — check `CLAUDE.md` and `CLAUDE.local.md` for recent changes, known issues, related commits
3. **Reproduce** — confirm the bug is reproducible with a minimal test case
   - If not reproducible after 3 attempts: classify as intermittent, add logging to capture it on next occurrence, and document in `CLAUDE.local.md`. Do not guess-fix intermittent bugs.
4. **Check if it's a regression** — run `git log --oneline -20` to spot recent changes; if the bug is likely a regression, use `git bisect` to find the introducing commit before reading any code
5. **Isolate** — narrow to the smallest scope: one function, one query, one conditional. Use the "comment out half the code" method if needed
6. **Hypothesize** — before changing any code, state your hypothesis in this form:
   > *"The bug is in [specific location] because [reason], which causes [symptom] when [condition]."*
7. **Fix** — implement one fix at a time; never fix two things in one commit
8. **Verify** — run tests using `test_cmd` from `CLAUDE.md` (or auto-detect framework); confirm the original symptom is gone
9. **Check for regressions** — run tests for related code paths
10. **Update registry** — if `.claude/registry.md` exists, mark `Done`
11. **Update session notes** — record in `CLAUDE.local.md`: root cause, fix, and any missing tests added

## Hard rules
- One change at a time during diagnosis — no combined fixes
- If the fix is non-obvious, add a comment explaining WHY (not WHAT)
- If the bug reveals a missing test, add it before closing

## Definition of Done
- [ ] Bug is no longer reproducible (or intermittent bug has logging to capture it)
- [ ] All tests pass
- [ ] Root cause documented in `CLAUDE.local.md`
- [ ] Regression test added where applicable

## Notes
Record patterns — recurring bug types, tricky areas, `git bisect` findings.
