# STRACE CLI-Anything Harness

**Binary**: `strace`  
**Description**: Trace execution syscalls

## Quick Start
```bash
python -m cli_anything.strace repl
```

## Architecture
- `cli_anything/strace/core/session.py` — Project session management
- `cli_anything/strace/core/` — strace-specific operations
- `cli_anything/strace/utils/repl_skin.py` — Terminal UI
- `cli_anything/strace/skills/SKILL.md` — Skill definition
