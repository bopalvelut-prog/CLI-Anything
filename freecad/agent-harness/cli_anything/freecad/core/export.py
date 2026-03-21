"""FreeCAD CLI - Import/Export operations."""

import os
from typing import Dict, Any, Optional, List
from cli_anything.freecad.core.engine import wrap_script, run_script

EXPORT_FORMATS = {
    "step": {"ext": ".step", "desc": "STEP (ISO 10303) — universal CAD exchange"},
    "stp": {"ext": ".stp", "desc": "STEP (alternate extension)"},
    "iges": {"ext": ".iges", "desc": "IGES — legacy CAD exchange"},
    "igs": {"ext": ".igs", "desc": "IGES (alternate extension)"},
    "stl": {"ext": ".stl", "desc": "STL — 3D printing mesh format"},
    "obj": {"ext": ".obj", "desc": "Wavefront OBJ — mesh format"},
    "dxf": {"ext": ".dxf", "desc": "AutoCAD DXF — 2D drawing exchange"},
    "svg": {"ext": ".svg", "desc": "SVG — vector graphics (2D projections)"},
    "brep": {"ext": ".brep", "desc": "OpenCASCADE BREP — native geometry"},
    "fcstd": {"ext": ".FCStd", "desc": "FreeCAD native format"},
    "gcode": {"ext": ".ngc", "desc": "G-code — CNC/3D printing toolpath"},
    "pdf": {"ext": ".pdf", "desc": "PDF — 2D drawing export"},
    "png": {"ext": ".png", "desc": "PNG — rendered image"},
    "vrml": {"ext": ".wrl", "desc": "VRML — 3D web format"},
    "webgl": {"ext": ".html", "desc": "WebGL — interactive 3D in browser"},
}

IMPORT_FORMATS = [
    "step",
    "stp",
    "iges",
    "igs",
    "stl",
    "obj",
    "dxf",
    "svg",
    "brep",
    "fcstd",
]


def export_shape(
    output_path: str, obj_name: Optional[str] = None, fmt: Optional[str] = None
) -> Dict[str, Any]:
    """Export objects to a file format."""
    abs_path = os.path.abspath(output_path)

    if fmt is None:
        ext = os.path.splitext(abs_path)[1].lower().lstrip(".")
        fmt = ext
    fmt = fmt.lower().lstrip(".")

    if fmt not in EXPORT_FORMATS:
        raise ValueError(
            f"Unknown format: {fmt}. Supported: {', '.join(EXPORT_FORMATS.keys())}"
        )

    obj_filter = ""
    if obj_name:
        obj_filter = f'objects = [doc.getObject("{obj_name}")]'
    else:
        obj_filter = "objects = list(doc.Objects)"

    # Build export script based on format
    if fmt in ("step", "stp"):
        export_line = f'import ImportGui; ImportGui.export(objects, "{abs_path}")'
    elif fmt in ("iges", "igs"):
        export_line = f'import ImportGui; ImportGui.export(objects, "{abs_path}")'
    elif fmt == "stl":
        export_line = f'''
import Mesh
mesh = Mesh.Mesh()
for obj in objects:
    if hasattr(obj, "Shape"):
        mesh.addMesh(Mesh.Mesh(obj.Shape.tessellate(0.1)))
Mesh.export([mesh], "{abs_path}")
'''
    elif fmt == "obj":
        export_line = f'''
import Mesh
mesh = Mesh.Mesh()
for obj in objects:
    if hasattr(obj, "Shape"):
        mesh.addMesh(Mesh.Mesh(obj.Shape.tessellate(0.1)))
Mesh.export([mesh], "{abs_path}")
'''
    elif fmt == "brep":
        export_line = f'''
if len(objects) == 1 and hasattr(objects[0], "Shape"):
    objects[0].Shape.exportBrep("{abs_path}")
else:
    import Part
    compound = Part.makeCompound([o.Shape for o in objects if hasattr(o, "Shape")])
    compound.exportBrep("{abs_path}")
'''
    elif fmt == "svg":
        export_line = f'''
import Drawing
for obj in objects:
    if hasattr(obj, "Shape"):
        proj = Drawing.projectToSVG(obj.Shape, FreeCAD.Vector(0, 0, 1))
        with open("{abs_path}", "w") as f:
            f.write(proj)
        break
'''
    elif fmt == "dxf":
        export_line = f'''
try:
    import importDXF
    importDXF.export(objects, "{abs_path}")
except ImportError:
    raise RuntimeError("DXF export requires the Draft workbench")
'''
    elif fmt == "fcstd":
        export_line = f'doc.saveAs("{abs_path}")'
    else:
        export_line = f'raise RuntimeError("Export format {fmt} not yet implemented")'

    script = wrap_script(f'''
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
{obj_filter}
if not objects:
    raise RuntimeError("No objects to export")
{export_line}
import os
result = {{
    "status": "success",
    "output": "{abs_path}",
    "format": "{fmt}",
    "objects_exported": len(objects),
    "size_bytes": os.path.getsize("{abs_path}") if os.path.exists("{abs_path}") else 0,
}}
''')
    return run_script(script)


def export_all(output_dir: str, formats: Optional[List[str]] = None) -> Dict[str, Any]:
    """Export all objects to multiple formats."""
    if formats is None:
        formats = ["step", "stl"]

    abs_dir = os.path.abspath(output_dir)
    os.makedirs(abs_dir, exist_ok=True)

    # Build export commands for each format
    export_lines = []
    for fmt in formats:
        ext = EXPORT_FORMATS.get(fmt, {}).get("ext", f".{fmt}")
        out_path = os.path.join(abs_dir, f"model{ext}")
        if fmt in ("step", "stp"):
            export_lines.append(
                f'try: ImportGui.export(list(doc.Objects), "{out_path}"); exports.append("{fmt}")'
            )
            export_lines.append(
                f'except Exception as e: errors.append({{"format": "{fmt}", "error": str(e)}})'
            )
        elif fmt == "stl":
            export_lines.append(f'''
try:
    import Mesh
    mesh = Mesh.Mesh()
    for obj in doc.Objects:
        if hasattr(obj, "Shape"):
            mesh.addMesh(Mesh.Mesh(obj.Shape.tessellate(0.1)))
    Mesh.export([mesh], "{out_path}")
    exports.append("{fmt}")
except Exception as e:
    errors.append({{"format": "{fmt}", "error": str(e)}})
''')

    script = wrap_script(f'''
import os
import ImportGui
doc = FreeCAD.ActiveDocument
if doc is None:
    raise RuntimeError("No active document")
exports = []
errors = []
{chr(10).join(export_lines)}
result = {{
    "status": "success" if exports else "error",
    "output_dir": "{abs_dir}",
    "exported": exports,
    "errors": errors,
}}
''')
    return run_script(script)


def formats() -> Dict[str, Any]:
    """List supported import/export formats."""
    return {
        "export": {k: v["desc"] for k, v in EXPORT_FORMATS.items()},
        "import": IMPORT_FORMATS,
    }
