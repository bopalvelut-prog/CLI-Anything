# SCREEN CLI-Anything Harness

**Binary**: `screen`  
**Description**: Terminal multiplexer

## Quick Start
```bash
python -m cli_anything.screen repl
```

## Architecture
- `cli_anything/screen/core/session.py` — Project session management
- `cli_anything/screen/core/` — screen-specific operations
- `cli_anything/screen/utils/repl_skin.py` — Terminal UI
- `cli_anything/screen/skills/SKILL.md` — Skill definition
