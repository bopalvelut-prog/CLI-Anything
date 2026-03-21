"""FreeCAD CLI - Document management (create, open, save, info)."""

import os
from typing import Dict, Any, Optional
from cli_anything.freecad.core.engine import wrap_script, run_script


def create(name: str = "Untitled", unit_system: str = "Standard") -> Dict[str, Any]:
    """Create a new FreeCAD document."""
    script = wrap_script(f'''
doc = FreeCAD.newDocument("{name}")
doc.UnitSystem = "{unit_system}"
doc.recompute()

objects = []
for obj in doc.Objects:
    objects.append({{
        "name": obj.Name,
        "label": obj.Label,
        "type": obj.TypeId,
    }})

result = {{
    "status": "success",
    "name": doc.Name,
    "label": doc.Label,
    "unit_system": doc.UnitSystem,
    "objects": objects,
    "object_count": len(objects),
}}
''')
    return run_script(script)


def open_doc(path: str) -> Dict[str, Any]:
    """Open an existing FreeCAD document (.FCStd)."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {path}")

    script = wrap_script(f'''
doc = FreeCAD.openDocument("{abs_path}")
doc.recompute()

objects = []
for obj in doc.Objects:
    info = {{
        "name": obj.Name,
        "label": obj.Label,
        "type": obj.TypeId,
    }}
    if hasattr(obj, "Shape") and obj.Shape:
        info["volume_mm3"] = round(obj.Shape.Volume, 3)
        info["area_mm2"] = round(obj.Shape.Area, 3)
    objects.append(info)

result = {{
    "status": "success",
    "path": "{abs_path}",
    "name": doc.Name,
    "label": doc.Label,
    "unit_system": doc.UnitSystem,
    "objects": objects,
    "object_count": len(objects),
}}
''')
    return run_script(script)


def save(path: Optional[str] = None) -> Dict[str, Any]:
    """Save the current document."""
    save_as = ""
    if path:
        save_as = f' doc.saveAs("{os.path.abspath(path)}")'
    else:
        save_as = " doc.save()"

    script = wrap_script(f"""
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
{save_as}
result = {{
    "status": "success",
    "path": doc.FileName,
    "name": doc.Name,
}}
""")
    return run_script(script)


def info() -> Dict[str, Any]:
    """Get document info."""
    script = wrap_script("""
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")

objects = []
for obj in doc.Objects:
    info = {
        "name": obj.Name,
        "label": obj.Label,
        "type": obj.TypeId,
    }
    if hasattr(obj, "Shape") and obj.Shape:
        shape = obj.Shape
        info["volume_mm3"] = round(shape.Volume, 3)
        info["area_mm2"] = round(shape.Area, 3)
        bbox = shape.BoundBox
        info["bounding_box"] = {
            "x_min": round(bbox.XMin, 3), "x_max": round(bbox.XMax, 3),
            "y_min": round(bbox.YMin, 3), "y_max": round(bbox.YMax, 3),
            "z_min": round(bbox.ZMin, 3), "z_max": round(bbox.ZMax, 3),
            "length": round(bbox.XMax - bbox.XMin, 3),
            "width": round(bbox.YMax - bbox.YMin, 3),
            "height": round(bbox.ZMax - bbox.ZMin, 3),
        }
    objects.append(info)

result = {
    "status": "success",
    "name": doc.Name,
    "label": doc.Label,
    "filename": doc.FileName,
    "unit_system": doc.UnitSystem,
    "objects": objects,
    "object_count": len(objects),
}
""")
    return run_script(script)


def list_objects() -> Dict[str, Any]:
    """List all objects in the document."""
    script = wrap_script("""
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")

objects = []
for obj in doc.Objects:
    o = {
        "name": obj.Name,
        "label": obj.Label,
        "type": obj.TypeId,
    }
    if hasattr(obj, "Shape") and obj.Shape:
        o["solid"] = obj.Shape.Solids != []
        o["face_count"] = len(obj.Shape.Faces)
        o["edge_count"] = len(obj.Shape.Edges)
        o["vertex_count"] = len(obj.Shape.Vertexes)
    objects.append(o)

result = {"status": "success", "objects": objects, "count": len(objects)}
""")
    return run_script(script)


def close() -> Dict[str, Any]:
    """Close the active document."""
    script = wrap_script("""
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
name = doc.Name
FreeCAD.closeDocument(name)
result = {"status": "success", "closed": name}
""")
    return run_script(script)
