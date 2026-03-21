# CLI-Anything: Give Your AI Agent Hands

Turn any software into an AI-controllable tool. No plugins, no APIs, no modifications to the original software.

```bash
pip install cli-anything
cli-anything install gimp blender inkscape
```

## What is CLI-Anything?

CLI-Anything wraps GUI and CLI software into structured, agent-friendly harnesses with:

- **JSON output** — Machine-readable responses for AI agents
- **REPL mode** — Interactive session with tab completion
- **Stateful projects** — Undo/redo history
- **Structured commands** — Predictable, documented API

## Quick Start

### Install everything

```bash
pip install cli-anything
cli-anything install recommended
```

### Use with Claude Code

```
/cli-anything ./path-to-software
```

### Use with LangChain

```python
from cli_anything.adapters.langchain import CLITool

tool = CLITool("gimp")
result = tool.run("convert input.png output.jpg --quality 90")
```

### Use with MCP (Claude Desktop)

```json
{
  "mcpServers": {
    "cli-anything": {
      "command": "python",
      "args": ["-m", "cli_anything.adapters.mcp_server", "--apps", "gimp,blender"]
    }
  }
}
```

## Harnesses

{{ harness_table }}

## Categories

| Category | Examples |
|----------|----------|
| Creative | GIMP, Blender, Inkscape, Krita, Darktable |
| Media | VLC, FFmpeg, FFprobe, yt-dlp, SoX |
| DevOps | Docker, Terraform, Ansible, Kubernetes |
| Security | Ghidra, Nmap, GPG, OpenSSL |
| CAD | FreeCAD, OpenSCAD, KiCad |
| Databases | PostgreSQL, MySQL, MongoDB, Redis |
| Build | CMake, Make, Cargo, Go, Maven |
| Cloud | AWS, GCloud, Azure, Heroku |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add new harnesses.
