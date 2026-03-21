# FreeCAD: Project-Specific Analysis & SOP

## Architecture Summary

FreeCAD is an open-source parametric 3D CAD modeler built on **OpenCASCADE**
(OCC) geometry kernel with a modular workbench architecture.

```
┌──────────────────────────────────────────────┐
│                 FreeCAD GUI                  │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ 3D View  │ │ Property │ │   Task      │  │
│  │  (Qt3D)  │ │  Editor  │ │   Panel     │  │
│  └────┬──────┘ └────┬─────┘ └──────┬──────┘  │
│       │             │              │          │
│  ┌────┴─────────────┴──────────────┴───────┐ │
│  │         FreeCAD Core / App              │ │
│  │  Document, Object, Property system      │ │
│  └─────────────────┬───────────────────────┘ │
└────────────────────┼─────────────────────────┘
                     │
         ┌───────────┴──────────────────┐
         │  OpenCASCADE (OCCT) Kernel   │
         │  B-Rep geometry, NURBS,      │
         │  boolean ops, fillets, etc.  │
         └──────────────────────────────┘
```

## CLI Strategy: freecadcmd + Python API

FreeCAD provides `freecadcmd` — a headless Python interpreter with FreeCAD
modules pre-loaded. Our strategy:

1. **freecadcmd** — Execute Python scripts headlessly for all operations
2. **Python API** — FreeCAD's extensive Python API for document/object manipulation
3. **Script generation** — Generate Python scripts per CLI command, execute via freecadcmd
4. **JSON output** — Parse JSON from script stdout for agent consumption

### Why freecadcmd?

- Full access to FreeCAD's parametric modeling engine
- All workbenches available (Part, PartDesign, Mesh, Draft, etc.)
- OpenCASCADE kernel for production-grade geometry
- Native .FCStd format for parametric design preservation
- Export to STEP/STL/OBJ/IGES/BREP and more

## Command Map: GUI Action -> CLI Command

| GUI Action | CLI Command |
|-----------|-------------|
| File -> New | `doc new --name "Model"` |
| File -> Open | `doc open model.FCStd` |
| File -> Save | `doc save [path]` |
| Part -> Box | `shape box --length 10 --width 10 --height 10` |
| Part -> Cylinder | `shape cylinder --radius 5 --height 10` |
| Part -> Sphere | `shape sphere --radius 5` |
| Part -> Cone | `shape cone --radius1 5 --radius2 2 --height 10` |
| Part -> Torus | `shape torus --radius1 10 --radius2 2` |
| Part -> Boolean -> Union | `boolean fuse Obj1 Obj2` |
| Part -> Boolean -> Difference | `boolean cut Obj1 Obj2` |
| Part -> Boolean -> Intersection | `boolean intersect Obj1 Obj2` |
| Part -> Extrude | `feature extrude Sketch --length 10` |
| Part -> Revolve | `feature revolve Sketch --axis z --angle 360` |
| Part -> Fillet | `feature fillet Box --radius 2` |
| Part -> Chamfer | `feature chamfer Box --distance 1` |
| Part -> Mirror | `feature mirror Obj --plane xy` |
| Edit -> Placement -> Move | `feature translate Obj --x 10 --y 5` |
| Edit -> Placement -> Rotate | `feature rotate Obj --axis z --angle 45` |
| File -> Export -> STEP | `export to model.step` |
| File -> Export -> STL | `export to model.stl` |
| View -> Measure | `measure properties Obj` |

## Supported Export Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| STEP | .step/.stp | Universal CAD exchange (ISO 10303) |
| IGES | .iges/.igs | Legacy CAD exchange |
| STL | .stl | 3D printing mesh format |
| OBJ | .obj | Wavefront mesh format |
| BREP | .brep | OpenCASCADE native geometry |
| SVG | .svg | 2D vector projection |
| DXF | .dxf | AutoCAD 2D drawing exchange |
| VRML | .wrl | 3D web format |

## OpenCASCADE Geometry Primitives

FreeCAD's Part workbench provides these shape types:
- **Box** — Rectangular prism
- **Cylinder** — Circular prism
- **Sphere** — Full sphere
- **Cone** — Frustum (truncated cone)
- **Torus** — Donut shape
- **Tube** — Hollow cylinder (via boolean cut)

## Test Coverage Plan

1. **Unit tests** (`test_core.py`): No FreeCAD required
   - Session create/status/undo/redo
   - Format listing
   - Script generation/wrapping
   - CLI argument parsing

2. **E2E tests** (`test_full_e2e.py`): Requires FreeCAD
   - Document create/save/open
   - Primitive shape creation
   - Boolean operations
   - Export to STEP/STL
   - Measurement operations

## Rendering Gap Assessment: **Low**

FreeCAD's Python API is extremely comprehensive. Almost all GUI operations
have direct API equivalents. The main gaps are:
- Some advanced sketcher constraints require interactive input
- Visual debugging (stress analysis visualization) not available headlessly
- Some workbenches (TechDraw) are primarily visual/GUI-oriented
