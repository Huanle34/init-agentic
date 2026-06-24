---
name: build-feature
description: >
  Implement a new feature from scratch, including code and tests.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Build Feature

## When to use
Use when implementing a new feature end-to-end: writing code, writing tests,
and verifying correctness before committing.

## Steps

1. **Log to registry** — if `.claude/registry.md` exists, add `FEAT-NNN | In Progress` before writing any code
2. **Read context** — check `CLAUDE.md` for stack, commands, and conventions; check `CLAUDE.local.md` for current state
3. **Clarify requirements** — stop only when you can answer all three:
   - *What does this produce?* (concrete output or behavior)
   - *What is explicitly out of scope for this change?*
   - *What does "done" look like?* (acceptance criterion)
4. **Plan** — write a checklist of files to create/edit before touching anything; share it with the user before implementing
5. **Implement** — work through the checklist; run tests after each meaningful change; stop if a step breaks something unexpected
6. **Review** — if `@agent-code-reviewer` is installed, invoke it; otherwise self-review against `.claude/rules/`
7. **Commit** — stage only the relevant files; use the commit format from `CLAUDE.md` (e.g. `feat: <description>`); do not commit if CRITICAL issues remain
8. **Update registry** — if `.claude/registry.md` exists, mark the row `Done`
9. **Update session notes** — append a summary to `CLAUDE.local.md`: what was built, any decisions made, gotchas

## Definition of Done
- [ ] Feature works per the clarified acceptance criterion
- [ ] Tests cover happy path and key edge cases (or documented why not)
- [ ] No CRITICAL issues from code review
- [ ] Changes committed with meaningful message
- [ ] `CLAUDE.local.md` updated

## Notes
Record patterns, non-obvious decisions, or reusable abstractions discovered here.
