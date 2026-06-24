---
description: Update documentation to match recent code changes
---

# Sync Documentation

1. Run `git diff HEAD~1 -- "*.py" "*.ts" "*.sql" "*.go"` to see what changed
2. Identify documentation that is out of date (README, docs/, schema.yml, docstrings)
3. If `@agent-documentation` is installed, invoke it with the diff as context
4. Otherwise update affected docs directly:
   - Public API changes → README and inline docstrings
   - New features → docs/ guide
   - Breaking changes → CHANGELOG
   - dbt model changes → schema.yml descriptions
