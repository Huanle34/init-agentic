---
description: Run a code review on staged or recently changed files
---

# Code Review

1. Run `git diff --staged` to see staged changes; if empty, use `git diff HEAD~1`
2. Identify changed files
3. If `@agent-code-reviewer` is installed, invoke it with the changed files as context
4. Otherwise apply the review checklist from `.claude/rules/` manually
5. Output: CRITICAL / WARNING / SUGGESTION / GOOD sections
