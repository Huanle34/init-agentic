---
description: Run data validation checks on the latest pipeline output
---

# Data Validation

1. Read `CLAUDE.md` for the run/test command and data tool (dbt, Airflow, etc.)
2. If `@agent-data-validator` is installed, invoke it
3. Otherwise run manual checks:
   - Row count vs. previous run baseline
   - Null counts on key columns
   - Duplicate primary keys
   - Schema drift (column count, data types)
4. Report: FAIL / WARN / PASS with affected tables and sample bad rows
