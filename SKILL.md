---
name: init-agentic
description: >
  Bootstrap a complete Claude Code agentic project structure interactively.
  Trigger: "init project", "bootstrap agents", "setup claude", "init agentic",
  "grill me on this project", "stress-test my plan", "scaffold agentic setup",
  "khởi tạo project", "tạo project mới", "bootstrap project".
version: "4.2.0"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# Init Agentic v4.2 — Claude-driven Wizard

You are running the Init Agentic wizard. Follow EVERY step in order.
Do NOT skip steps. Do NOT generate files before completing all steps.

Architecture:
- **Claude** handles the wizard: open intake → iterative clarification → selection (Steps 0–8)
- **Python script** handles file generation only (Step 9)

---

## Core Principle — Dynamic Context Expansion

At every step, use ALL context gathered so far (name, description, stack, prior answers) to make
the options smarter. Never show a generic fixed list when you have enough context to recommend.

**How to apply:**
- `description` field: extract domain keywords (data pipeline, e-commerce, API, dashboard…)
- `stack` field: detect languages, frameworks, tools
- Prior step answers: agents already selected inform MCP suggestions; stack informs rules

**In each AskUserQuestion call:**
- Put the most context-relevant options first
- Add `(Recommended for your stack)` or `(phù hợp với stack của bạn)` in `description` for strongly suggested items
- Options should feel like they were written specifically for THIS project, not copy-pasted from a template

**Do not ask for information you can infer.** If description says "Airflow DAG pipeline", do not
ask if they need a data-validator agent — suggest it directly as recommended.

---

## STEP 0 — Language Selection (ALWAYS FIRST, no exceptions)

Use `AskUserQuestion` tool:
```json
{
  "questions": [{
    "question": "Select language / Chọn ngôn ngữ:",
    "header": "Language",
    "multiSelect": false,
    "options": [
      {"label": "English", "description": "Run the wizard in English"},
      {"label": "Tiếng Việt", "description": "Chạy wizard bằng tiếng Việt"}
    ]
  }]
}
```

Store the answer as `lang` (`en` or `vi`).
Use the chosen language for ALL subsequent questions, labels, and messages.

---

## STEP 1 — Open Intake

Ask a single open question — accept any rough answer, do not demand structure:

> EN: "Tell me about this project — what it does, who uses it, and what stack you're thinking. As rough as you want."
> VI: "Kể về project này — mục tiêu là gì, ai dùng, dự định dùng stack nào. Cứ nói tự nhiên."

From the answer, extract:
- `name` — if not mentioned, use the current working directory name
- `description` — a rough summary of what was said

Do NOT ask follow-up questions yet. Proceed immediately to STEP 2 with what you have.

---

## STEP 2 — BA Requirements Discovery

This step delegates to the `grill-me` skill for relentless one-at-a-time questioning.
Your job here is to: (1) frame the session, (2) invoke grill-me, (3) extract the answers.

### 2a — Frame and announce

Tell the user what's about to happen:
> EN: "I'll now grill you on this project to get requirements clear — BA style. I'll start with WHY and work toward HOW. Answer as roughly as you want."
> VI: "Tôi sẽ hỏi sâu để làm rõ yêu cầu — theo kiểu BA. Bắt đầu từ TẠI SAO rồi đến NHƯ THẾ NÀO. Trả lời tự nhiên thôi."

### 2b — Invoke grill-me

Call `Skill("grill-me")` and follow its instructions.

While running the grill-me session, apply BA ordering to your questions — work through
these tiers in sequence (skip any already answered from STEP 1):

| Tier | Questions to resolve |
|------|---------------------|
| 1 — Why & Who | Business problem, urgency, sponsor, primary user |
| 2 — Value & Scope | Success metric, current workaround, v1 deliverable, explicit out-of-scope |
| 3 — Risk & Constraints | Key assumption, production risk, external dependencies, deadline |
| 4 — Technical | Stack, data sources, run/test/lint commands |

