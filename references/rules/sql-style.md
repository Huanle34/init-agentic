---
paths:
  - "**/*.sql"
---

# SQL Style Rules

- Keywords in UPPERCASE (SELECT, FROM, WHERE, JOIN, GROUP BY)
- Use CTEs (`WITH`) over nested subqueries for readability
- Qualify all column references with table alias in multi-table queries
- Never `SELECT *` in production queries -- list columns explicitly
- snake_case for all identifiers (tables, columns, aliases)
- Add a one-line comment above complex CTEs explaining their purpose
- Trailing commas on column lists for cleaner diffs
