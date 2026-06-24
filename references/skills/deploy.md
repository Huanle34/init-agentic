---
name: deploy
description: >
  Deploy or release the project to a target environment.
  Stack: <STACK>
version: "1.0.0"
---

# Skill: Deploy

## When to use
Use when deploying, releasing, or promoting an artifact to any environment.
Always requires explicit human approval before the production step.

## Steps

1. **Log to registry** — if `.claude/registry.md` exists, add `CHORE-NNN | In Progress`
2. **Read context** — check `CLAUDE.md` for deploy command, environment config, and rollback procedure (if documented)
3. **Verify quality** — run `test_cmd` or invoke `@agent-qa-tester` if installed; do not proceed with failing tests
4. **Identify deploy model** — confirm which pattern applies (see table below); ask if not clear from `CLAUDE.md`
5. **Know the rollback plan** — before deploying, state out loud: *"If this fails, I will [specific rollback action]."* Do not deploy without a rollback plan.
6. **Deploy to pre-production** — run the deploy command targeting the pre-production environment
   - If no pre-production exists: skip to step 7 but flag this as a risk to the user before proceeding
7. **Verify pre-production** — smoke test the critical path; confirm the deployment is healthy
8. **Request human approval** — STOP; show pre-production results and ask for explicit sign-off
9. **Deploy to production** — only after approval is given
10. **Verify production** — confirm healthy; run smoke test; monitor error rate for 5 minutes
11. **Rollback if needed** — if production verification fails, execute the rollback plan stated in step 5 immediately; do not wait
12. **Update registry** — mark `Done` (or `Rolled Back`)
13. **Update session notes** — record outcome, any issues, and whether rollback was triggered in `CLAUDE.local.md`

## Common deploy models

| Model | Pre-prod step | Production step | Rollback |
|-------|--------------|-----------------|---------|
| **Server / container** | Deploy to staging | Deploy to production | Redeploy previous image tag |
| **Airflow DAG** | Unpause in dev | Unpause in production | Pause DAG, restore previous file |
| **dbt Cloud** | Run dev job | Trigger production job | Re-run previous production job |
| **Serverless / Lambda** | Deploy to staging stage | Deploy to prod stage | Alias rollback or redeploy |
| **npm / PyPI package** | Publish to test registry | Publish to production | `npm deprecate` / `pip install ==prev` |
| **Database migration** | Run on staging DB | Run on production DB | Run down migration immediately |
| **No separate environment** | Dry-run / backup | Deploy with approval | Restore from backup |

## Hard rules
- Never deploy to production without explicit human approval in this session
- Never skip pre-production when it exists
- Rollback plan must be stated before deploying — not after something breaks

## Definition of Done
- [ ] Pre-production deploy verified (or risk of skipping acknowledged)
- [ ] Human approval obtained for production
- [ ] Production deploy verified healthy
- [ ] `CLAUDE.local.md` updated with outcome and rollback status

## Notes
Record deploy-specific gotchas, environment quirks, and rollback procedures here.
