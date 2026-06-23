---
name: refactor
description: >
  Improve code quality without changing observable behavior.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Refactor

## When to use
Use when improving readability, reducing duplication, or restructuring code
without changing what it does. Observable behavior must not change.

## Steps

1. **Read context** -- understand what the code does before touching it
2. **Run tests** -- capture baseline: all tests must be green before starting
3. **Define scope** -- write a one-line description of the change; if it takes more than one line, it's too broad
4. **Refactor incrementally** -- one logical change at a time; run tests after each step
5. **Review** -- invoke `@agent-code-reviewer` when done
6. **Update session notes** -- append what changed and why to `CLAUDE.local.md`

## Hard rules
- Tests must stay green throughout — if a test breaks, stop and investigate
- Do not combine a refactor with a feature addition or bug fix in the same commit
- If behavior changes are discovered, stop and raise them before continuing

## Definition of Done
- [ ] All tests pass (same results as before refactor)
- [ ] Code is simpler or more readable than before
- [ ] `@agent-code-reviewer` has reviewed
- [ ] `CLAUDE.local.md` updated with what changed and the motivation

## Notes
Record refactoring patterns that work well in this codebase.
