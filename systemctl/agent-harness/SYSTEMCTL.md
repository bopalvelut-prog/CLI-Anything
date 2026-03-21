# SYSTEMCTL CLI-Anything Harness

**Binary**: `systemctl`  
**Description**: Systemd service control

## Quick Start
```bash
python -m cli_anything.systemctl repl
```

## Architecture
- `cli_anything/systemctl/core/session.py` — Project session management
- `cli_anything/systemctl/core/` — systemctl-specific operations
- `cli_anything/systemctl/utils/repl_skin.py` — Terminal UI
- `cli_anything/systemctl/skills/SKILL.md` — Skill definition
