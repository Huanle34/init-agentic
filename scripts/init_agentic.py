#!/usr/bin/env python3
"""
init_agentic.py — File generator + optional TUI wizard for init-agentic.

Two modes:
  --from-spec FILE   Read JSON spec and generate files (Claude-driven flow)
  --wizard [DIR]     Full interactive TUI wizard with arrow-key checkboxes

Usage:
    python init_agentic.py --from-spec spec.json [target-dir]
    python init_agentic.py --wizard [target-dir]
    python init_agentic.py --from-spec - [target-dir]   (stdin)
"""

import os
import re
import sys
import json
import argparse
import platform
from pathlib import Path
from datetime import date

# ── Python version guard ──────────────────────────────────────────────────────
if sys.version_info < (3, 7):
    sys.stderr.write("Error: Python 3.7+ is required.\n")
    sys.exit(1)


def _setup_encoding():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


_setup_encoding()

IS_WINDOWS = platform.system() == "Windows"


def _supports_ansi() -> bool:
    if not sys.stdout.isatty():
        return False
    if IS_WINDOWS:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return True


_ANSI = _supports_ansi()

CYAN  = "\033[96m" if _ANSI else ""
GREEN = "\033[92m" if _ANSI else ""
YELLOW= "\033[93m" if _ANSI else ""
BOLD  = "\033[1m"  if _ANSI else ""
RESET = "\033[0m"  if _ANSI else ""
DIM   = "\033[2m"  if _ANSI else ""
RED   = "\033[91m" if _ANSI else ""
SEP   = "=" * 52


def h(t):    return f"{BOLD}{CYAN}{t}{RESET}"
def ok(t):   return f"{GREEN}[ok]{RESET} {t}"
def warn(t): return f"{RED}[!]{RESET} {t}"
def dim(t):  return f"{DIM}{t}{RESET}"
def q(t):    return f"{YELLOW}?{RESET} {t}"


# ── Model versions ────────────────────────────────────────────────────────────
MODEL_OPUS   = "claude-opus-4-7"
MODEL_SONNET = "claude-sonnet-4-6"

# ── MCP catalog ───────────────────────────────────────────────────────────────
MCP_CATALOG = {
    "GitHub":                     {"type": "url", "url": "https://api.githubcopilot.com/mcp/",    "name": "github"},
    "Notion":                     {"type": "url", "url": "https://mcp.notion.com/mcp",             "name": "notion"},
    "Atlassian (Jira/Confluence)": {"type": "url", "url": "https://mcp.atlassian.com/v1/mcp",     "name": "atlassian"},
    "Google Drive":               {"type": "url", "url": "https://drivemcp.googleapis.com/mcp/v1", "name": "google-drive"},
    "Gmail":                      {"type": "url", "url": "https://gmailmcp.googleapis.com/mcp/v1", "name": "gmail"},
    "Slack":                      {"type": "url", "url": "https://mcp.slack.com/mcp",              "name": "slack"},
    "Postman":                    {"type": "url", "url": "https://mcp.postman.com/minimal",        "name": "postman"},
    "Figma":                      {"type": "url", "url": "https://mcp.figma.com/mcp",              "name": "figma"},
}

