# LSOF CLI-Anything Harness

**Binary**: `lsof`  
**Description**: List open files

## Quick Start
```bash
python -m cli_anything.lsof repl
```

## Architecture
- `cli_anything/lsof/core/session.py` — Project session management
- `cli_anything/lsof/core/` — lsof-specific operations
- `cli_anything/lsof/utils/repl_skin.py` — Terminal UI
- `cli_anything/lsof/skills/SKILL.md` — Skill definition
