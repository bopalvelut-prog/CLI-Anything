"""FreeCAD CLI - Shape creation (primitives, booleans, features)."""

import os
from typing import Dict, Any, Optional
from cli_anything.freecad.core.engine import wrap_script, run_script


# ── Primitives ──────────────────────────────────────────────────


def box(
    name: str = "Box",
    length: float = 10,
    width: float = 10,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
) -> Dict[str, Any]:
    """Create a box primitive."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.addObject("Part::Box", "{name}")
obj.Length = {length}
obj.Width = {width}
obj.Height = {height}
obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "type": "Box",
    "volume_mm3": round(obj.Shape.Volume, 3),
    "area_mm2": round(obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def cylinder(
    name: str = "Cylinder",
    radius: float = 5,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
) -> Dict[str, Any]:
    """Create a cylinder primitive."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.addObject("Part::Cylinder", "{name}")
obj.Radius = {radius}
obj.Height = {height}
obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "type": "Cylinder",
    "volume_mm3": round(obj.Shape.Volume, 3),
    "area_mm2": round(obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def sphere(
    name: str = "Sphere", radius: float = 5, x: float = 0, y: float = 0, z: float = 0
) -> Dict[str, Any]:
    """Create a sphere primitive."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.addObject("Part::Sphere", "{name}")
obj.Radius = {radius}
obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "type": "Sphere",
    "volume_mm3": round(obj.Shape.Volume, 3),
    "area_mm2": round(obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def cone(
    name: str = "Cone",
    radius1: float = 5,
    radius2: float = 2,
    height: float = 10,
    x: float = 0,
    y: float = 0,
    z: float = 0,
) -> Dict[str, Any]:
    """Create a cone (frustum) primitive."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.addObject("Part::Cone", "{name}")
obj.Radius1 = {radius1}
obj.Radius2 = {radius2}
obj.Height = {height}
obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "type": "Cone",
    "volume_mm3": round(obj.Shape.Volume, 3),
    "area_mm2": round(obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def torus(
    name: str = "Torus",
    radius1: float = 10,
    radius2: float = 2,
    x: float = 0,
    y: float = 0,
    z: float = 0,
) -> Dict[str, Any]:
    """Create a torus primitive."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.addObject("Part::Torus", "{name}")
obj.Radius1 = {radius1}
obj.Radius2 = {radius2}
obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "type": "Torus",
    "volume_mm3": round(obj.Shape.Volume, 3),
    "area_mm2": round(obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def tube(
    name: str = "Tube",
    outer_radius: float = 10,
    inner_radius: float = 8,
    height: float = 20,
    x: float = 0,
    y: float = 0,
    z: float = 0,
) -> Dict[str, Any]:
    """Create a hollow tube (cylinder with hole)."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
outer = doc.addObject("Part::Cylinder", "{name}_outer")
outer.Radius = {outer_radius}
outer.Height = {height}
inner = doc.addObject("Part::Cylinder", "{name}_inner")
inner.Radius = {inner_radius}
inner.Height = {height}
inner.Placement = FreeCAD.Placement(
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Rotation()
)
cut = doc.addObject("Part::Cut", "{name}")
cut.Base = outer
cut.Tool = inner
cut.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": cut.Name, "type": "Tube",
    "volume_mm3": round(cut.Shape.Volume, 3),
    "area_mm2": round(cut.Shape.Area, 3),
}}
''')
    return run_script(script)


# ── Boolean Operations ──────────────────────────────────────────


def fuse(obj1: str, obj2: str, name: str = "Fusion") -> Dict[str, Any]:
    """Boolean union of two objects."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj1}")
tool = doc.getObject("{obj2}")
if base is None or tool is None:
    raise RuntimeError("Object not found")
result_obj = doc.addObject("Part::Fuse", "{name}")
result_obj.Base = base
result_obj.Tool = tool
doc.recompute()
result = {{
    "status": "success", "name": result_obj.Name, "type": "Fuse",
    "volume_mm3": round(result_obj.Shape.Volume, 3),
    "area_mm2": round(result_obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def cut(obj1: str, obj2: str, name: str = "Cut") -> Dict[str, Any]:
    """Boolean difference (subtract obj2 from obj1)."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj1}")
tool = doc.getObject("{obj2}")
if base is None or tool is None:
    raise RuntimeError("Object not found")
result_obj = doc.addObject("Part::Cut", "{name}")
result_obj.Base = base
result_obj.Tool = tool
doc.recompute()
result = {{
    "status": "success", "name": result_obj.Name, "type": "Cut",
    "volume_mm3": round(result_obj.Shape.Volume, 3),
    "area_mm2": round(result_obj.Shape.Area, 3),
}}
''')
    return run_script(script)


