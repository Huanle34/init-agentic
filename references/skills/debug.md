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

1. **Read context** -- check `CLAUDE.md` and `CLAUDE.local.md` for recent changes
2. **Reproduce** -- confirm the bug is reproducible with a minimal test case
3. **Isolate** -- narrow the problem to the smallest possible scope (one function, one query)
4. **Hypothesize** -- state one specific hypothesis before changing any code
5. **Fix** -- implement the fix; do not fix multiple things at once
6. **Verify** -- run the full test suite; confirm the original bug is gone
7. **Check for regressions** -- run any integration tests that touch related code
8. **Update session notes** -- record root cause and fix in `CLAUDE.local.md`

## Hard rules
- Do not change more than one thing at a time during diagnosis
- If the fix is non-obvious, add a comment explaining WHY (not WHAT)
- If the bug reveals a missing test, add that test

## Definition of Done
- [ ] Bug is reproducible no more
- [ ] All tests pass
- [ ] Root cause documented in `CLAUDE.local.md`
- [ ] Regression test added (if applicable)

## Notes
Record patterns — recurring bug types, tricky areas of the codebase.
