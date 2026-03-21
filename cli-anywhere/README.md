# CLI-Anything

Turn any software into an AI-controllable tool. No plugins, no APIs, no modifications.

[![PyPI](https://img.shields.io/pypi/v/cli-anything)](https://pypi.org/project/cli-anything/)
[![License](https://img.shields.io/github/license/HKUDS/CLI-Anything)](LICENSE)

## Install

```bash
pip install cli-anything
cli-anything install recommended
```

## What it does

CLI-Anything wraps GUI and CLI software into structured, agent-friendly harnesses:

- **JSON output** — Machine-readable responses for AI agents
- **REPL mode** — Interactive session with tab completion
- **Stateful projects** — Undo/redo history
- **645+ harnesses** — Creative, DevOps, Security, CAD, Media, and more

## Quick Start

```bash
# Install harnesses
cli-anything install gimp blender inkscape

# Use with Claude Code
/cli-anything ./path-to-software

# Use with LangChain
from cli_anything.adapters.langchain import CLITool
tool = CLITool("gimp")
result = tool.run("convert input.png output.jpg --quality 90")

# Use with MCP (Claude Desktop)
python -m cli_anything.adapters.mcp_server --apps gimp,blender
```

## Categories

| Category | Harnesses |
|----------|-----------|
| Creative | GIMP, Blender, Inkscape, Krita, Darktable |
| Media | VLC, FFmpeg, FFprobe, yt-dlp, SoX |
| DevOps | Docker, Terraform, Ansible, Kubernetes |
| Security | Ghidra, Nmap, GPG, OpenSSL |
| CAD | FreeCAD, OpenSCAD, KiCad |
| Databases | PostgreSQL, MySQL, MongoDB, Redis |
| Build | CMake, Make, Cargo, Go, Maven |
| Cloud | AWS, GCloud, Azure, Heroku |

## Documentation

Full docs at [cli-anything.dev](https://cli-anything.dev)

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md)
