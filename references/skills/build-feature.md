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
and verifying correctness before handing off to code-reviewer.

## Steps

1. **Read context** -- check `CLAUDE.md` for stack and commands; check `CLAUDE.local.md` for current state
2. **Clarify requirements** -- if ambiguous, ask one focused question before writing any code
3. **Plan** -- write a short checklist of files to create/edit before touching anything
4. **Implement** -- work through each step; run tests after each meaningful change
5. **Review** -- invoke `@agent-code-reviewer` before declaring done
6. **Update session notes** -- append a summary to `CLAUDE.local.md`

## Definition of Done
- [ ] Feature works correctly per requirements
- [ ] Tests cover happy path and key edge cases
- [ ] `@agent-code-reviewer` has reviewed and no CRITICAL issues remain
- [ ] `CLAUDE.local.md` updated with what was done and any gotchas

## Notes
Record any patterns, non-obvious decisions, or lessons learned here after each use.