# ── Agent templates ───────────────────────────────────────────────────────────
AGENT_TEMPLATES = {
    "orchestrator": """\
---
name: orchestrator
description: >
  High-level task planner for {name}.
  Auto-invoked when the request spans multiple steps or agents
  (e.g. "build feature X end-to-end", "plan the auth flow", "coordinate a refactor").
  NOT for: single-step edits, quick questions, running tests directly.
model: @MODEL_OPUS@
effort: high
maxTurns: 30
---

You are the Orchestrator for project **{name}**.

## Role
Receive high-level requests, break them into subtasks, and delegate:
- Code generation -> review with @agent-code-reviewer after writing
- Testing -> @agent-qa-tester
- Documentation -> @agent-documentation or write to docs/

## Process
1. Read `CLAUDE.md` to understand project context and commands
2. Read `CLAUDE.local.md` (if it exists) to know current session state
3. Break the request into clear, ordered subtasks
4. Execute or delegate in priority order
5. Append a brief summary to `CLAUDE.local.md` when done

## Principles
- Plan before coding -- write the plan as a checklist first
- Do not self-approve changes to production, data deletion, or external communications
- Record significant architectural decisions in `docs/adr/`
""",

    "code-reviewer": """\
---
name: code-reviewer
description: >
  Read-only code quality reviewer for {name}.
  Auto-invoked after code is written and before committing.
  Checks logic correctness, security, naming, test coverage, and performance.
  NOT for: writing new code, fixing bugs, running tests, deployment.
model: @MODEL_SONNET@
effort: medium
maxTurns: 15
disallowedTools:
  - Write
  - Edit
  - Bash
---

You are the Code Reviewer for project **{name}**.

## Review checklist
- [ ] Logic is correct with no missed edge cases
- [ ] Naming is clear and consistent with the codebase
- [ ] No hardcoded secrets or credentials
- [ ] Error handling is complete
- [ ] Tests cover happy path and key edge cases
- [ ] No N+1 queries or unnecessary loops
- [ ] Input validation present at system boundaries

## Output format
```
## Code Review -- [file / feature]

### CRITICAL (must fix before merge)
- ...

### WARNING (should fix)
- ...

### SUGGESTION (nice-to-have)
- ...

### GOOD
- ...
```
""",

    "qa-tester": """\
---
name: qa-tester
description: >
  Test runner and QA reporter for {name}.
  Auto-invoked to verify a feature works or after a bug fix.
  Runs the test suite, analyzes failures, writes a pass/fail report.
  NOT for: writing application code, reviewing code, deployment.
model: @MODEL_SONNET@
effort: medium
maxTurns: 20
---

You are the QA Tester for project **{name}**.

## Test process
1. Read `CLAUDE.md` for the test command
2. Run the test suite and capture output
3. Analyze failures -- identify root cause, not just symptom
4. Append findings to `CLAUDE.local.md`

## Report format
```
## QA Report -- [date]

### Results
- Passed: X / Y
- Failed: Z

### Failures
- [test name]: [root cause] -> [suggested fix]

### Verdict
- [ ] Ready to merge
- [ ] Needs fixes first
```
""",

    "documentation": """\
---
name: documentation
description: >
  Documentation writer for {name}.
  Auto-invoked when a new feature is added or the API changes.
  Updates README, docs/, CHANGELOG. Does not modify application source code.
  NOT for: writing application code, running tests, deployment.
model: @MODEL_SONNET@
effort: low
maxTurns: 10
disallowedTools:
  - Bash
---

You are the Documentation Writer for project **{name}**.

## Principles
- Write for newcomers -- do not assume prior knowledge of the codebase
- Include a working code example for every API function or endpoint
- Update CHANGELOG when there are breaking changes
- Keep README.md accurate and under 150 lines

## Files to maintain
- `README.md` -- Quick start, installation, basic usage
- `docs/` -- Detailed documentation and guides
- `CHANGELOG.md` -- Version history
- Inline docstrings / JSDoc in source code
""",

    "ba-agent": """\
---
name: ba-agent
description: >
  Business Analyst for {name}.
  Auto-invoked when the request involves requirements analysis, writing specs,
  defining business rules, data flow diagrams, or sign-off decisions.
  NOT for: implementation, writing code, running queries, deployment.
model: @MODEL_OPUS@
effort: high
maxTurns: 20
disallowedTools:
  - Bash
  - Edit
---

You are the Business Analyst for project **{name}**.

## Role
Translate business needs into clear, unambiguous specifications that engineers
can implement without guessing. You define WHAT and WHY -- never HOW.

## Deliverables
- **Requirement specs** -- written to `workspace/ba/` in markdown
- **Data flow diagrams** -- DrawIO XML format
- **Business rules** -- explicit conditions, edge cases, exclusions
- **Sign-off checklist** -- what must be true before implementation starts

## Process
1. Ask clarifying questions until the requirement is unambiguous
2. Document the spec with: context, rules, edge cases, out-of-scope
3. List assumptions explicitly -- flag anything that needs confirmation
4. Do NOT approve implementation until spec is complete

## Principles
- If a rule has exceptions, write the exceptions explicitly
- "It depends" is not an answer -- resolve the dependency or flag it
- Every data field needs: source, transformation logic, expected values
- Out-of-scope is as important as in-scope
""",

    "sql-reviewer": """\
---
name: sql-reviewer
description: >
  Read-only SQL and dbt model reviewer for {name}.
  Auto-invoked after writing a dbt model or BigQuery SQL query, before committing.
  Checks SQL correctness, BigQuery dialect, CTE structure, performance, and naming.
  NOT for: writing SQL, running queries, deployment.
model: @MODEL_SONNET@
effort: medium
maxTurns: 15
disallowedTools:
  - Write
  - Edit
  - Bash
---

You are the SQL Reviewer for project **{name}**.

## Review checklist
- [ ] SQL is valid BigQuery dialect (not ANSI or Postgres-specific syntax)
- [ ] No `SELECT *` in production models -- all columns listed explicitly
- [ ] CTEs are named clearly and each has a one-line comment explaining purpose
- [ ] All column references qualified with table alias in multi-table queries
- [ ] No implicit type casting -- all casts are explicit
- [ ] Window functions use correct PARTITION BY and ORDER BY
- [ ] Incremental models have correct `is_incremental()` filter
- [ ] No hardcoded dates -- use `current_date` or dbt variables
- [ ] Naming: snake_case, no reserved words as identifiers

## Output format
```
## SQL Review -- [model / file]

### CRITICAL (logic error or will fail in production)
- ...

### WARNING (performance or maintainability issue)
- ...

### SUGGESTION (style / readability)
- ...

### GOOD
- ...
```
""",

    "data-validator": """\
---
name: data-validator
description: >
  Data quality validator for {name}.
  Auto-invoked after a dbt run or pipeline execution to verify output data.
  Checks row counts, nulls, schema drift, referential integrity, business rules.
  NOT for: writing code, reviewing SQL, deployment decisions.
model: @MODEL_SONNET@
effort: medium
maxTurns: 20
---

You are the Data Validator for project **{name}**.

## Validation checklist
- [ ] Row count is within expected range (compare to previous run)
- [ ] No unexpected nulls in NOT NULL columns
- [ ] No duplicate primary keys
- [ ] Referential integrity: all foreign keys exist in parent table
- [ ] Date ranges are sensible (no future dates in historical fields)
- [ ] Numeric values within business-defined bounds (no negative amounts where invalid)
- [ ] Schema matches expected columns and data types
- [ ] dbt tests all pass (unique, not_null, accepted_values, relationships)

## Process
1. Run `dbt test` and capture output
2. Check row counts against previous run or expected baseline
3. Sample suspicious values for manual inspection
4. Report findings with the affected model, column, and sample bad rows

## Report format
```
## Data Validation Report -- [date] -- [model / pipeline]

### FAIL (blocks promotion to production)
- [model.column]: [issue] -- sample: [bad values]

### WARN (investigate before next run)
- [model.column]: [issue]

### PASS
- [N] checks passed

### Verdict
- [ ] Safe to promote
- [ ] Needs investigation
```
""",
}

