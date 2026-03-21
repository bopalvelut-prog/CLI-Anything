# NVM CLI-Anything Harness

**Binary**: `nvm`  
**Description**: Node version manager

## Quick Start
```bash
python -m cli_anything.nvm repl
```

## Architecture
- `cli_anything/nvm/core/session.py` — Project session management
- `cli_anything/nvm/core/` — nvm-specific operations
- `cli_anything/nvm/utils/repl_skin.py` — Terminal UI
- `cli_anything/nvm/skills/SKILL.md` — Skill definition