Do NOT jump to Tier 4 before Tiers 1–3 are resolved.
Use `AskUserQuestion` for each question (multiSelect: false) — synthesize 2–3 project-specific
options with your recommended answer first, labeled `(Recommended)`.

### 2c — Stop condition

Stop the grill-me session when ALL of the following are known:
- Why this project exists and why now
- Who uses it and who sponsors/owns it
- Measurable success criteria for v1
- What is explicitly OUT of scope for v1
- At least 1 critical risk or unvalidated assumption
- Stack / language / framework (inferred or confirmed)
- Run, test, lint commands (or "none yet" confirmed)

If any item above is still unknown and would affect agent/rule/hook recommendations — keep grilling.

### 2d — Extract and summarise

When stop condition is met, end the grill-me session and print a BA spec summary:

```
Problem    : <why this exists>
Sponsor    : <who owns it>
Users      : <who uses it daily>
Success    : <measurable v1 outcome>
In scope   : <core v1 deliverable>
Out of v1  : <explicit exclusions>
Key risk   : <what could break this>
Stack      : <language + framework>
Commands   : run=<cmd> | test=<cmd> | lint=<cmd>
```

Then say:
> EN: "Requirements clear — moving on to design agents and tools."
> VI: "Đã rõ yêu cầu — tiếp tục thiết kế agents và tools."

Proceed directly to STEP 3. Do NOT ask "is this correct?"

---

## STEP 3 — Agent Design

Do NOT copy from a fixed catalog. Design agents from this project's domain and workflow.

### 3a — Propose roles

From the BA spec, identify roles the project genuinely needs. Ask per role:
- What recurring task does this agent own end-to-end?
- What does it explicitly NOT do? (routing clarity)
- Does this need a separate agent, or can another handle it?

Max 5 agents. Fewer focused agents beat many overlapping ones.

Name agents after their role in THIS project — not generic names.
Example: `pipeline-orchestrator` not `orchestrator`; `sql-reviewer` not `reviewer`.

Use AskUserQuestion (multiSelect: true, max 4 options per call — use 2 calls if >4 proposals):
- Label = project-specific role name
- Description = one sentence: what it owns + what triggers it

Example for a HubSpot→BigQuery data pipeline:
```json
{
  "questions": [{
    "question": "Which agent roles should this project have?",
    "header": "Agents",
    "multiSelect": true,
    "options": [
      {"label": "pipeline-orchestrator", "description": "Breaks complex DAG tasks into steps; delegates SQL work to sql-reviewer (Recommended)"},
      {"label": "sql-reviewer", "description": "Reviews every .sql and dbt model; checks BigQuery dialect, cost, and naming conventions (Recommended)"},
      {"label": "data-validator", "description": "Runs after each DAG execution to verify row counts, nulls, and schema against expectations"},
      {"label": "requirements-analyst", "description": "Writes specs and acceptance criteria for new pipeline features before implementation begins"}
    ]
  }]
}
```

### 3b — Generate agent content

For EACH confirmed agent, Claude writes the full agent markdown.
Use all BA spec context (stack, tools, file paths, domain) — not placeholders.

Template structure (adapt freely):
```markdown
---
name: <agent-name>
description: >
  <When to auto-invoke this agent — specific trigger phrases for this project>
model: claude-opus-4-7   # for planning/BA roles; claude-sonnet-4-6 for others
---

# <Agent Name> — <Project Name>

## Role
<One paragraph: what this agent owns, domain context, why it exists>

## Responsibilities
- <specific task using actual stack/tools/paths from BA spec>
- <another specific task>

## Constraints
- <explicit boundary — what it will NOT do, to prevent overlap>
- <another boundary>

## Handoffs
- Delegates to: <other agents in this project>
- Receives from: <which agents or user actions trigger it>
```

Store each as: `{"path": ".claude/agents/<name>.md", "content": "<full markdown>"}`

---

## STEP 4 — MCP Integrations

Only propose MCPs with clear justification from the BA spec.
Do NOT show a full catalog — only what fits this project.

