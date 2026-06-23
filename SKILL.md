---
name: init-agentic
description: >
  Bootstrap a complete Claude Code agentic project structure interactively.
  Trigger: "init project", "bootstrap agents", "setup claude", "init agentic",
  "grill me on this project", "stress-test my plan", "scaffold agentic setup",
  "khởi tạo project", "tạo project mới", "bootstrap project".
version: "3.1.0"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Init Agentic v3.1 — Interactive Wizard

You are running the Init Agentic wizard. Follow EVERY step in order.
Do NOT skip steps. Do NOT generate files before completing all steps.

---

## STEP 0 — Language Selection (ALWAYS FIRST, no exceptions)

Before doing ANYTHING else, ask the user exactly this:

```
Select language / Chọn ngôn ngữ:

1. English
2. Tiếng Việt
```

Wait for their response. Store the choice as `lang`.
Use the chosen language for ALL subsequent questions, labels, and messages.

---

## STEP 1 — Project Info

Ask (in the chosen language):
- **Project name** — default: current working directory name
- **Short description** — 1-2 sentences about the goal

EN prompts: "Project name", "Short description (1-2 sentences about the goal)"
VI prompts: "Tên project", "Mô tả ngắn (1-2 câu về mục tiêu)"

---

## STEP 2 — Tech Stack

Ask (in the chosen language):
- Primary language / framework (default: Python)
- Run / start command (optional)
- Test command (optional)
- Lint command (optional)

EN prompts: "Primary language / framework", "Run / start command", "Test command", "Lint command"
VI prompts: "Ngôn ngữ / framework chính", "Lệnh chạy", "Lệnh test", "Lệnh lint"

---

## STEP 3 — Agents

Show ALL 7 agents as a numbered list. No pre-selection. User picks freely.

Available agents:
1. `orchestrator` — High-level task planner; delegates to other agents
2. `code-reviewer` — Read-only code quality reviewer; runs before commit
3. `qa-tester` — Test runner; verifies features after build
4. `documentation` — Doc writer; updates README, docs/, CHANGELOG
5. `ba-agent` — Business Analyst; writes specs and business rules (Opus)
6. `sql-reviewer` — BigQuery/dbt SQL reviewer; checks dialect and performance
7. `data-validator` — Data quality checker; validates pipeline output

EN prompt: "Select agents for this project (enter numbers, e.g. 1,3,5)"
VI prompt: "Chọn agents cho project này (nhập số, vd 1,3,5)"

---

## STEP 4 — MCP Integrations

Show the list, no pre-selection. User picks or skips.

Available MCPs: GitHub, Notion, Atlassian, Google Drive, Gmail, Slack, Postman, Figma

EN prompt: "Select MCP servers to connect (or Enter to skip)"
VI prompt: "Chọn MCP servers cần kết nối (hoặc Enter để bỏ qua)"

---

## STEP 5 — Hooks

Show both options, both pre-selected as default (user can deselect):

1. pre-write — runs lint before Claude writes a file
2. post-edit — runs test after Claude edits a file

EN prompt: "Select hooks to enable"
VI prompt: "Chọn hooks muốn bật"

---

## STEP 6 — Skills

Show 4 options, none pre-selected:

1. build-feature — implement a new feature end-to-end
2. deploy — deploy to staging or production
3. debug — systematic debugging workflow
4. refactor — improve code quality without changing behavior

EN prompt: "Select skill templates to generate"
VI prompt: "Chọn skill templates cần tạo"

---

## STEP 7 — Code Style Rules

Show 4 rule options. Auto-suggest based on stack detected in Step 2:
- Always suggest: `general`
- If Python in stack: suggest `python`
- If TypeScript/JavaScript/React/Node: suggest `typescript`
- If SQL/dbt/BigQuery/Postgres: suggest `sql`

1. general — no path filter, loads every session
2. python — paths: `**/*.py`
3. typescript — paths: `**/*.{ts,tsx,js,jsx}`
4. sql — paths: `**/*.sql`

EN prompt: "Select code style rule files to generate"
VI prompt: "Chọn rule files cần tạo"

---

## STEP 8 — Summary & Confirm

Print a summary of all selections. Example:

```
Project  : MyProject
Stack    : Python + dbt
Agents   : orchestrator, ba-agent, sql-reviewer, data-validator
MCPs     : none
Hooks    : pre-write, post-edit
Skills   : build-feature
Rules    : general, python, sql
```

Ask: EN: "Proceed with file generation? (y/n)" | VI: "Tiến hành tạo files? (y/n)"

---

## STEP 9 — Grilling Mode (optional)

Ask: EN: "Enable Grilling Mode — stress-test the plan? (y/n)" | VI: "Bật Grilling Mode? (y/n)"

If yes, ask these questions ONE AT A TIME. Show the recommended answer after each question.
Wait for the user to answer before moving to the next.

**Goals & Scope**
1. What core problem does this project solve? (Recommendation: 1 sentence — '[User X] cannot [do Y] without [Z]')
2. What does success look like after 30 days? A specific number? (Recommendation: 1 North Star metric only)
3. What is explicitly NOT in scope for v1? (Recommendation: list at least 3 things cut)

**Users**
4. Who is the first user — a specific person, not 'everyone'? (Recommendation: name one real person with role and context)
5. How does that user do this workflow today, without this tool? (Recommendation: walk through each step — biggest time sink = build first)

**Architecture**
6. What are the core entities and how do they relate? (Recommendation: 3-5 entities with relationship types)
7. Where is system state stored — who reads, who writes? (Recommendation: name the DB, cache layer, and source of truth)
8. What external services are needed — and if they go down? (Recommendation: fallback plan per dependency)

