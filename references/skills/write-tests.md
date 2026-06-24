---
name: write-tests
description: >
  Add test coverage to existing untested or under-tested code.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Write Tests

## When to use
Use when adding tests to existing code that has no tests or insufficient coverage.
Different from `build-feature` (which builds and tests something new) — this is specifically
for retrofitting tests onto code that already exists and works.

## Steps

1. **Log to registry** — if `.claude/registry.md` exists, add `TEST-NNN | In Progress`
2. **Read context** — check `CLAUDE.md` for the test command and testing framework
3. **Measure current coverage** — run coverage tool if available:
   - Python: `pytest --cov`
   - JS/TS: `jest --coverage`
   - Go: `go test -cover ./...`
   - If no coverage tool, list files that have no corresponding test file
4. **Prioritize targets** — do not test everything at once; rank by:
   - High business value (core logic, critical paths)
   - High change frequency (files changed most in recent git log)
   - No existing tests at all (gaps first)
5. **For each target function or module:**
   a. Read the code and understand what it *should* do (not just what it does)
   b. Write the **happy path** test first — the normal, expected use case
   c. Write **edge case** tests — empty input, boundary values, None/null, max values
   d. Write **failure case** tests — invalid input, expected errors, permission denied
   e. Verify each test actually fails if you break the code it tests (mutation check)
6. **Run the full suite** — confirm all new tests pass and no existing tests broke
7. **Review test quality** — tests should assert behavior, not implementation. Ask: "if I rename a variable inside the function, should this test break?" If yes, the test is too coupled to internals.
8. **Update registry** — mark `Done`
9. **Update session notes** — record what was tested, coverage delta, any untestable code found

## Hard rules
- Never write a test that passes without actually testing the right thing (green-washing)
- Do not test private internals directly — test through the public interface
- A test that never fails is not a test — verify each new test can catch a real bug

## Definition of Done
- [ ] All new tests pass
- [ ] Coverage increased (or baseline documented if tools unavailable)
- [ ] No existing tests broken
- [ ] Test targets prioritized — most critical paths covered first
- [ ] `CLAUDE.local.md` updated with coverage summary

## Notes
Record which areas are hard to test and why — this is useful technical debt documentation.
