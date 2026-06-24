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

1. **Log to registry** — if `.claude/registry.md` exists, add `REFACTOR-NNN | In Progress`
2. **Understand blast radius** — before touching anything, grep for callers of the target code:
   ```
   grep -r "function_or_class_name" --include="*.py" .
   ```
   List all files that import or call the code. Wider blast radius = smaller refactor steps.
3. **Establish baseline** — run tests and record results
   - If tests exist: all must be green before starting; record pass count
   - If no tests: write down 3–5 concrete input → expected output examples that describe current behavior; these are your regression checks
4. **Define scope** — write a one-line description of the change. If it needs more than one line, the scope is too broad — split it into smaller refactors
5. **Refactor incrementally** — one logical change at a time; verify baseline holds after each step
6. **Review** — if `@agent-code-reviewer` is installed, invoke it; otherwise self-review against `.claude/rules/`
7. **Commit** — use `refactor:` prefix in commit message; do not bundle with feature or fix work
8. **Update registry** — mark `Done`
9. **Update session notes** — append what changed, why, and any patterns found to `CLAUDE.local.md`

## Hard rules
- Tests must stay green throughout — if a test breaks, stop and investigate before continuing
- Behavior changes are bugs, not features — stop and raise them if discovered
- Do not combine a refactor with a feature addition or bug fix in the same commit

## Definition of Done
- [ ] All pre-existing tests still pass (or baseline examples still produce correct output)
- [ ] Code is demonstrably simpler or more readable than before
- [ ] No CRITICAL issues from code review
- [ ] Changes committed with `refactor:` prefix
- [ ] `CLAUDE.local.md` updated with what changed and the motivation

## Notes
Record refactoring patterns that work well in this codebase.
