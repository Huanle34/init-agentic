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

## STEP 2 — Requirement Grilling (no round limit)

**Foundation:** This step uses the `grill-me` approach — interview the user relentlessly,
walking down each branch of the decision tree, resolving dependencies between decisions
one at a time. Ask ONE question per turn. Provide your recommended answer as the first option.
**No artificial round limit. Continue until all open branches are resolved.**

### Stop condition

Stop only when ALL of the following are known:
- What the system does and for whom
- The primary stack / language / framework
- The core problem being solved
- At least 1 key risk or constraint
- Rough scope boundary (what is NOT in v1)
- Commands: run, test, lint (or confirmed "none yet")
- No unresolved dependency remains that would affect agent/tool selection

If even one branch is unresolved and it affects agent/hook/rule recommendations — keep grilling.

### Per-turn process

1. Build a decision tree from everything known so far
2. Find the highest-priority unresolved branch
3. Synthesize 2–3 options tailored to THIS project — put your recommended answer first,
   label it `(Recommended)` in the description
4. Call `AskUserQuestion` (multiSelect: false, one question) — "Other" auto-appears for free text
5. Record the answer; update the decision tree
6. Check stop condition — if not met, go to next branch

Example turn for a vague data pipeline project:
```json
{
  "questions": [{
    "question": "What triggers the pipeline?",
    "header": "Trigger",
    "multiSelect": false,
    "options": [
      {"label": "Scheduled Airflow DAG", "description": "Time-based — daily or hourly cron (Recommended — most common for analytics pipelines)"},
      {"label": "Webhook from upstream system", "description": "Event-driven — HubSpot, Kafka, or similar push"},
      {"label": "Manual run by analyst", "description": "Ad-hoc — no automated trigger in v1"}
    ]
  }]
}
```

### Branch priority order (use your own judgment — this is a guide)

1. Stack / language — if still unknown
2. Primary users — "who runs/uses this daily?"
3. Core output — "what does this produce or deliver?"
4. Trigger / entry point — "what starts the process?"
5. Scope boundary — "what is explicitly NOT in v1?"
6. Key risk — "what is most likely to break or block this?"
7. Commands — run / test / lint (stack-specific options via AskUserQuestion)
8. Any remaining open branch that affects agent/hook/rule selection

### Ending the loop

When stop condition is met, print a spec summary (5–8 bullets) and say:
> EN: "Got it — spec is clear. Moving on to select agents and tools."
> VI: "Đủ rồi — spec đã rõ. Tiếp tục chọn agents và tools."

Do NOT ask "is this correct?" — proceed directly to STEP 3.

---

## STEP 3 — Agents

Use `AskUserQuestion` with **two consecutive calls** (7 agents, max 4 per call).

**Before calling:** Analyze `name`, `description`, and `stack` to determine which agents are most relevant.
Mark recommended agents with `(Recommended)` in their description. Put recommended agents first within each call.

Agent catalog for reference:
- `orchestrator` — High-level task planner; delegates to other agents
- `code-reviewer` — Read-only code quality reviewer; runs before commit
- `qa-tester` — Test runner; verifies features after build
- `documentation` — Doc writer; updates README, docs/, CHANGELOG
- `ba-agent` — Business Analyst; writes specs and business rules (Opus)
- `sql-reviewer` — BigQuery/dbt SQL reviewer; checks dialect and performance
- `data-validator` — Data quality checker; validates pipeline output

**Recommendation heuristics (apply your own reasoning beyond these):**
- Data pipeline / Airflow / dbt → `data-validator`, `sql-reviewer`, `orchestrator` likely needed
- Web app / API → `code-reviewer`, `qa-tester` likely needed
- Early-stage / greenfield → `ba-agent` useful for spec writing
- Any project with multiple agents → `orchestrator` useful

**Call 1** — first 4 agents (reorder to put most relevant first for this project):
Build the options array dynamically with appropriate descriptions and "(Recommended)" markers.

**Call 2** — remaining 3 agents:
Same approach — reorder and annotate based on context.

Merge results from both calls into a single `agents` list.

---

## STEP 4 — MCP Integrations

Use `AskUserQuestion` with **two consecutive calls** (8 MCPs, max 4 per call).

**Before calling:** Infer likely MCPs from `description` and `stack`:
- Mentions "GitHub", "PR", "code review" → recommend GitHub
- Mentions "Jira", "ticket", "sprint", "Confluence" → recommend Atlassian
- Mentions "Notion", "wiki", "docs" → recommend Notion
- Mentions "Slack", "notification", "alert" → recommend Slack
- Mentions "API", "Postman", "endpoint" → recommend Postman
- Mentions "design", "UI", "Figma" → recommend Figma
- Mentions "email", "Gmail" → recommend Gmail
- Mentions "Drive", "spreadsheet", "GSheet" → recommend Google Drive

