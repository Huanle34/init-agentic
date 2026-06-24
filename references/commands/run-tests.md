---
description: Run the test suite and produce a pass/fail summary
---

# Run Tests

1. Read `CLAUDE.md` for the test command (`test_cmd`)
2. If no command found, detect from project: `pytest`, `npm test`, `go test ./...`, `dbt test`, `cargo test`
3. Run the tests and capture full output
4. If `@agent-qa-tester` is installed, invoke it for the analysis
5. Otherwise summarize: total passed / failed / skipped, and root cause of any failures