**Risks**
9. What could make this project fail completely in 3 months? (Recommendation: prove the highest-risk assumption first)
10. Which technical part is unknown — needs a spike? (Recommendation: build the smallest spike before business logic)

**Agentic Design**
11. Does each agent have clear scope — what does each NOT do? (Recommendation: one responsibility per agent; know when to refuse)
12. Where is human approval required — what can't agents decide? (Recommendation: before prod deploy, data deletion, external comms)

---

## STEP 10 — Generate Files

### Option A — Python script (preferred when Bash is available)

```bash
python3 ~/.claude/skills/init-agentic/scripts/init_agentic.py
```

The script handles all file generation, hook registration, and Portfolio Registry update automatically.

### Option B — Write tool directly (when Bash is unavailable or non-interactive)

Use the Read tool to load each template from `~/.claude/skills/init-agentic/references/`, then write the file with placeholders replaced by collected answers.

**Placeholder substitution rules:**
- `<PROJECT_NAME>` → project name from Step 1
- `<DESCRIPTION>` → short description from Step 1
- `<STACK>` → primary stack from Step 2
- `<DATE>` → today's date (YYYY-MM-DD)

**File structure to generate:**

```
CLAUDE.md                          ← compose from answers (see template below)
CLAUDE.local.md                    ← Read references/docs/claude-local.md, replace <DATE>
.mcp.json                          ← only if MCPs selected (see MCP catalog in script)
.claude/settings.json              ← compose from agents + hooks (see critical note below)
.claude/registry.md                ← Read references/docs/registry.md, replace <DATE>
.claude/agents/<name>.md           ← Read references/agents/<name>.md, replace <PROJECT_NAME>
.claude/rules/<filename>           ← Read references/rules/<name>.md (no substitution needed)
.claude/skills/<name>/SKILL.md     ← Read references/skills/<name>.md, replace <STACK>
.claude/hooks/pre-write.ps1|.sh    ← only if pre-write hook selected
.claude/hooks/post-edit.ps1|.sh    ← only if post-edit hook selected
docs/adr/0001-bootstrap.md         ← Read references/docs/adr-0001.md, replace all placeholders
docs/learnings.md                  ← Read references/docs/learnings.md, replace <DATE>
```

**Agent files** (in `references/agents/`):
- `orchestrator.md`, `code-reviewer.md`, `qa-tester.md`, `documentation.md`
- `ba-agent.md`, `sql-reviewer.md`, `data-validator.md`

Write only the agents the user selected. Replace `<PROJECT_NAME>` in each file.

**Rule files** (in `references/rules/`):
- `general.md` → `.claude/rules/general.md`
- `python-style.md` → `.claude/rules/python-style.md`
- `typescript-style.md` → `.claude/rules/typescript-style.md`
- `sql-style.md` → `.claude/rules/sql-style.md`

Write only the rules the user selected. No placeholder substitution needed.

**Skill files** (in `references/skills/`):
- `build-feature.md`, `deploy.md`, `debug.md`, `refactor.md`

Write only the skills the user selected. Replace `<STACK>` with the project stack.

**CLAUDE.md** — compose directly from collected answers (not a template file):

```markdown
# <PROJECT_NAME>

## Goal
<DESCRIPTION>

---

## Stack
<STACK>

## Commands

```bash
# Run / start
<RUN_CMD or # TODO: add run command>

# Test
<TEST_CMD or # TODO: add test command>

# Lint
<LINT_CMD or # TODO: add lint command>
```

## Agents

<list each selected agent as: - `@agent-<name>` -- <first sentence of its description>>

Invoke any agent with `@agent-<name>` in Claude Code.

## MCP Integrations

<list selected MCPs, or - (none configured)>

## Rules

<list selected rule files with their path filter>

Rules without a `paths:` filter load every session.
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
*Generated by init-agentic skill -- <DATE>*
```

**`.claude/settings.json`** — compose from agents and hooks selections:

```json
{
  "permissions": { "allow": ["Bash", "Read", "Write", "Edit"], "deny": [] },
  "enabledPlugins": [],
  "agentSettings": { "<agent-name>": { "enabled": true }, ... },
  "hooks": {
    "PreToolUse": [{ "matcher": "Write", "hooks": [{ "type": "command", "command": "<pre-write-cmd>" }] }],
    "PostToolUse": [{ "matcher": "Edit", "hooks": [{ "type": "command", "command": "<post-edit-cmd>" }] }]
  }
}
```

- Windows hook commands: `powershell -File .claude/hooks/pre-write.ps1` / `powershell -File .claude/hooks/post-edit.ps1`
- Unix hook commands: `.claude/hooks/pre-write.sh` / `.claude/hooks/post-edit.sh`
- Omit the `hooks` key entirely if no hooks were selected.

**Critical: hooks MUST be registered in `.claude/settings.json`** under the `hooks` key:
- `pre-write` → `PreToolUse` event, matcher `Write`
- `post-edit` → `PostToolUse` event, matcher `Edit`

---

## STEP 11 — Portfolio Registry Update

After generating files, update `~/.claude/CLAUDE.md` Portfolio Registry table:
- Find the `## Portfolio Registry` section
- Replace the placeholder row OR insert a new row after the separator:
  `| <project-name> | Active | | <project-path> |`

---

## STEP 12 — Summary

Print a final summary in the chosen language:
- List generated files
- Confirm Portfolio Registry was updated (or show manual row if not)
- Next steps: add CLAUDE.local.md to .gitignore, fill in TODO commands, open Claude Code
