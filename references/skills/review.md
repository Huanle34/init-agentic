---
name: review
description: >
  Full pre-merge review: diff analysis, quality checks, test verification, merge/block decision.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Review

## When to use
Use before committing, before opening a PR, or before merging. This is a full readiness check —
more thorough than quickly invoking `@agent-code-reviewer`. Use when the change matters and a mistake
would be costly to reverse.

## Steps

1. **Get the diff** — determine what to review:
   - Staged changes: `git diff --staged`
   - Last commit: `git diff HEAD~1`
   - Branch diff: `git diff main...HEAD`
   - Ask the user if scope is unclear
2. **Read context** — scan `CLAUDE.md` for conventions, `CLAUDE.local.md` for what was intended
3. **Check tests** — run `test_cmd` from `CLAUDE.md`; if tests fail, the change is blocked — do not continue
4. **Security scan** — look for:
   - Hardcoded secrets, tokens, or credentials
   - Unvalidated user input passed to SQL, shell, or file paths
   - New dependencies with known CVEs (check package name if suspicious)
5. **Code quality review** — if `@agent-code-reviewer` is installed, invoke it on the diff; otherwise apply this checklist manually:
   - [ ] Logic is correct — no missed edge cases
   - [ ] Naming is clear and consistent with the existing codebase
   - [ ] Error handling is complete at system boundaries
   - [ ] No N+1 queries or unnecessary loops
   - [ ] No dead code left in
6. **Docs check** — if any public API, endpoint, CLI flag, or user-visible behavior changed, confirm the docs were updated
7. **Verdict** — state clearly:
   - **MERGE READY** — no blocking issues found
   - **BLOCKED** — list CRITICAL issues that must be fixed first
   - **MERGE WITH CAUTION** — list WARNING items to address soon

## Hard rules
- Never declare MERGE READY if tests are failing
- Never declare MERGE READY if a hardcoded secret was found
- If BLOCKED, do not merge — fix issues and run this skill again

## Definition of Done
- [ ] Diff reviewed completely
- [ ] Tests pass
- [ ] No hardcoded secrets
- [ ] Verdict stated with supporting evidence
- [ ] Blocking issues fixed (if BLOCKED was the initial verdict)

## Notes
Record recurring issues found in reviews — patterns worth adding to `.claude/rules/`.
