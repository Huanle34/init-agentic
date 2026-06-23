#!/usr/bin/env python3
"""
init_agentic.py — Bootstrap a complete Claude Code agentic project structure.

Generates: CLAUDE.md, CLAUDE.local.md, .mcp.json, .claude/settings.json,
           .claude/agents/, .claude/rules/, .claude/skills/, .claude/hooks/,
           docs/adr/, docs/learnings.md, .claude/registry.md
"""

import os
import re
import sys
import json
import platform
from pathlib import Path
from datetime import date

# Fix encoding on Windows (cp1252 -> utf-8)
def _setup_encoding():
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_setup_encoding()

IS_WINDOWS = platform.system() == "Windows"

# ── Colors ────────────────────────────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
DIM    = "\033[2m"
RED    = "\033[91m"

def h(text):    return f"{BOLD}{CYAN}{text}{RESET}"
def ok(text):   return f"{GREEN}[ok]{RESET} {text}"
def q(text):    return f"{YELLOW}?{RESET} {text}"
def dim(text):  return f"{DIM}{text}{RESET}"
def warn(text): return f"{RED}[!]{RESET} {text}"
def ans(text):  return f"{CYAN}->{RESET} {text}"

SEP = "=" * 52

# ── i18n strings ──────────────────────────────────────────────────────────────
STRINGS = {
    "en": {
        "title":        "  [INIT]  Init Agentic -- Bootstrap Claude Code Project",
        "intro":        "  Answer each question. Press Enter to accept the default.",
        "step1":        "STEP 1 -- Project info",
        "project_name": "Project name",
        "description":  "Short description (1-2 sentences about the goal)",
        "step2":        "STEP 2 -- Tech stack",
        "stack":        "Primary language / framework",
        "run_cmd":      "Run / start command",
        "test_cmd":     "Test command",
        "lint_cmd":     "Lint command",
        "step3":        "STEP 3 -- Agents",
        "agents_q":     "Select agents for this project",
        "step4":        "STEP 4 -- MCP integrations",
        "mcps_q":       "Select MCP servers to connect (skip if not needed yet)",
        "step5":        "STEP 5 -- Hooks (quality gates)",
        "hooks_q":      "Select hooks to enable",
        "hook_pre":     "pre-write (lint before write)",
        "hook_post":    "post-edit (test after edit)",
        "step6":        "STEP 6 -- Skills",
        "skills_q":     "Select skill templates to generate",
        "step7":        "STEP 7 -- Code style rules (.claude/rules/)",
        "rules_q":      "Select code style rule files to generate",
        "confirm":      "  Confirm -- files to be generated:",
        "grill_q":      "Enable Grilling Mode -- stress-test the plan before building? (y/n)",
        "proceed_q":    "Proceed with file generation? (y/n)",
        "cancelled":    "  Cancelled.",
        "generating":   "Generating files...",
        "done":         "  [DONE]  Bootstrap complete!",
        "next_steps":   "Next steps:",
        "hint":         "(enter numbers separated by commas, e.g. 1,3 -- or Enter to skip)",
        "grill_title":  "  [GRILL]  Grilling Phase -- Stress-test your plan",
        "grill_intro":  "  Answer honestly. Press Enter to skip a question.",
        "grill_you":    "You",
        "grill_done":   "Grilling complete -- {done}/{total} questions answered.",
        "recorded":     "Recorded.",
        "skipped":      "Skipped.",
        "label_project": "Project",
        "label_stack":   "Stack",
        "label_agents":  "Agents",
        "label_mcps":    "MCPs",
        "label_hooks":   "Hooks",
        "label_skills":  "Skills",
        "label_rules":   "Rules",
        "label_location": "Location",
        "label_output":  "Output structure:",
        "next1": "Add {BOLD}CLAUDE.local.md{RESET} to your .gitignore",
        "next2": "Review {BOLD}CLAUDE.md{RESET} -- fill in any TODO commands",
        "next3": "Open Claude Code: {BOLD}claude{RESET}",
        "next4": "Run {BOLD}/memory{RESET} to see your auto memory state",
        "next5": "Connect MCP servers in Claude Code settings",
        "portfolio_ok":   "Portfolio Registry updated in",
        "portfolio_fail": "Could not auto-update Portfolio Registry.",
        "portfolio_hint": "Add this row manually to the Portfolio Registry in",
        "agents_invoke":  "Invoke agents: @agent-orchestrator, @agent-code-reviewer, etc.",
        "agents_auto":    "Agents auto-delegate based on their description field.",
    },
    "vi": {
        "title":        "  [INIT]  Init Agentic -- Khởi tạo Claude Code Project",
        "intro":        "  Trả lời từng câu. Nhấn Enter để dùng giá trị mặc định.",
        "step1":        "BƯỚC 1 -- Thông tin project",
        "project_name": "Tên project",
        "description":  "Mô tả ngắn (1-2 câu về mục tiêu)",
        "step2":        "BƯỚC 2 -- Tech stack",
        "stack":        "Ngôn ngữ / framework chính",
        "run_cmd":      "Lệnh chạy / khởi động",
        "test_cmd":     "Lệnh chạy test",
        "lint_cmd":     "Lệnh lint",
        "step3":        "BƯỚC 3 -- Agents",
        "agents_q":     "Chọn agents cho project này",
        "step4":        "BƯỚC 4 -- MCP integrations",
        "mcps_q":       "Chọn MCP servers cần kết nối (bỏ qua nếu chưa cần)",
        "step5":        "BƯỚC 5 -- Hooks (quality gates)",
        "hooks_q":      "Chọn hooks muốn bật",
        "hook_pre":     "pre-write (lint trước khi write)",
        "hook_post":    "post-edit (test sau khi edit)",
        "step6":        "BƯỚC 6 -- Skills",
        "skills_q":     "Chọn skill templates cần tạo",
        "step7":        "BƯỚC 7 -- Code style rules (.claude/rules/)",
        "rules_q":      "Chọn rule files cần tạo",
        "confirm":      "  Xác nhận -- các files sẽ được tạo:",
        "grill_q":      "Bật Grilling Mode -- stress-test plan trước khi build? (y/n)",
        "proceed_q":    "Tiến hành tạo files? (y/n)",
        "cancelled":    "  Đã hủy.",
        "generating":   "Đang tạo files...",
        "done":         "  [DONE]  Bootstrap hoàn thành!",
        "next_steps":   "Bước tiếp theo:",
        "hint":         "(nhập số cách nhau bằng dấu phẩy, vd 1,3 -- hoặc Enter để bỏ qua)",
        "grill_title":  "  [GRILL]  Grilling Phase -- Stress-test kế hoạch",
        "grill_intro":  "  Trả lời thật lòng. Nhấn Enter để bỏ qua.",
        "grill_you":    "Bạn",
        "grill_done":   "Grilling hoàn tất -- {done}/{total} câu đã trả lời.",
        "recorded":     "Đã ghi nhận.",
        "skipped":      "Bỏ qua.",
        "label_project": "Project",
        "label_stack":   "Stack",
        "label_agents":  "Agents",
        "label_mcps":    "MCPs",
        "label_hooks":   "Hooks",
        "label_skills":  "Skills",
        "label_rules":   "Rules",
        "label_location": "Vị trí",
        "label_output":  "Cấu trúc output:",
        "next1": "Thêm {BOLD}CLAUDE.local.md{RESET} vào .gitignore",
        "next2": "Review {BOLD}CLAUDE.md{RESET} -- điền lệnh còn TODO",
        "next3": "Mở Claude Code: {BOLD}claude{RESET}",
        "next4": "Chạy {BOLD}/memory{RESET} để xem auto memory",
        "next5": "Kết nối MCP servers trong Claude Code settings",
        "portfolio_ok":   "Portfolio Registry đã được cập nhật trong",
        "portfolio_fail": "Không thể tự động cập nhật Portfolio Registry.",
        "portfolio_hint": "Tự thêm dòng này vào Portfolio Registry trong",
        "agents_invoke":  "Gọi agents: @agent-orchestrator, @agent-code-reviewer, ...",
        "agents_auto":    "Agents tự delegate dựa trên trường description của chúng.",
    },
}


