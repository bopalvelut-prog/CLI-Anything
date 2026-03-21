# PS CLI-Anything Harness

**Binary**: `ps`  
**Description**: Process status

## Quick Start
```bash
python -m cli_anything.ps repl
```

## Architecture
- `cli_anything/ps/core/session.py` — Project session management
- `cli_anything/ps/core/` — ps-specific operations
- `cli_anything/ps/utils/repl_skin.py` — Terminal UI
- `cli_anything/ps/skills/SKILL.md` — Skill definition