def intersect(obj1: str, obj2: str, name: str = "Common") -> Dict[str, Any]:
    """Boolean intersection of two objects."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj1}")
tool = doc.getObject("{obj2}")
if base is None or tool is None:
    raise RuntimeError("Object not found")
result_obj = doc.addObject("Part::Common", "{name}")
result_obj.Base = base
result_obj.Tool = tool
doc.recompute()
result = {{
    "status": "success", "name": result_obj.Name, "type": "Common",
    "volume_mm3": round(result_obj.Shape.Volume, 3),
    "area_mm2": round(result_obj.Shape.Area, 3),
}}
''')
    return run_script(script)


# ── Feature Operations ──────────────────────────────────────────


def extrude(
    obj_name: str, name: str = "Extrude", length: float = 10, direction: str = "z"
) -> Dict[str, Any]:
    """Extrude a shape along an axis."""
    dirs = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}
    dx, dy, dz = dirs.get(direction, (0, 0, 1))

    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj_name}")
if base is None:
    raise RuntimeError("Object not found: {obj_name}")
ext = doc.addObject("Part::Extrusion", "{name}")
ext.Base = base
ext.Dir = FreeCAD.Vector({dx} * {length}, {dy} * {length}, {dz} * {length})
ext.Solid = True
doc.recompute()
result = {{
    "status": "success", "name": ext.Name, "type": "Extrusion",
    "volume_mm3": round(ext.Shape.Volume, 3),
    "area_mm2": round(ext.Shape.Area, 3),
}}
''')
    return run_script(script)


def revolve(
    obj_name: str, name: str = "Revolve", axis: str = "z", angle: float = 360
) -> Dict[str, Any]:
    """Revolve a shape around an axis."""
    axes = {
        "x": "FreeCAD.Vector(1,0,0)",
        "y": "FreeCAD.Vector(0,1,0)",
        "z": "FreeCAD.Vector(0,0,1)",
    }
    axis_vec = axes.get(axis, axes["z"])

    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj_name}")
if base is None:
    raise RuntimeError("Object not found: {obj_name}")
rev = doc.addObject("Part::Revolution", "{name}")
rev.Source = base
rev.Axis = {axis_vec}
rev.Angle = {angle}
rev.Solid = True
doc.recompute()
result = {{
    "status": "success", "name": rev.Name, "type": "Revolution",
    "volume_mm3": round(rev.Shape.Volume, 3),
    "area_mm2": round(rev.Shape.Area, 3),
}}
''')
    return run_script(script)


def fillet(obj_name: str, radius: float = 1, name: str = "Fillet") -> Dict[str, Any]:
    """Apply fillet (rounded edges) to an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj_name}")
if base is None:
    raise RuntimeError("Object not found: {obj_name}")
