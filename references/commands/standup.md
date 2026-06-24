---
description: Generate a standup summary from recent git commits and CLAUDE.local.md
---

# Standup Generator

1. Run `git log --oneline --since="yesterday" --author="$(git config user.email)"` to get yesterday's commits
2. If no commits found, try `git log --oneline -10` to see recent work
3. Read `CLAUDE.local.md` for current focus and blockers
4. Format output:

**Yesterday:**
- [commits / tasks completed — use plain language, not commit hashes]

**Today:**
- [current focus from CLAUDE.local.md]

**Blockers:**
- [blockers from CLAUDE.local.md, or "none"]
