# Contributing to CLI-Anything

## Adding a New Harness

### 1. Use the template

```bash
cli-anything new myapp --binary myapp-binary
```

This creates a harness scaffold at `~/.config/cli-anything/harnesses/myapp/`.

### 2. Harness structure

```
myapp/agent-harness/
├── setup.py                          # Package metadata
├── MYAPP.md                          # Architecture SOP
└── cli_anything/myapp/
    ├── __init__.py
    ├── __main__.py                   # Entry point
    ├── myapp_cli.py                  # Main CLI (Click + REPL)
    ├── README.md
    ├── core/
    │   ├── __init__.py
    │   ├── session.py                # Shared session (undo/redo)
    │   └── operations.py             # App-specific operations
    ├── utils/
    │   ├── __init__.py
    │   └── repl_skin.py              # REPL styling
    ├── skills/SKILL.md               # Agent skill description
    └── tests/
        ├── __init__.py
        └── test_core.py              # Unit tests
```

### 3. What makes a good harness?

A harness should provide **value beyond the native CLI**:

| Criteria | Good | Bad |
|----------|------|-----|
| Has native CLI? | GUI app with no CLI (GIMP, Blender) | Already has great CLI (ffmpeg, curl) |
| JSON output? | Native CLI has no JSON | Native CLI already has `--json` |
| Multi-step workflow? | GUI workflow → CLI pipeline | Single command |
| Agent-friendly? | Structured, predictable | Unstructured text output |

### 4. Checklist

- [ ] `setup.py` with correct metadata
- [ ] Click commands with `--json` flag
- [ ] REPL mode with tab completion
- [ ] `handle_error` decorator with `functools.wraps`
- [ ] Input validation (no f-string injection)
- [ ] Unit tests (5+ tests)
- [ ] E2E tests for core operations
- [ ] SKILL.md with agent description
- [ ] README.md with examples

### 5. Submit

```bash
git add myapp/agent-harness/
git commit -m "Add myapp CLI harness"
git push origin feat/myapp
# Open PR
```

## Code Style

- Python 3.10+
- Click for CLI
- prompt-toolkit for REPL
- `functools.wraps` on decorators
- No f-string injection (validate all user input)
- JSON output mode for all commands

## Testing

```bash
pip install pytest
pytest cli_anything/myapp/tests/ -v
```
