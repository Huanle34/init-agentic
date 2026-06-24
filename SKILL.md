---
name: init-agentic
description: >
  Bootstrap a complete Claude Code agentic project structure interactively.
  Trigger: "init project", "bootstrap agents", "setup claude", "init agentic",
  "grill me on this project", "stress-test my plan", "scaffold agentic setup",
  "khởi tạo project", "tạo project mới", "bootstrap project".
version: "3.4.0"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - AskUserQuestion
---

# Init Agentic v3.4 — Claude-driven Wizard

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

## STEP 2 — Iterative Requirement Clarification

This step replaces the old rigid stack questions and the optional grilling at the end.
**Goal: reach a clear enough spec to generate meaningful files.**

### How it works

Analyze everything from STEP 1. Identify the most important gap — the single thing that,
if answered, would most clarify the project. Ask it. Repeat until the spec is clear.

**You decide when the spec is clear enough.** Stop when you know:
- What the system does and for whom
- The primary stack / language / framework
- The core problem being solved
- At least 1 risk or constraint
- Rough scope boundary (what is NOT in v1)

Typically 3–6 rounds. Stop earlier if the STEP 1 answer was already detailed.

### Per-round process

Each round:
1. Identify the single most important gap remaining
2. Synthesize 2–3 specific answer options tailored to this project (not generic)
3. Call `AskUserQuestion` (multiSelect: false) — auto-adds "Other" for free text input
4. Record the answer, update your internal spec model
5. Decide: spec clear enough? If yes → exit loop. If no → next round.

Example round for a vague data pipeline project:
```json
{
  "questions": [{
    "question": "[2/?] What triggers the pipeline?",
    "header": "Clarify 2",
    "multiSelect": false,
    "options": [
      {"label": "Scheduled Airflow DAG (daily/hourly)", "description": "Time-based, no human action needed"},
      {"label": "Webhook from upstream system (e.g. HubSpot)", "description": "Event-driven trigger"},
      {"label": "Manual run by analyst", "description": "Ad-hoc, human-initiated"}
    ]
  }]
}
```

### Gap priority order (use your own reasoning, this is a guide)

1. Stack / language — if still unknown
2. Primary users — "who runs/uses this daily?"
3. Core output — "what does this produce or deliver?"
4. Scope boundary — "what is NOT in v1?"
5. Key risk — "what is most likely to break this?"
6. Commands — run / test / lint (stack-specific options via AskUserQuestion)
7. Anything else still ambiguous

### Ending the loop

When spec is clear, print a brief spec summary (5–8 bullet points) and say:
> "Got enough context — moving on to select agents and tools."

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

Use `AskUserQuestion` tool. Tailor the description based on what the user actually configured:

- If `lint_cmd` is set → `pre-write` description should mention the actual lint command
- If `test_cmd` is set → `post-edit` description should mention the actual test command
- If a command is empty → note "(no command set — you can add it later in settings.json)"

Example (Python + ruff + pytest):
```json
{
  "questions": [{
    "question": "Select hooks to register:",
    "header": "Hooks",
    "multiSelect": true,
    "options": [
      {"label": "pre-write", "description": "Runs `ruff check .` before Claude writes a file (Recommended)"},
      {"label": "post-edit", "description": "Runs `pytest` after Claude edits a file (Recommended)"}
    ]
  }]
}
```

Build the actual options dynamically based on the commands from Step 2.

---

## STEP 6 — Skills

Use `AskUserQuestion` tool. Infer which skills matter most for this project:

- New / greenfield project → `build-feature` is almost always useful
- Has `run_cmd` or CI/CD mentioned → `deploy` relevant
- Existing codebase / refactor mentioned in description → `refactor`, `debug`
- Any project → `debug` is universally useful

Build description dynamically — add context like "useful for your Airflow pipeline" or "(Recommended for new projects)":

```json
{
  "questions": [{
    "question": "Select skills to scaffold:",
    "header": "Skills",
    "multiSelect": true,
    "options": [
      {"label": "build-feature", "description": "<why this matters for THIS project>"},
      {"label": "deploy", "description": "<why this matters or skip hint>"},
      {"label": "debug", "description": "<why this matters for THIS stack>"},
      {"label": "refactor", "description": "<why this matters or skip hint>"}
    ]
  }]
}
```

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

## STEP 8 — Summary & Confirm

Print a clean summary of all selections. Example:

```
Project  : MyProject
Stack    : Python + dbt
Agents   : orchestrator, ba-agent, sql-reviewer, data-validator
MCPs     : none
Hooks    : pre-write, post-edit
Skills   : build-feature
Rules    : general, python, sql
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
  "hooks": ["pre-write", "post-edit"],
  "skills": ["<selected skill names>"],
  "rules": ["<selected rule keys: general|python|typescript|sql>"],
  "grilling_decisions": [
    {
      "branch": "<Goals & Scope|Users|Architecture|Risks|Agentic Design>",
      "question": "<question text>",
      "recommendation": "<your synthesized recommendation>",
      "answer": "<user answer or recommendation text>"
    }
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
| `.mcp.json` | Compose from MCP catalog | Only if MCPs selected |
| `.claude/settings.json` | Compose from agents + hooks | See hook registration below |
| `.claude/registry.md` | `references/docs/registry.md` | Replace `<DATE>` |
| `.claude/agents/<name>.md` | `references/agents/<name>.md` | Replace `<PROJECT_NAME>` |
| `.claude/rules/<filename>` | `references/rules/<name>.md` | No substitution needed |
| `.claude/skills/<name>/SKILL.md` | `references/skills/<name>.md` | Replace `<STACK>` |
| `.claude/hooks/pre-write.ps1\|.sh` | Compose | Only if pre-write selected |
| `.claude/hooks/post-edit.ps1\|.sh` | Compose | Only if post-edit selected |
| `docs/adr/0001-bootstrap.md` | `references/docs/adr-0001.md` | Replace all placeholders |
| `docs/learnings.md` | `references/docs/learnings.md` | Replace `<DATE>` |

**Hooks MUST be registered in `.claude/settings.json`** under the `hooks` key:
- `pre-write` → event `PreToolUse`, matcher `Write`
- `post-edit` → event `PostToolUse`, matcher `Edit`
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

Print a final summary in the chosen language:
- List generated files
- Confirm Portfolio Registry was updated (or show manual row if not)
- Next steps: add CLAUDE.local.md to .gitignore, fill in TODO commands, open Claude Code
