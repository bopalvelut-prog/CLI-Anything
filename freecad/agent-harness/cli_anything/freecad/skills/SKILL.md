---
name: >-
  cli-anything-freecad
description: >-
  Command-line interface for FreeCAD - Parametric 3D CAD modeling, boolean
  operations, feature modeling, export to STEP/STL/OBJ, and measurement...
---

# cli-anything-freecad

A stateful command-line interface for parametric 3D CAD modeling, built on FreeCAD.

## Prerequisites

- Python 3.10+
- FreeCAD (`apt install freecad freecad-python3`)

## Command Groups

### Document

| Command | Description |
|---------|-------------|
| `new` | Create a new document |
| `open` | Open an existing .FCStd file |
| `save` | Save the document |
| `info` | Show document info and objects |
| `list` | List all objects |
| `close` | Close the document |

### Shape (Primitives)

| Command | Description |
|---------|-------------|
| `box` | Create a box (length, width, height) |
| `cylinder` | Create a cylinder (radius, height) |
| `sphere` | Create a sphere (radius) |
| `cone` | Create a cone/frustum (r1, r2, height) |
| `torus` | Create a torus (major/minor radius) |
| `tube` | Create a hollow tube (outer/inner radius) |

### Boolean

| Command | Description |
|---------|-------------|
| `fuse` | Boolean union of two objects |
| `cut` | Boolean difference (subtract) |
| `intersect` | Boolean intersection |

### Feature

| Command | Description |
|---------|-------------|
| `extrude` | Extrude a shape along x/y/z axis |
| `revolve` | Revolve a shape around an axis |
| `fillet` | Round edges (fillet radius) |
| `chamfer` | Bevel edges (chamfer distance) |
| `mirror` | Mirror across xy/xz/yz plane |
| `translate` | Move object to position |
| `rotate` | Rotate object around axis |
| `scale` | Scale object uniformly |

### Export

| Command | Description |
|---------|-------------|
| `to` | Export to STEP, STL, OBJ, BREP, SVG, DXF |
| `all` | Export to multiple formats at once |
| `formats` | List supported formats |

### Measure

| Command | Description |
|---------|-------------|
| `properties` | Get all object properties |
| `distance` | Distance between two objects |
| `volume` | Object volume |
| `area` | Object surface area |
| `center` | Center of mass |
| `bbox` | Bounding box |
| `check` | Check shape validity |

### Mesh

| Command | Description |
|---------|-------------|
| `tessellate` | Convert solid to mesh |
| `decimate` | Reduce face count |
| `info` | Get mesh/shape info |
| `repair` | Fix non-manifold geometry |

## Examples

```bash
# Create a bracket with a hole
cli-anything-freecad doc new --name "Bracket"
cli-anything-freecad shape box --length 40 --width 20 --height 5
cli-anything-freecad shape cylinder --radius 3 --height 6 --x 10 --y 10
cli-anything-freecad boolean cut Box Cylinder

# Measure the result
cli-anything-freecad --json measure properties Cut

# Export for manufacturing
cli-anything-freecad export to bracket.step
cli-anything-freecad export to bracket.stl
```

## Version

1.0.0