**Call 1** — 4 MCPs most relevant to this project (put recommended first, add "(Recommended)" to description):
Build the options array dynamically — choose the 4 most likely MCPs for call 1, remaining 4 for call 2.

**Call 2** — remaining 4 MCPs.

Merge results. If nothing selected in either call, `mcps: []`.

---

## STEP 5 — Hooks

Use `AskUserQuestion` tool. Build options dynamically from commands gathered in Step 2:

- `pre-write` → mention actual `lint_cmd` if set, or "(no lint command configured)"
- `post-edit` → mention actual `test_cmd` if set, or "(no test command configured)"
- `session-end` → always available; appends a session marker to `CLAUDE.local.md` on Stop

Four hooks available. Build descriptions dynamically from commands gathered in Step 2:

| Hook | Event | Always offer? | When to recommend |
|------|-------|--------------|-------------------|
| `pre-write` | PreToolUse → Write | Yes | `lint_cmd` is set |
| `post-edit` | PostToolUse → Edit | Yes | `test_cmd` is set |
| `session-end` | Stop | Yes | Always — no command needed |
| `notification` | Notification | Yes | Projects with CI, alerts, or async workflows |

Example (Python + ruff + pytest):
```json
{
  "questions": [{
    "question": "Select hooks to register:",
    "header": "Hooks",
    "multiSelect": true,
    "options": [
      {"label": "pre-write", "description": "Runs `ruff check .` before Claude writes a file (Recommended)"},
      {"label": "post-edit", "description": "Runs `pytest` after Claude edits a file (Recommended)"},
      {"label": "session-end", "description": "Appends session marker to CLAUDE.local.md when Claude stops (Recommended)"},
      {"label": "notification", "description": "Logs all Claude Code notifications to .claude/notifications.log"}
    ]
  }]
}
```

---

## STEP 6 — Skills

Skill catalog (6 skills, 4 per AskUserQuestion call max → use **two consecutive calls**):

| Skill | When most relevant |
|-------|-------------------|
| `build-feature` | New / greenfield project |
| `debug` | Any project — universal |
| `review` | Any project — pre-merge readiness check |
| `write-tests` | Existing code with low coverage; data pipelines |
| `deploy` | Has `run_cmd`, CI/CD, or deployment mentioned |
| `refactor` | Existing codebase, technical debt mentioned |

**Before calling:** use heuristics above to decide which 4 go in Call 1 (most relevant first).

**Call 1** — 4 most relevant skills for this project (put recommended ones first with `(Recommended)`):
```json
{
  "questions": [{
    "question": "Select skills to scaffold (1/2):",
    "header": "Skills 1",
    "multiSelect": true,
    "options": [
      {"label": "build-feature", "description": "<why this matters for THIS project>"},
      {"label": "debug",         "description": "<universal — or skip if only non-code work>"},
      {"label": "review",        "description": "<pre-merge check — recommended for any project with git>"},
      {"label": "write-tests",   "description": "<why this matters for THIS stack>"}
    ]
  }]
}
```

**Call 2** — remaining 2 skills:
```json
{
  "questions": [{
    "question": "Select skills to scaffold (2/2):",
    "header": "Skills 2",
    "multiSelect": true,
    "options": [
      {"label": "deploy",   "description": "<why this matters or skip hint>"},
      {"label": "refactor", "description": "<why this matters or skip hint>"}
    ]
  }]
}
```

Merge results from both calls into a single `skills` list.

---

## STEP 7 — Code Style Rules

Auto-suggest based on stack from Step 2:
- Always suggest: `general`
- If Python in stack: suggest `python`
- If TypeScript/JavaScript/React/Node: suggest `typescript`
- If SQL/dbt/BigQuery/Postgres: suggest `sql`

Before calling AskUserQuestion, tell the user which rules are recommended based on their stack. Then use `AskUserQuestion` tool:

```json
{
  "questions": [{
    "question": "Select code style rules to generate (pick based on your stack):",
    "header": "Rules",
    "multiSelect": true,
    "options": [
      {"label": "general", "description": "Always loaded — applies every session (recommended)"},
      {"label": "python", "description": "Auto-loaded for **/*.py files"},
      {"label": "typescript", "description": "Auto-loaded for **/*.{ts,tsx,js,jsx} files"},
      {"label": "sql", "description": "Auto-loaded for **/*.sql files"}
    ]
  }]
}
```

After user responds, ensure `general` is always included even if not selected.

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

Build the JSON spec from all collected answers, then run the generator script.

### Spec format

Write the spec to `~/.claude/.init_spec.json` (not inside the target project):

