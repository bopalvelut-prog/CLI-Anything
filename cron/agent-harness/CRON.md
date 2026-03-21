# CRON CLI-Anything Harness

**Binary**: `crontab`  
**Description**: Cron job scheduling

## Quick Start
```bash
python -m cli_anything.cron repl
```

## Architecture
- `cli_anything/cron/core/session.py` — Project session management
- `cli_anything/cron/core/` — cron-specific operations
- `cli_anything/cron/utils/repl_skin.py` — Terminal UI
- `cli_anything/cron/skills/SKILL.md` — Skill definition
