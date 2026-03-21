# GALAXY CLI-Anything Harness

**Binary**: `ansible-galaxy`  
**Description**: Ansible Galaxy roles

## Quick Start
```bash
python -m cli_anything.galaxy repl
```

## Architecture
- `cli_anything/galaxy/core/session.py` — Project session management
- `cli_anything/galaxy/core/` — galaxy-specific operations
- `cli_anything/galaxy/utils/repl_skin.py` — Terminal UI
- `cli_anything/galaxy/skills/SKILL.md` — Skill definition