```json
{
  "name": "<from Step 1>",
  "description": "<from Step 1>",
  "stack": "<from Step 2>",
  "run_cmd": "<from Step 2, or empty string>",
  "test_cmd": "<from Step 2, or empty string>",
  "lint_cmd": "<from Step 2, or empty string>",
  "agents": ["<selected agent names>"],
  "mcps": ["<selected MCP display names>"],
  "hooks": ["pre-write", "post-edit", "session-end"],
  "skills": ["<selected skill names>"],
  "rules": ["<selected rule keys: general|python|typescript|sql>"],
  "env": {"KEY": "# TODO: set value"},
  "model": "<model ID, or empty string to inherit global>",
  "permission_preset": "<standard|data-safe|strict>",
  "clarification_rounds": [
    {"question": "<question text>", "answer": "<user answer>"}
  ],
  "lang": "<en|vi>"
}
```

### Detect Python command

Before running, detect which Python command is available:

```bash
python --version 2>&1 || python3 --version 2>&1 || py --version 2>&1
```

Use the first one that succeeds: `python`, `python3`, or `py` (Windows Store).

### Run the generator

```bash
# Unix / macOS
python3 ~/.claude/skills/init-agentic/scripts/init_agentic.py \
  --from-spec ~/.claude/.init_spec.json "<target>"

# Windows (PowerShell)
python "$HOME\.claude\skills\init-agentic\scripts\init_agentic.py" `
  --from-spec "$HOME\.claude\.init_spec.json" "<target>"
```

After generation succeeds, delete the spec file:

```bash
rm ~/.claude/.init_spec.json                      # Unix
Remove-Item "$HOME\.claude\.init_spec.json"       # Windows PowerShell
```

### Fallback (if Bash unavailable or Python not found)

Use the Write tool to generate each file directly. For each file:
1. Use the Read tool to load the template from `~/.claude/skills/init-agentic/references/`
2. Replace all placeholders with collected answers
3. Write to the target path

Placeholder map:
- `<PROJECT_NAME>` → project name (Step 1)
- `<DESCRIPTION>` → description (Step 1)
- `<STACK>` → stack (Step 2)
- `<DATE>` → today's date (YYYY-MM-DD)

Files to generate (write only selected items):

| Target path | Template source | Notes |
|-------------|-----------------|-------|
| `CLAUDE.md` | Compose from answers | Use gen_claude_md() structure |
| `CLAUDE.local.md` | `references/docs/claude-local.md` | Replace `<DATE>` |
| `.gitignore` | Create or append | Always add `CLAUDE.local.md` entry |
| `.mcp.json` | Compose from MCP catalog | Only if MCPs selected |
| `.claude/settings.json` | Compose from agents + hooks | See hook registration below |
| `.claude/registry.md` | `references/docs/registry.md` | Replace `<DATE>` |
| `.claude/agents/<name>.md` | `references/agents/<name>.md` | Replace `<PROJECT_NAME>` |
| `.claude/rules/<filename>` | `references/rules/<name>.md` | No substitution needed |
| `.claude/skills/<name>/SKILL.md` | `references/skills/<name>.md` | Replace `<STACK>` |
| `.claude/commands/standup.md` | `references/commands/standup.md` | Always generated |
| `.claude/commands/review.md` | `references/commands/review.md` | Always generated |
| `.claude/commands/run-tests.md` | `references/commands/run-tests.md` | Only if qa-tester selected |
| `.claude/commands/validate.md` | `references/commands/validate.md` | Only if data-validator selected |
| `.claude/commands/sync-docs.md` | `references/commands/sync-docs.md` | Only if documentation selected |
| `.claude/hooks/pre-write.ps1\|.sh` | Compose | Only if pre-write selected |
| `.claude/hooks/post-edit.ps1\|.sh` | Compose | Only if post-edit selected |
| `.claude/hooks/session-end.ps1\|.sh` | Compose | Only if session-end selected |
| `.claude/hooks/notification.ps1\|.sh` | Compose | Only if notification selected |
| `docs/adr/0001-bootstrap.md` | `references/docs/adr-0001.md` | Replace all placeholders |
| `docs/learnings.md` | `references/docs/learnings.md` | Replace `<DATE>` |

**Hooks MUST be registered in `.claude/settings.json`** under the `hooks` key:
- `pre-write` → event `PreToolUse`, matcher `Write`
- `post-edit` → event `PostToolUse`, matcher `Edit`
- `session-end` → event `Stop` (no matcher)
- `notification` → event `Notification` (no matcher)
- Windows command: `powershell -File .claude/hooks/<name>.ps1`
- Unix command: `.claude/hooks/<name>.sh`

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
