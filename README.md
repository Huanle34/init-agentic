# init-agentic — Claude Code Skill

Bootstrap a complete Claude Code agentic project structure in minutes,
aligned with official Claude Code conventions.

---

## Installation

### Option A — Clone (recommended)

```bash
# macOS / Linux
git clone https://github.com/Huanle34/init-agentic ~/.claude/skills/init-agentic

# Windows (PowerShell)
git clone https://github.com/Huanle34/init-agentic "$env:USERPROFILE\.claude\skills\init-agentic"
```

### Option B — Manual copy

```bash
cp -r init-agentic ~/.claude/skills/
```

### Option C — Run script directly (no install)

```bash
python3 init-agentic/scripts/init_agentic.py [target-directory]
```

---

## Usage in Claude Code

After installing, open Claude Code (`claude`) and say:

```
/init-agentic
```

Or any of: `init project`, `bootstrap agents`, `setup claude`, `init agentic`,
`khởi tạo project`, `tạo project mới`

Claude will run a step-by-step wizard — select language first, then fill in
project info, pick agents, MCPs, hooks, skills, and rules.

---

## Run directly from terminal

```bash
# Bootstrap current directory
python3 ~/.claude/skills/init-agentic/scripts/init_agentic.py

# Bootstrap a specific directory
python3 ~/.claude/skills/init-agentic/scripts/init_agentic.py /path/to/project
```

**Windows (PowerShell):**

```powershell
python "$HOME\.claude\skills\init-agentic\scripts\init_agentic.py"
```

---

## Features

### Bilingual wizard (EN / VI)
The first question selects your language. All subsequent prompts, labels,
and messages follow that choice.

### 7 agents to choose from
No defaults — you pick freely from:

| Agent | Model | Role |
|-------|-------|------|
| `orchestrator` | Opus | High-level task planner; delegates to other agents |
| `code-reviewer` | Sonnet | Read-only code quality reviewer; runs before commit |
| `qa-tester` | Sonnet | Test runner; verifies features after build |
| `documentation` | Sonnet | Doc writer; updates README, docs/, CHANGELOG |
| `ba-agent` | Opus | Business Analyst; writes specs and business rules |
| `sql-reviewer` | Sonnet | BigQuery/dbt SQL reviewer; checks dialect and performance |
| `data-validator` | Sonnet | Data quality checker; validates pipeline output |

### Grilling Mode
Optional stress-test phase with 12 project-scoped questions covering:
Goals & Scope, Users, Architecture, Risks, and Agentic Design.
Recommendations are generated from your project name, description, and stack —
type `1` to accept, or enter your own answer.

### MCP integrations
GitHub, Notion, Atlassian, Google Drive, Gmail, Slack, Postman, Figma.

### Hooks (registered in `settings.json`)
- `pre-write` — runs lint before Claude writes a file
- `post-edit` — runs tests after Claude edits a file

### Code style rules
Path-filtered rules auto-loaded by Claude Code:
- `general` — always loaded
- `python` — `**/*.py`
- `typescript` — `**/*.{ts,tsx,js,jsx}`
- `sql` — `**/*.sql`

### Portfolio Registry
After bootstrapping, automatically adds the new project to the
`## Portfolio Registry` table in `~/.claude/CLAUDE.md`.

---

## What gets generated

```
your-project/
├── CLAUDE.md                          <- project context (commit this)
├── CLAUDE.local.md                    <- personal session notes (gitignore this)
├── .mcp.json                          <- MCP server config (if any selected)
├── .claude/
│   ├── settings.json                  <- permissions + hook registrations
│   ├── registry.md                    <- agent task registry
│   ├── agents/                        <- one file per selected agent
│   ├── rules/                         <- code style rules (auto-loaded by file type)
│   ├── skills/                        <- one SKILL.md per selected skill
│   └── hooks/
│       ├── pre-write.sh | .ps1
│       └── post-edit.sh | .ps1
└── docs/
    ├── adr/
    │   └── 0001-bootstrap.md          <- architectural decision record
    └── learnings.md                   <- lessons log
```

**Add `CLAUDE.local.md` to your `.gitignore`.**

---

## Alignment with official Claude Code conventions

| Feature | Convention |
|---------|-----------|
| `CLAUDE.local.md` | Official gitignored personal notes file |
| `.claude/rules/` | Official path-filtered coding rules |
| Agent `description` field | Specific routing text for auto-delegation |
| Hooks in `settings.json` | Correct — harness reads hooks from settings, not by scanning `.claude/hooks/` |
| `docs/adr/` | Standard ADR pattern for architectural decisions |
| `.mcp.json` at project root | Official MCP config location |
| No `user-invocable` field | Deprecated field; omitted |

---

## Requirements

- Python 3.7+
- Claude Code CLI (`claude`)
- No external libraries required

---

## Customization

Edit `scripts/init_agentic.py` to extend:

| Dict / function | What to add |
|-----------------|------------|
| `AGENT_TEMPLATES` | New agent roles |
| `MCP_CATALOG` | Additional MCP servers |
| `RULES_TEMPLATES` | New language rule sets |
| `make_grilling_tree()` | Customize grilling questions |
| `skill_descriptions` in `generate_files()` | New skill types |