Infer from BA spec keywords:
- "GitHub", "PR", "code review" → GitHub MCP
- "Jira", "ticket", "Confluence" → Atlassian MCP
- "Notion", "wiki" → Notion MCP
- "Slack", "alert", "notification" → Slack MCP
- "Postman", "API testing", "endpoint" → Postman MCP
- "Figma", "design", "UI" → Figma MCP
- "Gmail", "email" → Gmail MCP
- "Drive", "GSheet", "spreadsheet" → Google Drive MCP

Use AskUserQuestion (multiSelect: true). Only show MCPs with a match.
If fewer than 2 matches found, offer "None — skip MCP setup" as first option.

For each option, explain WHY it fits this project specifically:
```json
{
  "questions": [{
    "question": "Which external integrations does Claude need access to?",
    "header": "MCPs",
    "multiSelect": true,
    "options": [
      {"label": "GitHub", "description": "For reading PRs and issues — your pipeline code lives on GitHub (Recommended)"},
      {"label": "Slack", "description": "For posting pipeline alerts — mentioned as the notification channel"},
      {"label": "None", "description": "Skip MCP setup for now"}
    ]
  }]
}
```

MCP server configs are fixed per provider — stored as `mcps: ["github", "slack"]` in spec.
Python script writes the `.mcp.json` from this list.

---

## STEP 5 — Hooks

Use `AskUserQuestion` (multiSelect: true). Build descriptions from actual commands from STEP 2.

| Hook | Event | Recommend when |
|------|-------|----------------|
| `pre-write` | PreToolUse → Write | `lint_cmd` is known |
| `post-edit` | PostToolUse → Edit | `test_cmd` is known |
| `session-end` | Stop | Always |
| `notification` | Notification | CI, async workflows, or alerts mentioned |

Example with ruff + pytest from STEP 2:
```json
{
  "questions": [{
    "question": "Select hooks to register:",
    "header": "Hooks",
    "multiSelect": true,
    "options": [
      {"label": "pre-write", "description": "Runs `ruff check .` before Claude writes any file (Recommended)"},
      {"label": "post-edit", "description": "Runs `pytest` after Claude edits any file (Recommended)"},
      {"label": "session-end", "description": "Appends session marker to CLAUDE.local.md on Stop (Recommended)"},
      {"label": "notification", "description": "Logs Claude Code notifications to .claude/notifications.log"}
    ]
  }]
}
```

Store as `hooks: ["pre-write", "post-edit", "session-end"]`.
Python script writes hook scripts and registers them in `settings.json`.

---

## STEP 6 — Slash Commands

Do NOT scaffold generic commands. Design commands around workflows THIS project actually repeats.
A slash command is worth creating when: multi-step, repeated, currently done manually.

### 6a — Propose commands

From BA spec: identify 2–4 high-value recurring workflows.
Name commands after the actual workflow — not abstract categories.
Example: `/scaffold-dag-feature` not `/build-feature`; `/validate-pipeline` not `/write-tests`.

Use AskUserQuestion (multiSelect: true, max 4 options):
```json
{
  "questions": [{
    "question": "Which slash commands should Claude know for this project?",
    "header": "Commands",
    "multiSelect": true,
    "options": [
      {"label": "scaffold-dag-feature", "description": "BA spec → staging model → mart → Airflow DAG → validation in one flow (Recommended)"},
      {"label": "validate-pipeline-output", "description": "Runs data-validator checks on the latest DAG run — row counts, nulls, schema"},
      {"label": "sync-docs", "description": "Updates README and OpenMetadata descriptions after model changes"},
      {"label": "review-sql-changes", "description": "Runs sql-reviewer on staged .sql/.yml files before commit"}
    ]
  }]
}
```

### 6b — Generate command content

For EACH confirmed command, Claude writes the full SKILL.md.
Reference actual paths, tools, agents, and patterns from BA spec — not generic steps.

Template structure:
```markdown
---
name: <command-name>
description: >
  <When to use this. Specific trigger for this project.>
allowed-tools:
  - <tools needed>
---

# <Command Name>

## When to use
<Specific situation that triggers this command in this project>

## Steps
1. <Concrete step with actual file paths, commands, agent calls from BA spec>
2. <Next step>
3. <...>

## Done when
<How to verify the command completed correctly for this project>
```

