# SED CLI-Anything Harness

**Binary**: `sed`  
**Description**: Stream editor

## Quick Start
```bash
python -m cli_anything.sed repl
```

## Architecture
- `cli_anything/sed/core/session.py` — Project session management
- `cli_anything/sed/core/` — sed-specific operations
- `cli_anything/sed/utils/repl_skin.py` — Terminal UI
- `cli_anything/sed/skills/SKILL.md` — Skill definition