def select_language() -> str:
    """Bilingual first question — returns 'en' or 'vi'."""
    print(f"\n{h(SEP)}")
    print(f"{h('  [INIT]  Init Agentic')}")
    print(f"{h(SEP)}")
    print(f"\n  Select language / Chọn ngôn ngữ:\n")
    print(f"  {dim('1.')} English")
    print(f"  {dim('2.')} Tiếng Việt")
    try:
        raw = input(f"\n{YELLOW}>{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return "vi" if raw == "2" else "en"


# ── Grilling engine ───────────────────────────────────────────────────────────
def make_grilling_tree(info: dict) -> list:
    """Generate project-specific grilling questions with contextual recommendations."""
    name  = info["name"]
    desc  = info["description"].rstrip(".")
    stack = info["stack"]
    desc60 = desc[:60] + "..." if len(desc) > 60 else desc

    return [
        {
            "key": "core_problem",
            "branch": "Goals & Scope",
            "question": "What core problem does this project solve — if it didn't exist, what would the user do instead?",
            "recommendation": (
                f"Draft: '{name} exists because [specific user] cannot {desc60.lower()} "
                f"without [root bottleneck]. Without it, they [current painful workaround].'"
            ),
        },
        {
            "key": "success_metric",
            "branch": "Goals & Scope",
            "question": "What does 'success' look like after 30 days? A specific number?",
            "recommendation": (
                f"Pick 1 metric for {name}: e.g., '[N] {stack} tasks automated/day', "
                f"'[X]% manual work eliminated', or '[N] pipeline runs without intervention'."
            ),
        },
        {
            "key": "out_of_scope",
            "branch": "Goals & Scope",
            "question": "What is explicitly NOT in scope for v1 — even if it sounds good?",
            "recommendation": (
                f"For a {stack} v1, cut at least 3: real-time streaming, multi-env deploy, "
                f"UI dashboard, access control, historical backfill -- "
                f"focus only on core {desc60.lower()}."
            ),
        },
        {
            "key": "primary_user",
            "branch": "Users",
            "question": "Who is your first user — a specific person, not 'everyone'?",
            "recommendation": (
                f"Name one real person who will use {name} first: "
                f"e.g., 'Alex, Analytics Engineer, runs {stack} queries daily, "
                f"currently spends 2h/day on manual checks.'"
            ),
        },
        {
            "key": "user_workflow",
            "branch": "Users",
            "question": "Before this tool exists, how does that user do this workflow today? How long does it take?",
            "recommendation": (
                f"Walk their current steps with {stack}: 1) open console, 2) run query manually, "
                f"3) copy result, 4) format & send -- biggest time sink = build that first."
            ),
        },
        {
            "key": "data_model",
            "branch": "Architecture",
            "question": "What are the core entities in your system and how do they relate?",
            "recommendation": (
                f"For {name} on {stack}: sketch 3-5 core tables/models. "
                f"E.g., events -> sessions -> users -> metrics. "
                f"Unclear model = major refactors later."
            ),
        },
        {
            "key": "state_management",
            "branch": "Architecture",
            "question": "Where is system state stored — who reads it, who writes it, when?",
            "recommendation": (
                f"For {stack}: source of truth = [primary warehouse], "
                f"incremental state = [run metadata / watermark table], "
                f"writer = pipeline, reader = analysts + BI tools."
            ),
        },
        {
            "key": "integration_points",
            "branch": "Architecture",
            "question": "What external services does this system depend on — and what happens if they go down?",
            "recommendation": (
                f"List each {name} dependency: source DBs, {stack} APIs, scheduler. "
                f"For each: fallback = retry / stale cache / alert? "
                f"Sync or async? Who owns the contract?"
            ),
        },
        {
            "key": "biggest_risk",
            "branch": "Risks",
            "question": "What could make this project fail completely in the first 3 months?",
            "recommendation": (
                f"Top risks for {name}: wrong assumption about source data quality, "
                f"{stack} dialect issues in prod, no stakeholder adoption, scope creep. "
                f"Which is highest? Prove it false before writing business logic."
            ),
        },
        {
            "key": "hardest_part",
            "branch": "Risks",
            "question": "Which technical part don't you know how to build yet — needs a spike first?",
            "recommendation": (
                f"On {stack}: which part is unproven -- incremental strategy, "
                f"cross-source join, scheduler trigger, data contract? "
                f"Build the smallest spike to validate it before the rest."
            ),
        },
        {
            "key": "agent_boundaries",
            "branch": "Agentic Design",
            "question": "Does each agent have clear boundaries — what does each one explicitly NOT do?",
            "recommendation": (
                f"For {name}: orchestrator delegates only, never writes {stack} code. "
                f"sql-reviewer reads only, never runs queries. "
                f"data-validator checks output only, never modifies data."
            ),
        },
        {
            "key": "human_in_loop",
            "branch": "Agentic Design",
            "question": "At which points is human approval required — where can't agents decide on their own?",
            "recommendation": (
                f"For {name}: require human sign-off before -- promoting to production, "
                f"deleting or truncating {stack} tables, sending external reports or alerts, "
                f"any schema migration on live data."
            ),
        },
    ]


def run_grilling(info: dict, lang: str = "en") -> list:
    s = STRINGS[lang]
    print(f"\n{h(SEP)}")
    print(f"{h(s['grill_title'])}")
    print(f"{h(SEP)}")
    print(dim(f"  Project: {info['name']} -- {info['description']}"))
    print(dim(f"  {s['grill_intro']}\n"))

    decisions = []
    current_branch = None
    grilling_tree = make_grilling_tree(info)
    total = len(grilling_tree)

    for i, item in enumerate(grilling_tree, 1):
        if item["branch"] != current_branch:
            current_branch = item["branch"]
            print(f"\n  {BOLD}-- {current_branch} --{RESET}")

        print(f"\n  {dim(f'[{i}/{total}]')} {BOLD}{item['question']}{RESET}")
        print(f"\n  {dim('1.')} {ans(item['recommendation'])}")
        print(dim(f"  (type 1 to accept -- or enter your own answer -- Enter to skip)"))

        try:
            answer = input(f"\n  {YELLOW}{s['grill_you']}:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if answer == "1":
            answer = item["recommendation"]

        if answer:
            decisions.append({
                "key": item["key"],
                "branch": item["branch"],
                "question": item["question"],
                "recommendation": item["recommendation"],
                "answer": answer,
            })
            print(f"  {ok(s['recorded'])}")
        else:
            print(f"  {dim(s['skipped'])}")

    done_msg = s["grill_done"].format(done=len(decisions), total=total)
    print(f"\n  {ok(done_msg)}")
    return decisions


# ── Helpers ───────────────────────────────────────────────────────────────────
def ask(prompt, default=""):
    suffix = f" {dim(f'[{default}]')}" if default else ""
    try:
        val = input(f"{q(prompt)}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return val if val else default


def ask_multi(prompt, options, defaults=None, hint=""):
    print(f"\n{q(prompt)}")
    for i, opt in enumerate(options, 1):
        marker = "*" if defaults and opt in defaults else " "
        print(f"  {dim(str(i)+'.')} {opt}  {dim(marker) if marker == '*' else ''}")
    print(dim(f"  {hint}"))
    try:
        raw = input(f"{YELLOW}>{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    if not raw:
        return defaults or []
    chosen = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(options):
                chosen.append(options[idx])
    return chosen if chosen else (defaults or [])


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(ok(f"Generated: {path}"))


def extract_description(template_str: str) -> str:
    """Parse the description field out of an agent template's frontmatter."""
    match = re.search(r"^---\n(.*?)\n---", template_str, re.DOTALL)
    if not match:
        return ""
    frontmatter = match.group(1)
    # Multiline description (> block)
    block = re.search(r"^description:\s*>\s*\n((?:[ \t]+.+\n?)+)", frontmatter, re.MULTILINE)
    if block:
        lines = [ln.strip() for ln in block.group(1).strip().splitlines() if ln.strip()]
        return " ".join(lines)
    # Single-line description
    single = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if single:
        return single.group(1).strip()
    return ""


# ── MCP catalog ───────────────────────────────────────────────────────────────
MCP_CATALOG = {
    "GitHub": {"type": "url", "url": "https://api.githubcopilot.com/mcp/", "name": "github"},
    "Notion": {"type": "url", "url": "https://mcp.notion.com/mcp", "name": "notion"},
    "Atlassian (Jira/Confluence)": {"type": "url", "url": "https://mcp.atlassian.com/v1/mcp", "name": "atlassian"},
    "Google Drive": {"type": "url", "url": "https://drivemcp.googleapis.com/mcp/v1", "name": "google-drive"},
    "Gmail": {"type": "url", "url": "https://gmailmcp.googleapis.com/mcp/v1", "name": "gmail"},
    "Slack": {"type": "url", "url": "https://mcp.slack.com/mcp", "name": "slack"},
    "Postman": {"type": "url", "url": "https://mcp.postman.com/minimal", "name": "postman"},
    "Figma": {"type": "url", "url": "https://mcp.figma.com/mcp", "name": "figma"},
}

# ── Agent templates ───────────────────────────────────────────────────────────
# description field is read by Claude on every turn for auto-delegation routing.
# Be specific: state WHEN to invoke and what NOT to use this agent for.
AGENT_TEMPLATES = {
    "orchestrator": """\
---
name: orchestrator
description: >
  High-level task planner for {name}.
  Auto-invoked when the request spans multiple steps or agents
  (e.g. "build feature X end-to-end", "plan the auth flow", "coordinate a refactor").
  NOT for: single-step edits, quick questions, running tests directly.
model: claude-opus-4-7
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
- Plan before coding — write the plan as a checklist first
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
model: claude-sonnet-4-6
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
model: claude-sonnet-4-6
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
model: claude-sonnet-4-6
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
model: claude-opus-4-7
effort: high
maxTurns: 20
disallowedTools:
  - Bash
  - Edit
---

You are the Business Analyst for project **{name}**.

## Role
Translate business needs into clear, unambiguous specifications that engineers
can implement without guessing. You define WHAT and WHY — never HOW.

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
model: claude-sonnet-4-6
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
model: claude-sonnet-4-6
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

# ── Rules templates ───────────────────────────────────────────────────────────
# Rules in .claude/rules/ are loaded by Claude Code automatically:
#   - files WITHOUT paths: -> loaded every session (like CLAUDE.md)
#   - files WITH paths:    -> loaded only when a matching file enters context
RULES_TEMPLATES = {
    "general": {
        "display": "general (no path filter -- always loaded)",
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
        "display": "python (**/*.py)",
        "filename": "python-style.md",
        "paths": ["**/*.py"],
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
        "display": "typescript (**/*.{ts,tsx,js,jsx})",
        "filename": "typescript-style.md",
        "paths": ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
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
        "display": "sql (**/*.sql)",
        "filename": "sql-style.md",
        "paths": ["**/*.sql"],
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


def gen_rules_file(key: str) -> str:
    tmpl = RULES_TEMPLATES[key]
    paths_yaml = ""
    if "paths" in tmpl:
        paths_lines = "\n".join(f'  - "{p}"' for p in tmpl["paths"])
        paths_yaml = f"paths:\n{paths_lines}\n"
    return f"---\n{paths_yaml}---\n\n{tmpl['content']}"


# ── Skill template ────────────────────────────────────────────────────────────
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


# ── Generators ────────────────────────────────────────────────────────────────
def gen_claude_md(info):
    agents_list = "\n".join(
        f"- `@agent-{a}` -- {extract_description(AGENT_TEMPLATES[a]).split('.')[0].replace('{name}', info['name'])}"
        for a in info["agents"] if a in AGENT_TEMPLATES
    )
    mcp_list = "\n".join(f"- {m}" for m in info["mcps"]) if info["mcps"] else "- (none configured)"
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
{info["run_cmd"] or "# TODO: add run command"}

# Test
{info["test_cmd"] or "# TODO: add test command"}

# Lint
{info["lint_cmd"] or "# TODO: add lint command"}
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
    """
    Generate .claude/settings.json.
    Hooks MUST be registered here -- Claude Code reads hook config from
    settings.json, not by scanning .claude/hooks/ automatically.
    """
    perms = {"allow": ["Bash", "Read", "Write", "Edit"], "deny": []}

    hooks_config = {}
    if "pre-write" in hooks:
        ext = ".ps1" if IS_WINDOWS else ".sh"
        cmd = (
            f"powershell -File .claude/hooks/pre-write{ext}"
            if IS_WINDOWS else
            f".claude/hooks/pre-write{ext}"
        )
        hooks_config["PreToolUse"] = [
            {"matcher": "Write", "hooks": [{"type": "command", "command": cmd}]}
        ]
    if "post-edit" in hooks:
        ext = ".ps1" if IS_WINDOWS else ".sh"
        cmd = (
            f"powershell -File .claude/hooks/post-edit{ext}"
            if IS_WINDOWS else
            f".claude/hooks/post-edit{ext}"
        )
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
    return json.dumps({"mcpServers": servers}, indent=2, ensure_ascii=False)


def gen_hook_bash(hook_type, info):
    if hook_type == "pre-write":
        lint = info.get("lint_cmd") or "echo 'no lint configured'"
        return f"""\
#!/bin/bash
# Hook: pre-write -- run lint before Claude writes a file
# Registered in .claude/settings.json under PreToolUse/Write
# Generated by init-agentic -- {date.today()}

FILE="$1"
if [ -z "$FILE" ]; then exit 0; fi

case "$FILE" in
  *.py|*.ts|*.js|*.tsx|*.jsx|*.sql)
    echo "[hook] Linting $FILE..."
    {lint} "$FILE" 2>&1 || true
    ;;
esac
"""
    elif hook_type == "post-edit":
        test_cmd = info.get("test_cmd") or "echo 'no test configured'"
        return f"""\
#!/bin/bash
# Hook: post-edit -- run quick test after Claude edits a file
# Registered in .claude/settings.json under PostToolUse/Edit
# Generated by init-agentic -- {date.today()}

echo "[hook] post-edit triggered. Running quick check..."
{test_cmd} 2>&1 | tail -5 || true
"""


def gen_hook_ps1(hook_type, info):
    if hook_type == "pre-write":
        lint = info.get("lint_cmd") or "Write-Host 'no lint configured'"
        return f"""\
# Hook: pre-write -- run lint before Claude writes a file
# Registered in .claude/settings.json under PreToolUse/Write
# Generated by init-agentic -- {date.today()}

param([string]$File)
if (-not $File) {{ exit 0 }}

$ext = [System.IO.Path]::GetExtension($File)
if ($ext -in @('.py','.ts','.js','.tsx','.jsx','.sql')) {{
    Write-Host "[hook] Linting $File..."
    try {{ {lint} $File 2>&1 }} catch {{ }}
}}
"""
    elif hook_type == "post-edit":
        test_cmd = info.get("test_cmd") or "Write-Host 'no test configured'"
        return f"""\
# Hook: post-edit -- run quick test after Claude edits a file
# Registered in .claude/settings.json under PostToolUse/Edit
# Generated by init-agentic -- {date.today()}

Write-Host "[hook] post-edit triggered. Running quick check..."
try {{
    {test_cmd} 2>&1 | Select-Object -Last 5
}} catch {{ }}
"""


def gen_claude_local():
    """Personal session notes -- gitignored, not committed."""
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
    """ADR-0001 in docs/adr/ -- official pattern for architectural decisions."""
    grilling_section = ""
    if grilling_decisions:
        branches: dict = {}
        for d in grilling_decisions:
            branches.setdefault(d["branch"], []).append(d)
        parts = ["\n## Grilling Session Decisions\n"]
        for branch, items in branches.items():
            parts.append(f"\n### {branch}\n")
            for item in items:
                parts.append(f"**Q:** {item['question']}\n\n")
                parts.append(f"> Recommended approach: {item['recommendation']}\n\n")
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


# ── Main wizard ───────────────────────────────────────────────────────────────
def run_wizard():
    lang = select_language()
    s    = STRINGS[lang]

    print(f"\n{h(SEP)}")
    print(f"{h(s['title'])}")
    print(f"{h(SEP)}")
    print(dim(f"  {s['intro']}\n"))

    cwd          = Path.cwd()
    default_name = cwd.name
    none_label   = "none" if lang == "en" else "không có"

    # Step 1: Project basics
    print(f"\n{h(s['step1'])}")
    name        = ask(s["project_name"], default_name)
    description = ask(s["description"], "")
    if not description:
        description = f"Project {name}."

    # Step 2: Tech stack
    print(f"\n{h(s['step2'])}")
    stack    = ask(s["stack"], "Python")
    run_cmd  = ask(s["run_cmd"], "")
    test_cmd = ask(s["test_cmd"], "")
    lint_cmd = ask(s["lint_cmd"], "")

    # Step 3: Agents — all shown, none pre-selected, user chooses freely
    print(f"\n{h(s['step3'])}")
    agent_options = list(AGENT_TEMPLATES.keys())
    chosen_agents = ask_multi(
        s["agents_q"],
        agent_options,
        defaults=[],
        hint=s["hint"],
    )

    # Step 4: MCP servers
    print(f"\n{h(s['step4'])}")
    chosen_mcps = ask_multi(
        s["mcps_q"],
        list(MCP_CATALOG.keys()),
        defaults=[],
        hint=s["hint"],
    )

    # Step 5: Hooks
    print(f"\n{h(s['step5'])}")
    hook_options     = [s["hook_pre"], s["hook_post"]]
    chosen_hooks_raw = ask_multi(s["hooks_q"], hook_options, defaults=hook_options, hint=s["hint"])
    chosen_hooks     = []
    if any("pre-write" in h_ for h_ in chosen_hooks_raw):
        chosen_hooks.append("pre-write")
    if any("post-edit" in h_ for h_ in chosen_hooks_raw):
        chosen_hooks.append("post-edit")

    # Step 6: Skills
    print(f"\n{h(s['step6'])}")
    skill_options = [
        "build-feature (implement a new feature end-to-end)",
        "deploy (deploy to staging or production)",
        "debug (systematic debugging workflow)",
        "refactor (improve code quality without changing behavior)",
    ]
    chosen_skills_raw = ask_multi(s["skills_q"], skill_options, defaults=[], hint=s["hint"])
    chosen_skills     = [sk.split(" ")[0] for sk in chosen_skills_raw]

    # Step 7: Code rules — auto-detect from stack, but no forced defaults
    print(f"\n{h(s['step7'])}")
    rule_options = [RULES_TEMPLATES[k]["display"] for k in RULES_TEMPLATES]
    rule_keys    = list(RULES_TEMPLATES.keys())

    stack_lower        = stack.lower()
    auto_rule_displays = [RULES_TEMPLATES["general"]["display"]]
    if "python" in stack_lower:
        auto_rule_displays.append(RULES_TEMPLATES["python"]["display"])
    if any(x in stack_lower for x in ["typescript", "javascript", "react", "node", "next", "vue"]):
        auto_rule_displays.append(RULES_TEMPLATES["typescript"]["display"])
    if any(x in stack_lower for x in ["sql", "dbt", "bigquery", "postgres", "mysql", "snowflake"]):
        auto_rule_displays.append(RULES_TEMPLATES["sql"]["display"])

    chosen_rule_displays = ask_multi(s["rules_q"], rule_options, defaults=auto_rule_displays, hint=s["hint"])
    chosen_rules         = [rule_keys[i] for i, d in enumerate(rule_options) if d in chosen_rule_displays]

    # Summary
    print(f"\n{h(SEP)}")
    print(f"{h(s['confirm'])}")
    print(f"  {s['label_project']:10s}: {BOLD}{name}{RESET}")
    print(f"  {s['label_stack']:10s}: {stack}")
    print(f"  {s['label_agents']:10s}: {', '.join(chosen_agents) or none_label}")
    print(f"  {s['label_mcps']:10s}: {', '.join(chosen_mcps) or none_label}")
    print(f"  {s['label_hooks']:10s}: {', '.join(chosen_hooks) or none_label}")
    print(f"  {s['label_skills']:10s}: {', '.join(chosen_skills) or none_label}")
    print(f"  {s['label_rules']:10s}: {', '.join(chosen_rules) or none_label}")
    print(f"{h(SEP)}")

    # Grilling
    want_grill        = ask(s["grill_q"], "y")
    grilling_decisions = []
    if want_grill.lower() == "y":
        grilling_decisions = run_grilling({"name": name, "description": description}, lang=lang)

    # Final confirm
    print(f"\n{h(SEP)}")
    confirm = ask(s["proceed_q"], "y")
    if confirm.lower() != "y":
        print(dim(s["cancelled"]))
        sys.exit(0)

    return {
        "name": name,
        "description": description,
        "stack": stack,
        "run_cmd": run_cmd,
        "test_cmd": test_cmd,
        "lint_cmd": lint_cmd,
        "agents": chosen_agents,
        "mcps": chosen_mcps,
        "hooks": chosen_hooks,
        "skills": chosen_skills,
        "rules": chosen_rules,
        "grilling_decisions": grilling_decisions,
        "lang": lang,
    }


# ── Portfolio Registry ────────────────────────────────────────────────────────
GLOBAL_CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"

PORTFOLIO_PLACEHOLDER = "| (chưa có project nào — thêm khi bootstrap) | | | |"
PORTFOLIO_HEADER      = "| Project | Status | BA Docs | Repos |"
PORTFOLIO_SEPARATOR   = re.compile(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|")


def update_portfolio(info: dict, target: Path) -> bool:
    """
    Add this project to the Portfolio Registry table in ~/.claude/CLAUDE.md.
    Returns True if updated, False if the file or section was not found.
    """
    if not GLOBAL_CLAUDE_MD.exists():
        return False

    content = GLOBAL_CLAUDE_MD.read_text(encoding="utf-8")
    if "Portfolio Registry" not in content:
        return False

    new_row = f"| {info['name']} | Active | | {target} |"

    # Case 1: placeholder row still present — replace it
    if PORTFOLIO_PLACEHOLDER in content:
        content = content.replace(PORTFOLIO_PLACEHOLDER, new_row)
        GLOBAL_CLAUDE_MD.write_text(content, encoding="utf-8")
        return True

    # Case 2: table exists with real rows — insert after separator row
    # Find the Portfolio Registry section first, then the separator within it
    portfolio_start = content.find("## Portfolio Registry")
    if portfolio_start == -1:
        return False

    section = content[portfolio_start:]
    sep_match = PORTFOLIO_SEPARATOR.search(section)
    if not sep_match:
        return False

    # Check project not already listed
    if f"| {info['name']} |" in section:
        return True  # already present, no-op

    insert_at = portfolio_start + sep_match.end()
    content = content[:insert_at] + "\n" + new_row + content[insert_at:]
    GLOBAL_CLAUDE_MD.write_text(content, encoding="utf-8")
    return True


# ── File generation ───────────────────────────────────────────────────────────
def generate_files(info, target: Path):
    s = STRINGS.get(info.get("lang", "en"))
    print(f"\n{h(s['generating'])}\n")

    # CLAUDE.md -- project context (committed, shared)
    write_file(target / "CLAUDE.md", gen_claude_md(info))

    # CLAUDE.local.md -- personal session notes (gitignored)
    write_file(target / "CLAUDE.local.md", gen_claude_local())

    # .mcp.json -- MCP server config at project root
    if info["mcps"]:
        write_file(target / ".mcp.json", gen_mcp_json(info["mcps"]))

    # .claude/settings.json -- permissions + hook registrations
    write_file(target / ".claude" / "settings.json", gen_settings(info["agents"], info["hooks"]))

    # .claude/registry.md -- agent task registry
    write_file(target / ".claude" / "registry.md", gen_registry())

    # .claude/agents/*.md
    for agent_key in info["agents"]:
        if agent_key in AGENT_TEMPLATES:
            content = AGENT_TEMPLATES[agent_key].format(name=info["name"])
            write_file(target / ".claude" / "agents" / f"{agent_key}.md", content)

    # .claude/rules/*.md -- NEW: file-type coding rules
    for rule_key in info["rules"]:
        if rule_key in RULES_TEMPLATES:
            filename = RULES_TEMPLATES[rule_key]["filename"]
            write_file(target / ".claude" / "rules" / filename, gen_rules_file(rule_key))

    # .claude/skills/*/SKILL.md
    skill_descriptions = {
        "build-feature": "Implement a new feature from scratch, including code and tests.",
        "deploy": "Deploy the project to a staging or production environment.",
        "debug": "Analyze errors systematically: reproduce, isolate, fix, verify.",
        "refactor": "Improve code quality without changing observable behavior.",
    }
    for skill_name in info["skills"]:
        desc = skill_descriptions.get(skill_name, f"Skill: {skill_name}")
        write_file(
            target / ".claude" / "skills" / skill_name / "SKILL.md",
            make_skill(skill_name, desc, info["stack"]),
        )

    # .claude/hooks/*.sh or .ps1
    for hook in info["hooks"]:
        if IS_WINDOWS:
            content  = gen_hook_ps1(hook, info)
            ext      = ".ps1"
        else:
            content  = gen_hook_bash(hook, info)
            ext      = ".sh"
        hook_path = target / ".claude" / "hooks" / f"{hook}{ext}"
        write_file(hook_path, content)
        if not IS_WINDOWS:
            os.chmod(hook_path, 0o755)

    # docs/adr/0001-bootstrap.md -- architectural decision record
    write_file(
        target / "docs" / "adr" / "0001-bootstrap.md",
        gen_adr(info, info.get("grilling_decisions", [])),
    )

    # docs/learnings.md
    write_file(target / "docs" / "learnings.md", gen_learnings())


def print_summary(info, target: Path, portfolio_updated: bool = False):
    s = STRINGS.get(info.get("lang", "en"))

    print(f"\n{h(SEP)}")
    print(f"{h(s['done'])}")
    print(f"{h(SEP)}\n")
    print(f"  {s['label_project']:10s}: {BOLD}{info['name']}{RESET}")
    print(f"  {s['label_location']:10s}: {target}\n")

    print(f"  {CYAN}{s['label_output']}{RESET}")
    print(f"  {BOLD}CLAUDE.md{RESET}                   <- project context (commit this)")
    print(f"  {BOLD}CLAUDE.local.md{RESET}              <- session notes  (gitignore this)")
    print(f"  {BOLD}.claude/agents/{RESET}              <- sub-agent definitions")
    print(f"  {BOLD}.claude/rules/{RESET}               <- code style rules (auto-loaded)")
    print(f"  {BOLD}.claude/settings.json{RESET}        <- permissions + hook registrations")
    print(f"  {BOLD}docs/adr/0001-bootstrap.md{RESET}   <- architectural decision record")
    print(f"  {BOLD}docs/learnings.md{RESET}            <- lessons log")
    print()

    # Portfolio status
    if portfolio_updated:
        print(f"  {ok(s['portfolio_ok'])} {dim(str(GLOBAL_CLAUDE_MD))}")
    else:
        print(f"  {warn(s['portfolio_fail'])}")
        manual_row = f"| {info['name']} | Active | | {target} |"
        print(f"  {s['portfolio_hint']} {dim(str(GLOBAL_CLAUDE_MD))}:")
        print(f"  {dim(manual_row)}")
    print()

    print(f"  {CYAN}{s['next_steps']}{RESET}")
    print(f"  1. {s['next1']}")
    print(f"  2. {s['next2']}")
    print(f"  3. {s['next3']}")
    print(f"  4. {s['next4']}")
    if info["mcps"]:
        print(f"  5. {s['next5']}")
    print()

    gd = info.get("grilling_decisions", [])
    if gd:
        label = f"Grilling summary ({len(gd)} decisions)" if info.get("lang") == "en" else f"Grilling ({len(gd)} quyết định)"
        print(f"  {CYAN}{label}:{RESET}")
        for d in gd[:3]:
            short_q = d["question"][:65] + "..." if len(d["question"]) > 65 else d["question"]
            print(f"  {dim('*')} {short_q}")
        if len(gd) > 3:
            print(f"  {dim(f'  ... +{len(gd)-3} more in docs/adr/0001-bootstrap.md')}")
        print()

    print(dim(f"  {s['agents_invoke']}"))
    print(dim(f"  {s['agents_auto']}\n"))


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    target = Path.cwd()
    if len(sys.argv) > 1:
        target = Path(sys.argv[1]).expanduser().resolve()
        target.mkdir(parents=True, exist_ok=True)

    info = run_wizard()
    generate_files(info, target)
    portfolio_updated = update_portfolio(info, target)
    print_summary(info, target, portfolio_updated)


if __name__ == "__main__":
    main()
