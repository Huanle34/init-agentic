# init-agentic — Claude Code Skill

Bootstrap a complete Claude Code agentic project structure in minutes,
aligned with official Claude Code conventions.

## Installation

### Option A — User scope (available in all projects)

```bash
cp -r init-agentic ~/.claude/skills/
```

### Option B — Project scope (current project only)

```bash
cp -r init-agentic .claude/skills/
```

### Option C — Run directly (no install required)

```bash
python3 init-agentic/scripts/init_agentic.py [target-directory]
```

---

## Usage in Claude Code

After installing, open Claude Code (`claude`) and say:

```
/init-agentic
```

or any of: `init project`, `bootstrap agents`, `setup claude agentic`

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

## What gets generated

```
your-project/
├── CLAUDE.md                          <- project context + goal (commit this)
├── CLAUDE.local.md                    <- personal session notes (gitignore this)
├── .mcp.json                          <- MCP server config (if any selected)
├── .claude/
│   ├── settings.json                  <- permissions + hook event registrations
│   ├── registry.md                    <- agent task registry
│   ├── agents/
│   │   ├── orchestrator.md
│   │   ├── code-reviewer.md
│   │   ├── qa-tester.md
│   │   └── documentation.md
│   ├── rules/                         <- NEW: auto-loaded code style rules
│   │   ├── general.md                 <- no paths filter, always loaded
│   │   ├── python-style.md            <- paths: **/*.py
│   │   ├── typescript-style.md        <- paths: **/*.{ts,tsx,js,jsx}
│   │   └── sql-style.md               <- paths: **/*.sql
│   ├── skills/
│   │   └── build-feature/
│   │       └── SKILL.md
│   └── hooks/
│       ├── pre-write.sh   (Unix) | pre-write.ps1   (Windows)
│       └── post-edit.sh   (Unix) | post-edit.ps1   (Windows)
└── docs/
    ├── adr/
    │   └── 0001-bootstrap.md          <- architectural decision record
    └── learnings.md                   <- lessons log
```

**Note:** Add `CLAUDE.local.md` to your `.gitignore`.

---

## Alignment with official Claude Code conventions

| Feature | Convention followed |
|---------|-------------------|
| `CLAUDE.local.md` | Official gitignored personal notes file |
| `.claude/rules/` | Official path-filtered coding rules |
| Agent `description` field | Specific routing text for auto-delegation |
| Hooks registered in `settings.json` | Correct — harness reads hooks from settings, not by scanning `.claude/hooks/` |
| `docs/adr/` | Standard ADR pattern for architectural decisions |
| `.mcp.json` at project root | Official location |
| No `user-invocable` field | Field is deprecated; omitted |
| Auto memory via `/memory` | Referenced in CLAUDE.md, not replaced by custom files |

---

## Requirements

- Python 3.7+
- Claude Code CLI (`claude`)
- No external libraries required

---

## Customization

Edit `scripts/init_agentic.py` to extend:

| Dict | What to add |
|------|------------|
| `AGENT_TEMPLATES` | New agent roles |
| `MCP_CATALOG` | Additional MCP servers |
| `RULES_TEMPLATES` | New language rule sets |
| `skill_descriptions` in `generate_files()` | New skill types |
| `gen_claude_md()` | Change CLAUDE.md structure |
