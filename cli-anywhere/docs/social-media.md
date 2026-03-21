# Social Media Posts

## Twitter/X Thread

### Tweet 1 (Hook)
```
I gave my AI agent hands. 🤖✋

It can now control GIMP, Blender, FreeCAD, VLC, and 645 other apps — with JSON output, undo/redo, and structured commands.

No plugins. No APIs. No modifications.

pip install cli-anything
```

### Tweet 2 (Demo)
```
Watch what happens:

User: "Create a bracket with a hole, export as STEP for manufacturing"

Agent:
→ cli-anything-freecad doc new --name Bracket
→ cli-anything-freecad shape box --length 40 --width 20 --height 5  
→ cli-anything-freecad shape cylinder --radius 3 --height 6
→ cli-anything-freecad boolean cut Box Cylinder
→ cli-anything-freecad export to bracket.step

Done. A CAD file from a text prompt. 🏭
```

### Tweet 3 (How it works)
```
The trick: we wrap GUI software with headless CLI harnesses.

Each harness provides:
• JSON output for agents
• REPL with tab completion
• Stateful undo/redo
• Structured commands

GIMP runs headless via gimp-console
Blender runs headless via blender -b
FreeCAD runs headless via freecadcmd
```

### Tweet 4 (Scale)
```
Currently covering:
✅ Creative: GIMP, Blender, Inkscape, Krita
✅ Media: VLC, FFmpeg, yt-dlp, SoX
✅ DevOps: Docker, Terraform, Ansible
✅ Security: Ghidra, Nmap, GPG
✅ CAD: FreeCAD, KiCad, OpenSCAD

GitHub: github.com/HKUDS/CLI-Anything
```

### Tweet 5 (CTA)
```
Want to contribute?

1. Pick any GUI app without a CLI
2. `cli-anything new myapp --binary myapp`
3. Fill in the commands
4. Submit PR

We need harnesses for: DaVinci Resolve, Figma, Ableton, AutoCAD, Photoshop...

github.com/HKUDS/CLI-Anything
```

---

## Reddit r/commandline Post

**Title:** CLI-Anything: Turn any GUI software into an AI-controllable CLI tool

**Body:**
I've been working on a project that wraps GUI software into structured CLI harnesses for AI agent consumption.

The idea is simple: most powerful software (GIMP, Blender, FreeCAD, VLC) only has GUIs. AI agents can't use GUIs. So we wrap them with headless CLI interfaces that output JSON.

Each harness provides:
- Structured commands (no magic strings)
- JSON output mode (`--json` flag)
- Interactive REPL with tab completion
- Stateful project management with undo/redo
- Input validation against injection

Currently covering 645+ apps across creative, devops, security, CAD, and media categories.

Install: `pip install cli-anything`
GitHub: https://github.com/HKUDS/CLI-Anything

Would love feedback on the approach and contributions for new harnesses.

---

## Hacker News "Show HN"

**Title:** Show HN: CLI-Anything – Give your AI agent control over 645+ GUI apps

**Body:**
We built a framework that wraps GUI and CLI software into structured, agent-friendly interfaces.

The problem: AI agents (Claude, GPT, etc.) can generate code but can't interact with GUI software. Most powerful tools (GIMP, Blender, FreeCAD) have no CLI or limited CLI.

Our solution: headless CLI harnesses that:
1. Run the software without a GUI (headless mode)
2. Expose structured commands (JSON in/out)
3. Support undo/redo state management
4. Validate input to prevent injection

It works with Claude Code, LangChain, CrewAI, and any MCP-compatible client.

We started with GIMP, Blender, and FreeCAD. Now covering 645+ apps across every major category.

`pip install cli-anything`
`cli-anything install gimp blender inkscape`

GitHub: https://github.com/HKUDS/CLI-Anything

Looking for feedback on the architecture and contributions for new harnesses.