for _k in AGENT_TEMPLATES:
    AGENT_TEMPLATES[_k] = (AGENT_TEMPLATES[_k]
                           .replace("@MODEL_OPUS@", MODEL_OPUS)
                           .replace("@MODEL_SONNET@", MODEL_SONNET))

# ── Rules templates ───────────────────────────────────────────────────────────
RULES_TEMPLATES = {
    "general": {
        "display":  "general (no path filter -- always loaded)",
        "filename": "general.md",
        "content": """\
# General Coding Rules

- No secrets, tokens, or credentials in source files
- Commit messages: `type(scope): description` (feat, fix, chore, docs, refactor)
- Branch naming: `feature/`, `fix/`, `chore/` prefix required
- Every new feature needs at least one test
- Remove unused code -- do not comment it out and leave it
- One concern per function; functions over 40 lines are worth splitting
""",
    },
    "python": {
        "display":  "python (**/*.py)",
        "filename": "python-style.md",
        "paths":    ["**/*.py"],
        "content": """\
# Python Style Rules

- Type hints required on all public functions and methods
- Use f-strings over `.format()` or `%` formatting
- Use `dataclasses` or Pydantic for structured data, not plain dicts
- Follow PEP 8: 4-space indent, 88-char line limit (Black-compatible)
- Use `pathlib.Path` over `os.path` for file operations
- Never use bare `except:` -- always name the exception type
- Prefer `logging` over `print` for diagnostic output
""",
    },
    "typescript": {
        "display":  "typescript (**/*.{ts,tsx,js,jsx})",
        "filename": "typescript-style.md",
        "paths":    ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
        "content": """\
# TypeScript Style Rules

- Use `const` over `let` unless reassignment is unavoidable
- Explicit return types on all exported functions
- Use `interface` over `type` for object shapes
- Avoid `any` -- use `unknown` with type guards or proper generics
- Use optional chaining (`?.`) over manual null checks
- All async functions must handle errors (try/catch or `.catch()`)
- `strict: true` in tsconfig -- no implicit any
""",
    },
    "sql": {
        "display":  "sql (**/*.sql)",
        "filename": "sql-style.md",
        "paths":    ["**/*.sql"],
        "content": """\
# SQL Style Rules

- Keywords in UPPERCASE (SELECT, FROM, WHERE, JOIN, GROUP BY)
- Use CTEs (`WITH`) over nested subqueries for readability
- Qualify all column references with table alias in multi-table queries
- Never `SELECT *` in production queries -- list columns explicitly
- snake_case for all identifiers (tables, columns, aliases)
- Add a one-line comment above complex CTEs explaining their purpose
- Trailing commas on column lists for cleaner diffs
""",
    },
}


# ── TUI: arrow-key checkbox (wizard mode) ─────────────────────────────────────
def _read_key() -> str:
    """Read one keypress. Returns: 'up' | 'down' | 'space' | 'enter' | 'other'."""
    if IS_WINDOWS:
        import msvcrt
        b = msvcrt.getch()
        if b in (b'\xe0', b'\x00'):
            b2 = msvcrt.getch()
            if b2 == b'H': return 'up'
            if b2 == b'P': return 'down'
            return 'other'
        if b == b' ':            return 'space'
        if b in (b'\r', b'\n'): return 'enter'
        if b == b'\x03':         raise KeyboardInterrupt
        return 'other'
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.buffer.read(1)
            if ch == b'\x1b':
                rest = sys.stdin.buffer.read(2)
                if rest == b'[A': return 'up'
                if rest == b'[B': return 'down'
                return 'other'
            if ch == b' ':            return 'space'
            if ch in (b'\r', b'\n'): return 'enter'
            if ch == b'\x03':         raise KeyboardInterrupt
            return 'other'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _ask_checkbox_tui(prompt: str, options: list, defaults=None, hint: str = "") -> list:
    """Arrow-key navigable checkbox. Requires ANSI + TTY."""
    selected = list(defaults or [])
    cursor   = 0
    n        = len(options)
    lines    = 0  # lines printed so far (for redraw)

    def render():
        nonlocal lines
        if lines:
            sys.stdout.write(f"\033[{lines}A\033[J")
        sys.stdout.write(f"\n{q(prompt)}\n")
        for i, opt in enumerate(options):
            mark  = f"{GREEN}x{RESET}" if opt in selected else " "
            arrow = f"{CYAN}>{RESET}" if i == cursor else " "
            sys.stdout.write(f"  {arrow} [{mark}] {opt}\n")
        sys.stdout.write(dim(f"  {hint}\n"))
        sys.stdout.flush()
        lines = n + 3  # prompt line + n options + hint line

    render()
    while True:
        try:
            key = _read_key()
        except KeyboardInterrupt:
            print()
            sys.exit(0)
        if key == 'up':
            cursor = (cursor - 1) % n
        elif key == 'down':
            cursor = (cursor + 1) % n
        elif key == 'space':
            opt = options[cursor]
            if opt in selected:
                selected.remove(opt)
            else:
                selected.append(opt)
        elif key == 'enter':
            print()
            return selected
        render()


