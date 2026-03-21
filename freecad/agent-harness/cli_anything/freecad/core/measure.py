"""FreeCAD CLI - Measurement and analysis tools."""

from typing import Dict, Any, Optional
from cli_anything.freecad.core.engine import wrap_script, run_script


def properties(obj_name: str) -> Dict[str, Any]:
    """Get all properties of an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")

props = {{
    "name": obj.Name,
    "label": obj.Label,
    "type": obj.TypeId,
}}

if hasattr(obj, "Shape") and obj.Shape:
    shape = obj.Shape
    props["volume_mm3"] = round(shape.Volume, 3)
    props["area_mm2"] = round(shape.Area, 3)
    props["solid_count"] = len(shape.Solids)
    props["face_count"] = len(shape.Faces)
    props["edge_count"] = len(shape.Edges)
    props["vertex_count"] = len(shape.Vertexes)
    props["is_closed"] = shape.isClosed()
    props["is_valid"] = shape.isValid()
    bb = shape.BoundBox
    props["bounding_box"] = {{
        "length": round(bb.XMax - bb.XMin, 3),
        "width": round(bb.YMax - bb.YMin, 3),
        "height": round(bb.ZMax - bb.ZMin, 3),
    }}

# Get parametric properties
param_props = []
for prop in obj.PropertiesList:
    try:
        val = getattr(obj, prop)
        param_props.append({{"name": prop, "type": type(val).__name__, "value": str(val)}})
    except Exception:
        pass
props["parametric_properties"] = param_props

result = props
''')
    return run_script(script)


def distance(obj1: str, obj2: str) -> Dict[str, Any]:
    """Measure distance between two objects (center of mass)."""
    script = wrap_script(f'''
import Part
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
o1 = doc.getObject("{obj1}")
o2 = doc.getObject("{obj2}")
if o1 is None:
    raise RuntimeError("Object not found: {obj1}")
if o2 is None:
    raise RuntimeError("Object not found: {obj2}")

if hasattr(o1, "Shape") and hasattr(o2, "Shape"):
    dist = o1.Shape.distToShape(o2.Shape)
    result = {{
        "status": "success",
        "object1": "{obj1}",
        "object2": "{obj2}",
        "distance_mm": round(dist[0], 6),
        "nearest_point_1": [round(p, 6) for p in (dist[1][0].x, dist[1][0].y, dist[1][0].z)],
        "nearest_point_2": [round(p, 6) for p in (dist[2][0].x, dist[2][0].y, dist[2][0].z)],
    }}
else:
    raise RuntimeError("Objects must have Shape attribute for distance measurement")
''')
    return run_script(script)


def volume(obj_name: str) -> Dict[str, Any]:
    """Get volume of an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
result = {{
    "status": "success",
    "name": obj.Name,
    "volume_mm3": round(obj.Shape.Volume, 6),
    "volume_cm3": round(obj.Shape.Volume / 1000, 6),
}}
''')
    return run_script(script)


def area(obj_name: str) -> Dict[str, Any]:
    """Get surface area of an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
result = {{
    "status": "success",
    "name": obj.Name,
    "area_mm2": round(obj.Shape.Area, 6),
    "area_cm2": round(obj.Shape.Area / 100, 6),
}}
''')
    return run_script(script)


def center_of_mass(obj_name: str) -> Dict[str, Any]:
    """Get center of mass of an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
com = obj.Shape.CenterOfMass
result = {{
    "status": "success",
    "name": obj.Name,
    "center_of_mass": {{
        "x": round(com.x, 6),
        "y": round(com.y, 6),
        "z": round(com.z, 6),
    }},
    "volume_mm3": round(obj.Shape.Volume, 6),
}}
''')
    return run_script(script)


def bounding_box(obj_name: str) -> Dict[str, Any]:
    """Get bounding box of an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
bb = obj.Shape.BoundBox
result = {{
    "status": "success",
    "name": obj.Name,
    "x_min": round(bb.XMin, 6), "x_max": round(bb.XMax, 6),
    "y_min": round(bb.YMin, 6), "y_max": round(bb.YMax, 6),
    "z_min": round(bb.ZMin, 6), "z_max": round(bb.ZMax, 6),
    "length": round(bb.XMax - bb.XMin, 6),
    "width": round(bb.YMax - bb.YMin, 6),
    "height": round(bb.ZMax - bb.ZMin, 6),
    "diagonal": round(bb.DiagonalLength, 6),
}}
''')
    return run_script(script)


def check_validity(obj_name: str) -> Dict[str, Any]:
    """Check if a shape is valid and report issues."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
if not hasattr(obj, "Shape"):
    raise RuntimeError("Object has no shape")
shape = obj.Shape
issues = []
if not shape.isValid():
    issues.append("Shape is not valid (self-intersections or degenerate geometry)")
if shape.isNull():
    issues.append("Shape is null")
if not shape.isClosed() and shape.Solids:
    issues.append("Shape has solids but is not closed")
result = {{
    "status": "success",
    "name": obj.Name,
    "is_valid": shape.isValid(),
    "is_null": shape.isNull(),
    "is_closed": shape.isClosed(),
    "is_manifold": len(shape.Faces) > 0 and all(f.isValid() for f in shape.Faces),
    "issues": issues,
    "face_count": len(shape.Faces),
    "edge_count": len(shape.Edges),
    "vertex_count": len(shape.Vertexes),
}}
''')
    return run_script(script)