Store each as: `{"path": ".claude/skills/<command-name>/SKILL.md", "content": "<full markdown>"}`

---

## STEP 7 — Code Style Rules

### 7a — Confirm rule sets

Auto-suggest from stack. Always include `general`.
Use AskUserQuestion (multiSelect: true):
```json
{
  "questions": [{
    "question": "Which rule sets to generate?",
    "header": "Rules",
    "multiSelect": true,
    "options": [
      {"label": "general", "description": "Always loaded — project context + critical constraints (Recommended)"},
      {"label": "python", "description": "Auto-loaded for *.py — ruff, type hints, project conventions"},
      {"label": "sql", "description": "Auto-loaded for *.sql — BigQuery dialect, dbt patterns, naming"},
      {"label": "typescript", "description": "Auto-loaded for *.ts/*.tsx/*.js/*.jsx"}
    ]
  }]
}
```

### 7b — Generate rule content

Do NOT copy generic templates. Write rules that reference actual project constraints.

`general` rule always includes:
- Brief project context (so Claude remembers domain every session)
- Critical constraints from BA spec (e.g., "never DROP tables", "always read specs before coding")
- Key workflow rules (lint before commit, read BA doc before implementing)

Stack-specific rules include:
- Actual tools (ruff, pytest, dbt, etc.) with actual commands
- Naming conventions specific to this project
- Patterns or anti-patterns discovered during BA discovery

Store each as: `{"path": ".claude/rules/<name>.md", "content": "<full markdown>"}`

---

## STEP 7b — Environment, Model & Permissions

Three quick optional configurations. All have "Skip / use default" as the first option.

### Env vars

Analyze `stack` from Step 2. Suggest relevant env var keys (values are placeholders — user fills in later).

Stack → suggested vars:
- dbt → `DBT_PROFILES_DIR`, `DBT_PROJECT_DIR`
- BigQuery → `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLOUD_PROJECT`
- Airflow → `AIRFLOW_HOME`, `AIRFLOW__CORE__DAGS_FOLDER`
- Python → `PYTHONPATH`
- Node / Next / React → `NODE_ENV`, `PORT`
- Snowflake → `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE`
- Postgres → `DATABASE_URL`

Use `AskUserQuestion` (multiSelect: true). Always include "None needed" as an option.
Store selected keys as `env: { "KEY": "# TODO: set value" }` in the spec.

**Note:** env block is for non-secret config paths. Secrets should go in `.env` (gitignored), not `settings.json`.

### Model override

Use `AskUserQuestion` (multiSelect: false). Default = "Inherit global":

```json
{
  "questions": [{
    "question": "Claude model for this project?",
    "header": "Model",
    "multiSelect": false,
    "options": [
      {"label": "Inherit global settings", "description": "Use whatever model is set globally (Recommended for most projects)"},
      {"label": "claude-sonnet-4-6", "description": "Fast and cost-effective — good default for most tasks"},
      {"label": "claude-opus-4-7", "description": "Most capable — for complex reasoning-heavy projects"},
      {"label": "claude-haiku-4-5-20251001", "description": "Fastest — for high-volume simple tasks"}
    ]
  }]
}
```

Store as `model: ""` (empty = inherit) or the selected model ID.

### Permission preset

Use `AskUserQuestion` (multiSelect: false). Default = "standard":

```json
{
  "questions": [{
    "question": "Permission level for Claude in this project?",
    "header": "Permissions",
    "multiSelect": false,
    "options": [
      {"label": "standard", "description": "Allow Bash, Read, Write, Edit — no extra restrictions (Recommended)"},
      {"label": "data-safe", "description": "Standard + deny destructive commands: rm -rf, DROP, DELETE, TRUNCATE"},
      {"label": "strict", "description": "Read and Edit only — no Bash (for review-only or sensitive codebases)"}
    ]
  }]
}
```

Store as `permission_preset: "standard"` (or selected value).

---

## STEP 8 — Summary & Confirm

Print a clean summary of all selections. Example:

