---
name: deploy
description: >
  Deploy the project to a staging or production environment.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Deploy

## When to use
Use when deploying to staging or production. Always requires explicit human
approval before the final production step.

## Steps

1. **Read context** -- check `CLAUDE.md` for deploy command and environment config
2. **Verify tests pass** -- invoke `@agent-qa-tester` or run test command manually
3. **Deploy to staging** -- run deploy command targeting staging environment
4. **Smoke test** -- verify the critical path works in staging
5. **Request approval** -- STOP here; get explicit human sign-off before production
6. **Deploy to production** -- only after approval is given
7. **Verify production** -- confirm the deployment is healthy
8. **Update session notes** -- append outcome to `CLAUDE.local.md`

## Hard rules
- Never deploy to production without explicit human approval
- Never skip staging verification
- If smoke tests fail in staging, roll back and investigate before retrying

## Definition of Done
- [ ] Staging deploy verified
- [ ] Human approval obtained for production
- [ ] Production deploy verified healthy
- [ ] `CLAUDE.local.md` updated with deploy outcome

## Notes
Record deploy-specific gotchas, environment quirks, or rollback procedures here.
