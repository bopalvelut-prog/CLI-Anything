"""FreeCAD CLI - Mesh operations."""

import os
from typing import Dict, Any, Optional
from cli_anything.freecad.core.engine import wrap_script, run_script


def from_shape(
    obj_name: str, tolerance: float = 0.1, name: str = "Mesh"
) -> Dict[str, Any]:
    """Convert a solid shape to a mesh."""
    script = wrap_script(f'''
import Mesh
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
mesh_obj = doc.addObject("Mesh::Feature", "{name}")
mesh_obj.Mesh = Mesh.Mesh(obj.Shape.tessellate({tolerance}))
doc.recompute()
result = {{
    "status": "success",
    "name": mesh_obj.Name,
    "vertices": mesh_obj.Mesh.CountPoints,
    "faces": mesh_obj.Mesh.CountFacets,
    "tolerance": {tolerance},
}}
''')
    return run_script(script)


def decimate(
    obj_name: str, reduction: float = 0.5, name: str = "DecimatedMesh"
) -> Dict[str, Any]:
    """Decimate a mesh (reduce face count)."""
    script = wrap_script(f'''
import Mesh
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Mesh"):
    raise RuntimeError("Object is not a mesh")
target = int(obj.Mesh.CountFacets * {reduction})
result_mesh = obj.Mesh.copy()
result_mesh.decimate(target)
mesh_obj = doc.addObject("Mesh::Feature", "{name}")
mesh_obj.Mesh = result_mesh
doc.recompute()
result = {{
    "status": "success",
    "name": mesh_obj.Name,
    "original_faces": obj.Mesh.CountFacets,
    "decimated_faces": result_mesh.CountFacets,
    "reduction": {reduction},
}}
''')
    return run_script(script)


def info(obj_name: str) -> Dict[str, Any]:
    """Get mesh info (vertex/face count, volume, area)."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if hasattr(obj, "Mesh"):
    mesh = obj.Mesh
    result = {{
        "status": "success",
        "name": obj.Name,
        "type": "mesh",
        "vertices": mesh.CountPoints,
        "faces": mesh.CountFacets,
        "volume_mm3": round(mesh.Volume, 6),
        "area_mm2": round(mesh.Area, 6),
    }}
elif hasattr(obj, "Shape"):
    shape = obj.Shape
    result = {{
        "status": "success",
        "name": obj.Name,
        "type": "shape",
        "faces": len(shape.Faces),
        "edges": len(shape.Edges),
        "vertices": len(shape.Vertexes),
        "volume_mm3": round(shape.Volume, 6),
        "area_mm2": round(shape.Area, 6),
    }}
else:
    raise RuntimeError("Object has neither Mesh nor Shape")
''')
    return run_script(script)


def repair(obj_name: str, name: str = "RepairedMesh") -> Dict[str, Any]:
    """Repair a mesh (fix non-manifold edges, degenerate faces)."""
    script = wrap_script(f'''
import Mesh
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Mesh"):
    raise RuntimeError("Object is not a mesh")
result_mesh = obj.Mesh.copy()
result_mesh.rebuildNonManifoldEdge()
result_mesh.removeDegeneratedFacets()
result_mesh.removeDuplicatedFacets()
result_mesh.removeDuplicatedPoints()
result_mesh.rebuildIndex()
mesh_obj = doc.addObject("Mesh::Feature", "{name}")
mesh_obj.Mesh = result_mesh
doc.recompute()
result = {{
    "status": "success",
    "name": mesh_obj.Name,
    "vertices": result_mesh.CountPoints,
    "faces": result_mesh.CountFacets,
    "volume_mm3": round(result_mesh.Volume, 6),
}}
''')
    return run_script(script)


def cross_section(
    obj_name: str, height: float = 0, axis: str = "z", name: str = "Section"
) -> Dict[str, Any]:
    """Create cross-sections of a mesh at given heights."""
    axes = {
        "x": "FreeCAD.Vector(1,0,0)",
        "y": "FreeCAD.Vector(0,1,0)",
        "z": "FreeCAD.Vector(0,0,1)",
    }
    axis_vec = axes.get(axis, axes["z"])

    script = wrap_script(f'''
import Mesh
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
section = obj.Shape.section(FreeCAD.Placement(
    FreeCAD.Vector(0, 0, {height}),
    FreeCAD.Rotation({axis_vec}, 0)
))
sketch = doc.addObject("Sketcher::SketchObject", "{name}")
sketch.Geometry = section.Edges
doc.recompute()
result = {{
    "status": "success",
    "name": sketch.Name,
    "height": {height},
    "axis": "{axis}",
    "edge_count": len(section.Edges),
}}
''')
    return run_script(script)