```
Project     : MyProject
Stack       : Python + dbt
Agents      : orchestrator, ba-agent, sql-reviewer, data-validator
MCPs        : none
Hooks       : pre-write, post-edit, session-end
Skills      : build-feature
Rules       : general, python, sql
Env vars    : DBT_PROFILES_DIR, GOOGLE_APPLICATION_CREDENTIALS
Model       : inherit global
Permissions : data-safe
```

Use `AskUserQuestion` tool to confirm:

```json
{
  "questions": [{
    "question": "Proceed with generating files? / Tiến hành tạo file?",
    "header": "Confirm",
    "multiSelect": false,
    "options": [
      {"label": "Yes — generate files", "description": "Proceed / Tiến hành"},
      {"label": "No — start over", "description": "Cancel and restart the wizard"}
    ]
  }]
}
```

If user selects "No", restart from STEP 1.

---

## STEP 9 — Generate Files

Build the JSON spec, then run the generator. The spec carries **full file contents** — the Python
script is a pure file writer with no template logic.

### STEP 9a — Generate CLAUDE.md content (Claude writes this)

Before building the spec, Claude writes the project's `CLAUDE.md` inline.
Do NOT copy a template — write from BA spec context.

Structure:
```markdown
# <Project Name>

## Project context
<2–3 sentences: what this project does, who uses it, why it matters>

## Stack
<List: language, frameworks, tools — from BA spec>

## Commands
- run: `<run_cmd or TBD>`
- test: `<test_cmd or TBD>`
- lint: `<lint_cmd or TBD>`

## Critical constraints
<From BA spec Tier 3: risks, rules Claude must always respect>

## Agent routing
<For each agent: when to invoke it, what it owns>

## Key paths
<Important directories/files for this project>
```

### STEP 9b — Spec format

Write spec to `~/.claude/.init_spec.json`:

```json
{
  "name": "<project name>",
  "description": "<project description>",
  "stack": "<from STEP 2>",
  "run_cmd": "<or empty>",
  "test_cmd": "<or empty>",
  "lint_cmd": "<or empty>",
  "mcps": ["github", "slack"],
  "hooks": ["pre-write", "post-edit", "session-end"],
  "env": {"KEY": "# TODO: set value"},
  "model": "<model ID or empty string>",
  "permission_preset": "standard",
  "lang": "en",
  "files": [
    {"path": "CLAUDE.md",          "content": "<Claude-generated content from 9a>"},
    {"path": "CLAUDE.local.md",    "content": "<session notes template>"},
    {"path": ".claude/agents/<name>.md",          "content": "<from STEP 3b>"},
    {"path": ".claude/skills/<command>/SKILL.md", "content": "<from STEP 6b>"},
    {"path": ".claude/rules/general.md",          "content": "<from STEP 7b>"},
    {"path": ".claude/rules/<name>.md",           "content": "<from STEP 7b, per stack>"},
    {"path": ".claude/registry.md",               "content": "<task log template with project name>"},
    {"path": "docs/adr/0001-bootstrap.md",        "content": "<ADR with actual decisions from this session>"},
    {"path": "docs/learnings.md",                 "content": "<empty learnings log with date>"}
  ]
}
```

**Key:** `files` contains every Claude-generated file. The Python script writes each `path`/`content`
pair as-is — no template substitution needed.

Files NOT in `files` (Python script generates these from spec metadata):
- `.gitignore` — always append `CLAUDE.local.md`
- `.mcp.json` — from `mcps` list, fixed config per provider
- `.claude/settings.json` — from `hooks`, `model`, `permission_preset`, `env`
- `.claude/hooks/*.sh|.ps1` — from `hooks` list + `lint_cmd`/`test_cmd`

### STEP 9c — Run the generator

Detect Python command:
```bash
python --version 2>&1 || python3 --version 2>&1 || py --version 2>&1
```

Run:
```bash
# Unix / macOS
python3 ~/.claude/skills/init-agentic/scripts/init_agentic.py \
  --from-spec ~/.claude/.init_spec.json "<target>"

# Windows
python "$HOME\.claude\skills\init-agentic\scripts\init_agentic.py" `
  --from-spec "$HOME\.claude\.init_spec.json" "<target>"