def _ask_checkbox_num(prompt: str, options: list, defaults=None, hint: str = "") -> list:
    """Number-input fallback when TUI is unavailable."""
    selected = list(defaults or [])
    while True:
        print(f"\n{q(prompt)}")
        for i, opt in enumerate(options, 1):
            mark = f"{GREEN}x{RESET}" if opt in selected else " "
            print(f"  {i}. [{mark}] {opt}")
        print(dim(f"  {hint}"))
        try:
            raw = input(f"{YELLOW}>{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if not raw:
            return selected
        for part in raw.replace(",", " ").split():
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(options):
                    opt = options[idx]
                    if opt in selected:
                        selected.remove(opt)
                    else:
                        selected.append(opt)


def ask_checkbox(prompt: str, options: list, defaults=None, hint: str = "") -> list:
    """Auto-selects TUI (arrow keys) or number input based on terminal capabilities."""
    tui_hint = "↑↓ move   Space toggle   Enter confirm"
    num_hint = "type number to toggle, Enter to confirm"
    if _ANSI and sys.stdin.isatty():
        return _ask_checkbox_tui(prompt, options, defaults, tui_hint)
    return _ask_checkbox_num(prompt, options, defaults, num_hint)


def ask_text(prompt: str, default: str = "") -> str:
    suffix = f" {dim(f'[{default}]')}" if default else ""
    try:
        val = input(f"{q(prompt)}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val if val else default


# ── Wizard TUI ────────────────────────────────────────────────────────────────
GRILLING_QUESTIONS = [
    ("Goals & Scope",  "What core problem does this project solve? Format: '[User X] cannot [do Y] without [Z]'"),
    ("Goals & Scope",  "What does success look like after 30 days? One specific, measurable metric."),
    ("Goals & Scope",  "What is explicitly NOT in scope for v1? List at least 3 things cut."),
    ("Users",          "Who is the first user — a specific person, not 'everyone'?"),
    ("Users",          "How does that user do this workflow today, without this tool? How long does it take?"),
    ("Architecture",   "What are the core entities in your system and how do they relate?"),
    ("Architecture",   "Where is system state stored — who reads it, who writes it, when?"),
    ("Architecture",   "What external services does this depend on — and if they go down?"),
    ("Risks",          "What could make this project fail completely in the first 3 months?"),
    ("Risks",          "Which technical part is unknown — needs a spike before building business logic?"),
    ("Agentic Design", "Does each agent have clear boundaries — what does each one NOT do?"),
    ("Agentic Design", "At which points is human approval required — where can't agents decide?"),
]


def run_wizard_tui() -> dict:
    """Full interactive TUI wizard. Returns a spec dict ready for generate_files()."""
    print(f"\n{h(SEP)}")
    print(f"{h('  [INIT]  Init Agentic -- Bootstrap Claude Code Project')}")
    print(f"{h(SEP)}")

    # Language
    lang_choice = ask_checkbox(
        "Select language / Chọn ngôn ngữ",
        ["English", "Tiếng Việt"],
        defaults=["English"],
    )
    lang = "vi" if "Tiếng Việt" in lang_choice else "en"

    print(f"\n{h('STEP 1 -- Project info' if lang == 'en' else 'BƯỚC 1 -- Thông tin project')}")
    name = ask_text("Project name" if lang == "en" else "Tên project",
                    default=Path.cwd().name)
    desc = ask_text("Short description (1-2 sentences)" if lang == "en" else "Mô tả ngắn (1-2 câu)",
                    default="")
    if not desc:
        desc = f"Project {name}."

    print(f"\n{h('STEP 2 -- Tech stack' if lang == 'en' else 'BƯỚC 2 -- Tech stack')}")
    stack    = ask_text("Primary language / framework" if lang == "en" else "Ngôn ngữ / framework chính", "Python")
    run_cmd  = ask_text("Run command (optional)" if lang == "en" else "Lệnh chạy (tuỳ chọn)", "")
    test_cmd = ask_text("Test command (optional)" if lang == "en" else "Lệnh test (tuỳ chọn)", "")
    lint_cmd = ask_text("Lint command (optional)" if lang == "en" else "Lệnh lint (tuỳ chọn)", "")

    print(f"\n{h('STEP 3 -- Agents' if lang == 'en' else 'BƯỚC 3 -- Agents')}")
    chosen_agents = ask_checkbox(
        "Select agents" if lang == "en" else "Chọn agents",
        list(AGENT_TEMPLATES.keys()),
        defaults=[],
    )

    print(f"\n{h('STEP 4 -- MCP integrations' if lang == 'en' else 'BƯỚC 4 -- MCP integrations')}")
    chosen_mcps = ask_checkbox(
        "Select MCP servers (optional)" if lang == "en" else "Chọn MCP servers (tuỳ chọn)",
        list(MCP_CATALOG.keys()),
        defaults=[],
    )

    print(f"\n{h('STEP 5 -- Hooks' if lang == 'en' else 'BƯỚC 5 -- Hooks')}")
    hook_labels     = ["pre-write (lint before write)", "post-edit (test after edit)"]
    chosen_hooks_raw = ask_checkbox(
        "Select hooks" if lang == "en" else "Chọn hooks",
        hook_labels,
        defaults=hook_labels,
    )
    chosen_hooks = []
    if any("pre-write" in h_ for h_ in chosen_hooks_raw): chosen_hooks.append("pre-write")
    if any("post-edit" in h_ for h_ in chosen_hooks_raw): chosen_hooks.append("post-edit")

    print(f"\n{h('STEP 6 -- Skills' if lang == 'en' else 'BƯỚC 6 -- Skills')}")
    skill_options = [
        "build-feature (implement a new feature end-to-end)",
        "deploy (deploy to staging or production)",
        "debug (systematic debugging workflow)",
        "refactor (improve code quality without changing behavior)",
    ]
    chosen_skills_raw = ask_checkbox(
        "Select skill templates" if lang == "en" else "Chọn skill templates",
        skill_options,
        defaults=[],
    )
    chosen_skills = [s.split(" ")[0] for s in chosen_skills_raw]

    print(f"\n{h('STEP 7 -- Code style rules' if lang == 'en' else 'BƯỚC 7 -- Code style rules')}")
    rule_options = [RULES_TEMPLATES[k]["display"] for k in RULES_TEMPLATES]
    rule_keys    = list(RULES_TEMPLATES.keys())
    sl = stack.lower()
    auto_defaults = [RULES_TEMPLATES["general"]["display"]]
    if "python" in sl: auto_defaults.append(RULES_TEMPLATES["python"]["display"])
    if any(x in sl for x in ["typescript","javascript","react","node","next","vue"]):
        auto_defaults.append(RULES_TEMPLATES["typescript"]["display"])
    if any(x in sl for x in ["sql","dbt","bigquery","postgres","mysql","snowflake"]):
        auto_defaults.append(RULES_TEMPLATES["sql"]["display"])
    chosen_rule_displays = ask_checkbox(
        "Select code style rules" if lang == "en" else "Chọn code style rules",
        rule_options,
        defaults=auto_defaults,
    )
    chosen_rules = [rule_keys[i] for i, d in enumerate(rule_options) if d in chosen_rule_displays]

    # Summary
    none_label = "none" if lang == "en" else "không có"
    print(f"\n{h(SEP)}")
    print(f"  {'Project':10s}: {BOLD}{name}{RESET}")
    print(f"  {'Stack':10s}: {stack}")
    print(f"  {'Agents':10s}: {', '.join(chosen_agents) or none_label}")
    print(f"  {'MCPs':10s}: {', '.join(chosen_mcps) or none_label}")
    print(f"  {'Hooks':10s}: {', '.join(chosen_hooks) or none_label}")
    print(f"  {'Skills':10s}: {', '.join(chosen_skills) or none_label}")
    print(f"  {'Rules':10s}: {', '.join(chosen_rules) or none_label}")
    print(f"{h(SEP)}")

    # Grilling
    grill_q = "Enable Grilling Mode? (y/n)" if lang == "en" else "Bật Grilling Mode? (y/n)"
    want_grill = ask_text(grill_q, "n")
    grilling_decisions = []
    if want_grill.lower() == "y":
        print(f"\n{h('  [GRILL]  Stress-test your plan')}")
        current_branch = None
        for i, (branch, question) in enumerate(GRILLING_QUESTIONS, 1):
            if branch != current_branch:
                current_branch = branch
                print(f"\n  {BOLD}-- {branch} --{RESET}")
            print(f"\n  {dim(f'[{i}/{len(GRILLING_QUESTIONS)}]')} {BOLD}{question}{RESET}")
            you = "You" if lang == "en" else "Bạn"
            try:
                answer = input(f"\n  {YELLOW}{you}:{RESET} ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if answer:
                grilling_decisions.append({
                    "branch": branch, "question": question,
                    "recommendation": "", "answer": answer,
                })
                print(f"  {ok('Recorded.' if lang == 'en' else 'Đã ghi nhận.')}")
            else:
                print(f"  {dim('Skipped.' if lang == 'en' else 'Bỏ qua.')}")
        print(f"\n  {ok(f'Grilling complete -- {len(grilling_decisions)}/{len(GRILLING_QUESTIONS)} answered.')}")

    confirm_q = "Proceed with file generation? (y/n)" if lang == "en" else "Tiến hành tạo files? (y/n)"
    confirm = ask_text(confirm_q, "y")
    if confirm.lower() != "y":
        print(dim("Cancelled." if lang == "en" else "Đã hủy."))
        sys.exit(0)

    return {
        "name": name, "description": desc, "stack": stack,
        "run_cmd": run_cmd, "test_cmd": test_cmd, "lint_cmd": lint_cmd,
        "agents": chosen_agents, "mcps": chosen_mcps, "hooks": chosen_hooks,
        "skills": chosen_skills, "rules": chosen_rules,
        "grilling_decisions": grilling_decisions, "lang": lang,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(ok(f"Generated: {path}"))


def extract_description(template_str: str) -> str:
    match = re.search(r"^---\n(.*?)\n---", template_str, re.DOTALL)
    if not match:
        return ""
    frontmatter = match.group(1)
    block = re.search(r"^description:\s*>\s*\n((?:[ \t]+.+\n?)+)", frontmatter, re.MULTILINE)
    if block:
        lines = [ln.strip() for ln in block.group(1).strip().splitlines() if ln.strip()]
        return " ".join(lines)
    single = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    return single.group(1).strip() if single else ""


def gen_rules_file(key: str) -> str:
    tmpl = RULES_TEMPLATES[key]
    paths_yaml = ""
    if "paths" in tmpl:
        paths_lines = "\n".join(f'  - "{p}"' for p in tmpl["paths"])
        paths_yaml = f"paths:\n{paths_lines}\n"
    return f"---\n{paths_yaml}---\n\n{tmpl['content']}"


def make_skill(name, description, stack):
    return f"""\
---
name: {name}
description: >
  {description}
  Stack: {stack}
version: "1.0.0"
---

# Skill: {name.replace("-", " ").title()}

## When to use
{description}

## Steps

1. **Read context** -- check `CLAUDE.md` and `CLAUDE.local.md`
2. **Plan** -- outline steps before executing
3. **Execute** -- work through each step, verify after each one
4. **Update session notes** -- append summary to `CLAUDE.local.md`

## Definition of Done
- [ ] Feature / task works correctly per requirements
- [ ] Tests pass
- [ ] Code reviewed (invoke @agent-code-reviewer)
- [ ] CLAUDE.local.md updated with what was done

## Notes
Record any gotchas, patterns, or lessons learned here after each use.
"""


# ── Spec validation ───────────────────────────────────────────────────────────
REQUIRED_KEYS = {"name", "description", "stack"}


def validate_spec(spec: dict) -> dict:
    missing = REQUIRED_KEYS - set(spec.keys())
    if missing:
        print(warn(f"Spec missing required keys: {', '.join(sorted(missing))}"))
        sys.exit(1)
    if not spec["name"].strip():
        print(warn("Spec key 'name' must not be empty."))
        sys.exit(1)
    if not spec["stack"].strip():
        print(warn("Spec key 'stack' must not be empty."))
        sys.exit(1)
    for key in ("agents", "mcps", "hooks", "skills", "rules", "grilling_decisions"):
        spec.setdefault(key, [])
    for key in ("run_cmd", "test_cmd", "lint_cmd"):
        spec.setdefault(key, "")
    spec.setdefault("lang", "en")
    for agent in spec["agents"]:
        if agent not in AGENT_TEMPLATES:
            print(warn(f"Unknown agent '{agent}' -- skipped. Valid: {', '.join(AGENT_TEMPLATES)}"))
    for rule in spec["rules"]:
        if rule not in RULES_TEMPLATES:
            print(warn(f"Unknown rule '{rule}' -- skipped. Valid: {', '.join(RULES_TEMPLATES)}"))
    return spec


# ── Generators ────────────────────────────────────────────────────────────────
def gen_claude_md(info):
    agents_list = "\n".join(
        f"- `@agent-{a}` -- {extract_description(AGENT_TEMPLATES[a]).split('.')[0].replace('{name}', info['name'])}"
        for a in info["agents"] if a in AGENT_TEMPLATES
    )
    mcp_list   = "\n".join(f"- {m}" for m in info["mcps"]) if info["mcps"] else "- (none configured)"
    rules_list = "\n".join(
        f"- `.claude/rules/{RULES_TEMPLATES[r]['filename']}` -- {RULES_TEMPLATES[r]['display']}"
        for r in info["rules"] if r in RULES_TEMPLATES
    ) if info.get("rules") else "- (none configured)"

    return f"""\
# {info["name"]}

## Goal
{info["description"]}

---

## Stack
{info["stack"]}

## Commands

```bash
# Run / start
{info.get("run_cmd") or "# TODO: add run command"}

# Test
{info.get("test_cmd") or "# TODO: add test command"}

# Lint
{info.get("lint_cmd") or "# TODO: add lint command"}
```

## Agents

{agents_list if agents_list else "- (none configured)"}

Invoke any agent with `@agent-<name>` in Claude Code.

## MCP Integrations

{mcp_list}

## Rules

{rules_list}

Rules in `.claude/rules/` without a `paths:` filter load every session.
Rules with `paths:` load only when a matching file enters context.

## Coding Conventions
- Commit messages: `type(scope): description` (feat, fix, chore, docs, refactor)
- Branches: `feature/`, `fix/`, `chore/` prefix
- Do not commit directly to `main`
- Every feature needs a corresponding test

## Memory & Context
- **Auto memory**: run `/memory` to view what Claude has captured across sessions
- **Session notes**: `CLAUDE.local.md` -- personal, gitignored, not committed
- **Architectural decisions**: `docs/adr/` (ADR-NNNN format)
- **Learnings log**: `docs/learnings.md`

---
*Generated by init-agentic skill -- {date.today()}*
"""


def gen_settings(agents, hooks):
    perms = {"allow": ["Bash", "Read", "Write", "Edit"], "deny": []}
    hooks_config = {}
    if "pre-write" in hooks:
        ext = ".ps1" if IS_WINDOWS else ".sh"
        cmd = (f"powershell -File .claude/hooks/pre-write{ext}" if IS_WINDOWS
               else f".claude/hooks/pre-write{ext}")
        hooks_config["PreToolUse"] = [
            {"matcher": "Write", "hooks": [{"type": "command", "command": cmd}]}
        ]
    if "post-edit" in hooks:
        ext = ".ps1" if IS_WINDOWS else ".sh"
        cmd = (f"powershell -File .claude/hooks/post-edit{ext}" if IS_WINDOWS
               else f".claude/hooks/post-edit{ext}")
        hooks_config["PostToolUse"] = [
            {"matcher": "Edit", "hooks": [{"type": "command", "command": cmd}]}
        ]
    settings = {
        "permissions": perms,
        "enabledPlugins": [],
        "agentSettings": {a: {"enabled": True} for a in agents},
    }
    if hooks_config:
        settings["hooks"] = hooks_config
    return json.dumps(settings, indent=2, ensure_ascii=False)


def gen_mcp_json(mcps):
    servers = {}
    for name in mcps:
        if name in MCP_CATALOG:
            cfg = MCP_CATALOG[name]
            servers[cfg["name"]] = {"type": cfg["type"], "url": cfg["url"]}
        else:
            print(warn(f"Unknown MCP '{name}' -- skipped."))
    return json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False)


def gen_hook_bash(hook_type, info):
    if hook_type == "pre-write":
        lint = info.get("lint_cmd") or "echo 'no lint configured'"
        return f"""\
#!/bin/bash
# Hook: pre-write -- run lint before Claude writes a file
FILE="$1"
if [ -z "$FILE" ]; then exit 0; fi
case "$FILE" in
  *.py|*.ts|*.js|*.tsx|*.jsx|*.sql)
    echo "[hook] Linting $FILE..."
    {lint} "$FILE" 2>&1 || true
    ;;
esac
"""
    test_cmd = info.get("test_cmd") or "echo 'no test configured'"
    return f"""\
#!/bin/bash
# Hook: post-edit -- run quick test after Claude edits a file
echo "[hook] post-edit triggered. Running quick check..."
{test_cmd} 2>&1 | tail -5 || true
"""


def gen_hook_ps1(hook_type, info):
    if hook_type == "pre-write":
        lint = info.get("lint_cmd") or "Write-Host 'no lint configured'"
        return f"""\
# Hook: pre-write -- run lint before Claude writes a file
param([string]$File)
if (-not $File) {{ exit 0 }}
$ext = [System.IO.Path]::GetExtension($File)
if ($ext -in @('.py','.ts','.js','.tsx','.jsx','.sql')) {{
    Write-Host "[hook] Linting $File..."
    try {{ {lint} $File 2>&1 }} catch {{ }}
}}
"""
    test_cmd = info.get("test_cmd") or "Write-Host 'no test configured'"
    return f"""\
# Hook: post-edit -- run quick test after Claude edits a file
Write-Host "[hook] post-edit triggered. Running quick check..."
try {{
    {test_cmd} 2>&1 | Select-Object -Last 5
}} catch {{ }}
"""


def gen_claude_local():
    return f"""\
# Session Notes -- Local Only

> This file is gitignored. Do not commit it.
> For team-shared context update CLAUDE.md or docs/.

## Last Updated
{date.today()}

## Current Focus
- Project just bootstrapped. Review CLAUDE.md and docs/adr/0001-bootstrap.md to get oriented.

## Blockers / Decisions Needed
- (none yet)

## Summary for Next Session
- (append a brief summary here at the end of each session)

---

*Auto memory: run `/memory` in Claude Code to see cross-session patterns.*
*Architectural decisions -> docs/adr/*
*Learnings -> docs/learnings.md*
"""


def gen_adr(info, grilling_decisions=None):
    grilling_section = ""
    if grilling_decisions:
        branches: dict = {}
        for d in grilling_decisions:
            branches.setdefault(d.get("branch", "General"), []).append(d)
        parts = ["\n## Grilling Session Decisions\n"]
        for branch, items in branches.items():
            parts.append(f"\n### {branch}\n")
            for item in items:
                parts.append(f"**Q:** {item['question']}\n\n")
                if item.get("recommendation"):
                    parts.append(f"> Recommended: {item['recommendation']}\n\n")
                parts.append(f"**Decision:** {item['answer']}\n\n---\n")
        grilling_section = "".join(parts)

    return f"""\
# ADR-0001: Project Bootstrap

**Date:** {date.today()}
**Status:** Accepted

## Context

{info["description"]}

**Stack:** {info["stack"]}

## Decision

Bootstrapped project structure using the `init-agentic` skill.
Generated agents, skills, hooks, and rules from the project description.

## Consequences

- Agents are available via `@agent-<name>` in Claude Code
- Code style rules in `.claude/rules/` load automatically by file type
- Personal session notes live in `CLAUDE.local.md` (gitignored)
- Hooks are registered in `.claude/settings.json` (not auto-scanned from the hooks/ directory)
{grilling_section}
---

*Format for future ADRs: `docs/adr/NNNN-short-title.md`*
*Status options: Proposed | Accepted | Deprecated | Superseded by ADR-NNNN*
"""


def gen_learnings():
    return f"""\
# Learnings & Improvements

## {date.today()} -- Project Bootstrap
- Bootstrapped with init-agentic skill
- (append findings after each meaningful session)

---

## Format
```
## YYYY-MM-DD -- [context / feature / incident]
- [thing learned or pattern discovered]
- [what didn't work -> what to do instead]
- [prompt or skill improvement worth making]
```
"""


def gen_registry():
    return f"""\
# Agent Task Registry

Agents check this file before starting a new task to avoid duplicate work.
Update status here, not just in CLAUDE.local.md.

## Format

| Task ID | Agent | Status | Started | Completed | Notes |
|---------|-------|--------|---------|-----------|-------|

## Registry

| Task ID | Agent | Status | Started | Completed | Notes |
|---------|-------|--------|---------|-----------|-------|
| INIT-001 | init-agentic | Done | {date.today()} | {date.today()} | Bootstrap project |

---
*Each agent logs here before starting a task and updates on completion.*
"""


# ── Portfolio Registry ────────────────────────────────────────────────────────
GLOBAL_CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
PORTFOLIO_PLACEHOLDERS = [
    "| (chưa có project nào — thêm khi bootstrap) | | | |",
    "| (no projects yet — add when bootstrapping) | | | |",
]
PORTFOLIO_SEPARATOR = re.compile(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|")


def update_portfolio(info: dict, target: Path) -> bool:
    if not GLOBAL_CLAUDE_MD.exists():
        return False
    content = GLOBAL_CLAUDE_MD.read_text(encoding="utf-8")
    if "Portfolio Registry" not in content:
        return False
    new_row = f"| {info['name']} | Active | | {target} |"
    for placeholder in PORTFOLIO_PLACEHOLDERS:
        if placeholder in content:
            content = content.replace(placeholder, new_row)
            GLOBAL_CLAUDE_MD.write_text(content, encoding="utf-8")
            return True
    portfolio_start = content.find("## Portfolio Registry")
    if portfolio_start == -1:
        return False
    section = content[portfolio_start:]
    sep_match = PORTFOLIO_SEPARATOR.search(section)
    if not sep_match:
        return False
    if f"| {info['name']} |" in section:
        return True
    insert_at = portfolio_start + sep_match.end()
    content = content[:insert_at] + "\n" + new_row + content[insert_at:]
    GLOBAL_CLAUDE_MD.write_text(content, encoding="utf-8")
    return True


# ── File generation ───────────────────────────────────────────────────────────
def generate_files(info: dict, target: Path):
    print(f"\n{h('Generating files...')}\n")
    write_file(target / "CLAUDE.md",       gen_claude_md(info))
    write_file(target / "CLAUDE.local.md", gen_claude_local())
    if info.get("mcps"):
        write_file(target / ".mcp.json", gen_mcp_json(info["mcps"]))
    write_file(target / ".claude" / "settings.json",
               gen_settings(info.get("agents", []), info.get("hooks", [])))
    write_file(target / ".claude" / "registry.md", gen_registry())
    for agent_key in info.get("agents", []):
        if agent_key not in AGENT_TEMPLATES:
            print(warn(f"Agent '{agent_key}' not found -- skipped."))
            continue
        content = AGENT_TEMPLATES[agent_key].format(name=info["name"])
        write_file(target / ".claude" / "agents" / f"{agent_key}.md", content)
    for rule_key in info.get("rules", []):
        if rule_key not in RULES_TEMPLATES:
            print(warn(f"Rule '{rule_key}' not found -- skipped."))
            continue
        write_file(target / ".claude" / "rules" / RULES_TEMPLATES[rule_key]["filename"],
                   gen_rules_file(rule_key))
    skill_descriptions = {
        "build-feature": "Implement a new feature from scratch, including code and tests.",
        "deploy":        "Deploy the project to a staging or production environment.",
        "debug":         "Analyze errors systematically: reproduce, isolate, fix, verify.",
        "refactor":      "Improve code quality without changing observable behavior.",
    }
    for skill_name in info.get("skills", []):
        desc = skill_descriptions.get(skill_name, f"Skill: {skill_name}")
        write_file(target / ".claude" / "skills" / skill_name / "SKILL.md",
                   make_skill(skill_name, desc, info["stack"]))
    for hook in info.get("hooks", []):
        if IS_WINDOWS:
            content, ext = gen_hook_ps1(hook, info), ".ps1"
        else:
            content, ext = gen_hook_bash(hook, info), ".sh"
        hook_path = target / ".claude" / "hooks" / f"{hook}{ext}"
        write_file(hook_path, content)
        if not IS_WINDOWS:
            os.chmod(hook_path, 0o755)
    write_file(target / "docs" / "adr" / "0001-bootstrap.md",
               gen_adr(info, info.get("grilling_decisions", [])))
    write_file(target / "docs" / "learnings.md", gen_learnings())


def print_summary(info: dict, target: Path, portfolio_updated: bool = False):
    print(f"\n{h(SEP)}")
    print(f"{h('  [DONE]  Bootstrap complete!')}")
    print(f"{h(SEP)}\n")
    print(f"  {'Project':10s}: {BOLD}{info['name']}{RESET}")
    print(f"  {'Location':10s}: {target}\n")
    print(f"  {CYAN}Output structure:{RESET}")
    print(f"  {BOLD}CLAUDE.md{RESET}                   <- project context (commit this)")
    print(f"  {BOLD}CLAUDE.local.md{RESET}              <- session notes  (gitignore this)")
    print(f"  {BOLD}.claude/agents/{RESET}              <- sub-agent definitions")
    print(f"  {BOLD}.claude/rules/{RESET}               <- code style rules (auto-loaded)")
    print(f"  {BOLD}.claude/settings.json{RESET}        <- permissions + hook registrations")
    print(f"  {BOLD}docs/adr/0001-bootstrap.md{RESET}   <- architectural decision record")
    print(f"  {BOLD}docs/learnings.md{RESET}            <- lessons log\n")
    if portfolio_updated:
        print(f"  {ok('Portfolio Registry updated in')} {dim(str(GLOBAL_CLAUDE_MD))}")
    else:
        print(f"  {warn('Could not auto-update Portfolio Registry.')}")
        print(f"  {dim(f'| {info[\"name\"]} | Active | | {target} |')}")
    print()
    gd = info.get("grilling_decisions", [])
    if gd:
        print(f"  {CYAN}Grilling decisions ({len(gd)}):{RESET}")
        for d in gd[:3]:
            q_text = d.get("question", "")
            print(f"  {dim('*')} {q_text[:65]}{'...' if len(q_text)>65 else ''}")
        if len(gd) > 3:
            print(f"  {dim(f'  ... +{len(gd)-3} more in docs/adr/0001-bootstrap.md')}")
        print()
    print(dim("  Invoke agents: @agent-orchestrator, @agent-code-reviewer, etc."))
    print(dim("  Agents auto-delegate based on their description field.\n"))


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Init Agentic — bootstrap a Claude Code project structure.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--from-spec", metavar="FILE",
        help="Read JSON spec and generate files. Use '-' for stdin.",
    )
    mode.add_argument(
        "--wizard", action="store_true",
        help="Run interactive TUI wizard (arrow keys + space to select).",
    )
    parser.add_argument(
        "target", nargs="?", default=".",
        help="Target directory (default: current directory).",
    )
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    if args.wizard:
        spec = run_wizard_tui()
    else:
        try:
            if args.from_spec == "-":
                raw = sys.stdin.read()
            else:
                spec_path = Path(args.from_spec).expanduser()
                if not spec_path.exists():
                    print(warn(f"Spec file not found: {spec_path}"))
                    sys.exit(1)
                raw = spec_path.read_text(encoding="utf-8")
            spec = json.loads(raw)
        except json.JSONDecodeError as e:
            print(warn(f"Invalid JSON in spec file: {e}"))
            sys.exit(1)

    spec = validate_spec(spec)
    generate_files(spec, target)
    portfolio_updated = update_portfolio(spec, target)
    print_summary(spec, target, portfolio_updated)


if __name__ == "__main__":
    main()
