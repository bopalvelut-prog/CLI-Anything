# cli-anything-freecad

A stateful command-line interface for parametric 3D CAD modeling, built on FreeCAD. Designed for AI agents and engineers who need to create, modify, and export 3D models without a GUI.

## Features

- **Documents** — Create, open, save .FCStd parametric documents
- **Primitives** — Box, cylinder, sphere, cone, torus, tube
- **Booleans** — Fuse (union), cut (difference), intersect
- **Features** — Extrude, revolve, fillet, chamfer, mirror, translate, rotate, scale
- **Export** — STEP, STL, OBJ, BREP, SVG, DXF, and more
- **Measurement** — Volume, area, distance, center of mass, bounding box, validity check
- **Mesh** — Tessellate, decimate, repair
- **JSON output** — Machine-readable output with `--json` flag
- **REPL** — Interactive session with undo/redo history

## Installation

```bash
cd agent-harness
pip install -e .
```

**Prerequisites:**
- Python 3.10+
- FreeCAD (`apt install freecad freecad-python3`)

## Quick Start

```bash
# Create a new document and add shapes
cli-anything-freecad doc new --name "Bracket"
cli-anything-freecad shape box --length 40 --width 20 --height 5
cli-anything-freecad shape cylinder --radius 3 --height 6 --x 10 --y 10
cli-anything-freecad boolean cut Box Cylinder

# Export to STEP for manufacturing
cli-anything-freecad export to bracket.step

# Or export to STL for 3D printing
cli-anything-freecad export to bracket.stl
```