fil = doc.addObject("Part::Fillet", "{name}")
fil.Base = base)
edges = list(range(1, len(base.Shape.Edges) + 1))
fil.Edges = [(e, {radius}, {radius}) for e in edges]
doc.recompute()
result = {{
    "status": "success", "name": fil.Name, "type": "Fillet",
    "radius": {radius},
    "edge_count": len(base.Shape.Edges),
    "volume_mm3": round(fil.Shape.Volume, 3),
}}
''')
    return run_script(script)


def chamfer(
    obj_name: str, distance: float = 1, name: str = "Chamfer"
) -> Dict[str, Any]:
    """Apply chamfer (beveled edges) to an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj_name}")
if base is None:
    raise RuntimeError("Object not found: {obj_name}")
cha = doc.addObject("Part::Chamfer", "{name}")
cha.Base = base
edges = list(range(1, len(base.Shape.Edges) + 1))
cha.Edges = [(e, {distance}, {distance}) for e in edges]
doc.recompute()
result = {{
    "status": "success", "name": cha.Name, "type": "Chamfer",
    "distance": {distance},
    "edge_count": len(base.Shape.Edges),
    "volume_mm3": round(cha.Shape.Volume, 3),
}}
''')
    return run_script(script)


def mirror(obj_name: str, plane: str = "xy", name: str = "Mirror") -> Dict[str, Any]:
    """Mirror an object across a plane."""
    planes = {
        "xy": ("FreeCAD.Vector(0,0,0)", "FreeCAD.Vector(0,0,1)"),
        "xz": ("FreeCAD.Vector(0,0,0)", "FreeCAD.Vector(0,1,0)"),
        "yz": ("FreeCAD.Vector(0,0,0)", "FreeCAD.Vector(1,0,0)"),
    }
    base_pt, norm = planes.get(plane, planes["xy"])

    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj_name}")
if base is None:
    raise RuntimeError("Object not found: {obj_name}")
mir = doc.addObject("Part::Mirroring", "{name}")
mir.Source = base
mir.Base = {base_pt}
mir.Normal = {norm}
doc.recompute()
result = {{
    "status": "success", "name": mir.Name, "type": "Mirror",
    "plane": "{plane}",
    "volume_mm3": round(mir.Shape.Volume, 3),
}}
''')
    return run_script(script)


def translate(
    obj_name: str, x: float = 0, y: float = 0, z: float = 0
) -> Dict[str, Any]:
    """Move/translate an object."""
    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector({x}, {y}, {z}),
    FreeCAD.Rotation()
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "action": "translate",
    "position": {{"x": {x}, "y": {y}, "z": {z}}},
}}
''')
    return run_script(script)


def rotate(
    obj_name: str,
    axis: str = "z",
    angle: float = 45,
    x: float = 0,
    y: float = 0,
    z: float = 0,
) -> Dict[str, Any]:
    """Rotate an object around an axis."""
    axes = {
        "x": "FreeCAD.Vector(1,0,0)",
        "y": "FreeCAD.Vector(0,1,0)",
        "z": "FreeCAD.Vector(0,0,1)",
    }
    axis_vec = axes.get(axis, axes["z"])

    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
obj = doc.getObject("{obj_name}")
if obj is None:
    raise RuntimeError("Object not found: {obj_name}")
center = FreeCAD.Vector({x}, {y}, {z})
rotation = FreeCAD.Rotation({axis_vec}, {angle})
obj.Placement = FreeCAD.Placement(
    obj.Placement.Base,
    rotation * obj.Placement.Rotation
)
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "action": "rotate",
    "axis": "{axis}", "angle": {angle},
}}
''')
    return run_script(script)


def scale(obj_name: str, factor: float = 2.0, name: str = "Scale") -> Dict[str, Any]:
    """Scale an object uniformly."""
    script = wrap_script(f'''
import Part
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
base = doc.getObject("{obj_name}")
if base is None:
    raise RuntimeError("Object not found: {obj_name}")
mat = FreeCAD.Matrix()
mat.scale({factor}, {factor}, {factor})
new_shape = base.Shape.transformGeometry(mat)
obj = doc.addObject("Part::Feature", "{name}")
obj.Shape = new_shape
doc.recompute()
result = {{
    "status": "success", "name": obj.Name, "action": "scale",
    "factor": {factor},
    "volume_mm3": round(obj.Shape.Volume, 3),
}}
''')
    return run_script(script)