```

Delete spec after success:
```bash
rm ~/.claude/.init_spec.json            # Unix
Remove-Item "$HOME\.claude\.init_spec.json"  # Windows
```

### Fallback — if Python unavailable

Use the Write tool directly. For each item in `files`, write `content` to `path` (relative to target).
Then write `.gitignore`, `.mcp.json`, `.claude/settings.json`, hook scripts using formulas below.

**Hook registration in `.claude/settings.json`:**
- `pre-write` → event `PreToolUse`, matcher `Write`, command = lint_cmd
- `post-edit` → event `PostToolUse`, matcher `Edit`, command = test_cmd
- `session-end` → event `Stop`, command appends marker to `CLAUDE.local.md`
- `notification` → event `Notification`, command logs to `.claude/notifications.log`
- Windows: `powershell -File .claude/hooks/<name>.ps1`
- Unix: `.claude/hooks/<name>.sh`

---

## STEP 10 — Portfolio Registry Update

After generating files, update `~/.claude/CLAUDE.md` Portfolio Registry table:
- Find the `## Portfolio Registry` section
- Replace the placeholder row OR insert a new row after the separator:
  `| <project-name> | Active | | <project-path> |`

(The Python script does this automatically. Only needed for the fallback path.)

---

## STEP 11 — Summary

Print a final summary in the chosen language with three sections:

### Section A — Generated files (list only what was actually created)

```
your-project/
├── CLAUDE.md              ← project context Claude reads every session
├── CLAUDE.local.md        ← your private session notes (add to .gitignore)
├── .mcp.json              ← MCP server config (if MCPs selected)
├── .claude/
│   ├── settings.json      ← permissions + hook registrations
│   ├── registry.md        ← task log: what each agent did and when
│   ├── agents/            ← one file per agent (Claude reads when delegating)
│   ├── rules/             ← code style rules, auto-loaded by file type
│   ├── skills/            ← slash commands you can invoke in any session
│   └── hooks/             ← scripts that run before/after Claude's actions
└── docs/
    ├── adr/0001-bootstrap.md  ← why this structure was chosen
    └── learnings.md           ← lessons captured across sessions
```

### Section B — What each part does (explain in plain language, adapted to selections made)

For each file/folder that was generated, give one sentence explaining its role.
Use the actual project name and stack in the explanation — not generic placeholders.

Example for a Python + Airflow project:

| Part | Role |
|------|------|
| `CLAUDE.md` | Project bible — stack, conventions, agent routing. Claude reads this first every session so you never repeat context. |
| `CLAUDE.local.md` | Your scratchpad — blockers, current focus, session notes. Never committed. |
| `.claude/agents/orchestrator.md` | When Claude sees a complex task, it delegates to this agent to break it into subtasks across your Airflow DAGs. |
| `.claude/agents/data-validator.md` | Runs after pipeline execution to verify output counts, nulls, and schema match expectations. |
| `.claude/rules/python.md` | Loaded automatically for every `.py` file — enforces ruff, type hints, and your dbt/Airflow patterns. |
| `.claude/hooks/pre-write.ps1` | Runs `ruff check .` before Claude writes any file. Catches lint errors before they land in code. |
| `.claude/registry.md` | Agent task log — what was done, by which agent, and when. Helps you pick up after a break. |
| `docs/adr/0001-bootstrap.md` | Records why this agent structure was chosen for this project. |

Generate this table dynamically using the actual agents, rules, hooks, and commands from this session.

### Section C — Next steps (3–5 bullets, specific to this project)

- Add `CLAUDE.local.md` to `.gitignore`
- Fill in any TODO commands in `CLAUDE.md` (run, test, lint)
- Commit `CLAUDE.md`, `.claude/`, `docs/` as the project baseline
- Mention which agents are ready to use and how to invoke them (`/orchestrator`, etc.)
- If MCP selected: remind to configure credentials in `.mcp.json`
