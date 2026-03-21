#!/usr/bin/env python3
"""FreeCAD CLI — A stateful command-line interface for parametric 3D CAD.

This CLI wraps FreeCAD's powerful parametric modeling capabilities into a
structured, agent-friendly interface with JSON output, project state, and
REPL mode.

Usage:
    # One-shot commands
    cli-anything-freecad doc new --name "MyModel"
    cli-anything-freecad shape box --length 20 --width 10 --height 5
    cli-anything-freecad boolean fuse Box Cylinder
    cli-anything-freecad export model.step

    # Interactive REPL
    cli-anything-freecad
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.freecad.core.session import Session
from cli_anything.freecad.core import document as doc_mod
from cli_anything.freecad.core import shapes as shape_mod
from cli_anything.freecad.core import export as export_mod
from cli_anything.freecad.core import measure as measure_mod
from cli_anything.freecad.core import mesh_ops as mesh_mod

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_not_found"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except (ValueError, IndexError, RuntimeError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI Group ──────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """FreeCAD CLI — Stateful parametric 3D CAD from the command line.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Document Commands ───────────────────────────────────────────
@cli.group()
def doc():
    """Document management commands."""
    pass


@doc.command("new")
@click.option("--name", "-n", default="Untitled", help="Document name")
@click.option("--unit", default="Standard", help="Unit system")
@handle_error
def doc_new(name, unit):
    """Create a new FreeCAD document."""
    result = doc_mod.create(name, unit)
    output(result)


@doc.command("open")
@click.argument("path")
@handle_error
def doc_open(path):
    """Open an existing .FCStd document."""
    result = doc_mod.open_doc(path)
    output(result)


@doc.command("save")
@click.argument("path", required=False)
@handle_error
def doc_save(path):
    """Save the active document."""
    result = doc_mod.save(path)
    output(result, f"Saved to: {result.get('path', '')}")


@doc.command("info")
@handle_error
def doc_info():
    """Show document info and list objects."""
    result = doc_mod.info()
    output(result)


@doc.command("list")
@handle_error
def doc_list():
    """List all objects in the document."""
    result = doc_mod.list_objects()
    output(result)


@doc.command("close")
@handle_error
def doc_close():
    """Close the active document."""
    result = doc_mod.close()
    output(result)


# ── Shape Commands ──────────────────────────────────────────────
@cli.group()
def shape():
    """Primitive shape creation commands."""
    pass


@shape.command("box")
@click.option("--name", "-n", default="Box")
@click.option("--length", "-l", type=float, default=10)
@click.option("--width", "-w", type=float, default=10)
@click.option("--height", "-h", type=float, default=10)
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def shape_box(name, length, width, height, x, y, z):
    """Create a box primitive."""
    result = shape_mod.box(name, length, width, height, x, y, z)
    output(result)


@shape.command("cylinder")
@click.option("--name", "-n", default="Cylinder")
@click.option("--radius", "-r", type=float, default=5)
@click.option("--height", "-h", type=float, default=10)
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def shape_cylinder(name, radius, height, x, y, z):
    """Create a cylinder primitive."""
    result = shape_mod.cylinder(name, radius, height, x, y, z)
    output(result)


@shape.command("sphere")
@click.option("--name", "-n", default="Sphere")
@click.option("--radius", "-r", type=float, default=5)
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def shape_sphere(name, radius, x, y, z):
    """Create a sphere primitive."""
    result = shape_mod.sphere(name, radius, x, y, z)
    output(result)


@shape.command("cone")
@click.option("--name", "-n", default="Cone")
@click.option("--radius1", "-r1", type=float, default=5)
@click.option("--radius2", "-r2", type=float, default=2)
@click.option("--height", "-h", type=float, default=10)
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def shape_cone(name, radius1, radius2, height, x, y, z):
    """Create a cone/frustum primitive."""
    result = shape_mod.cone(name, radius1, radius2, height, x, y, z)
    output(result)


@shape.command("torus")
@click.option("--name", "-n", default="Torus")
@click.option("--radius1", "-r1", type=float, default=10, help="Major radius")
@click.option("--radius2", "-r2", type=float, default=2, help="Minor radius")
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def shape_torus(name, radius1, radius2, x, y, z):
    """Create a torus primitive."""
    result = shape_mod.torus(name, radius1, radius2, x, y, z)
    output(result)


@shape.command("tube")
@click.option("--name", "-n", default="Tube")
@click.option("--outer-radius", "-or", type=float, default=10)
@click.option("--inner-radius", "-ir", type=float, default=8)
@click.option("--height", "-h", type=float, default=20)
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def shape_tube(name, outer_radius, inner_radius, height, x, y, z):
    """Create a hollow tube."""
    result = shape_mod.tube(name, outer_radius, inner_radius, height, x, y, z)
    output(result)


# ── Boolean Commands ────────────────────────────────────────────
@cli.group()
def boolean():
    """Boolean operation commands."""
    pass


@boolean.command("fuse")
@click.argument("obj1")
@click.argument("obj2")
@click.option("--name", "-n", default="Fusion")
@handle_error
def boolean_fuse(obj1, obj2, name):
    """Boolean union of two objects."""
    result = shape_mod.fuse(obj1, obj2, name)
    output(result)


@boolean.command("cut")
@click.argument("obj1")
@click.argument("obj2")
@click.option("--name", "-n", default="Cut")
@handle_error
def boolean_cut(obj1, obj2, name):
    """Boolean difference (subtract obj2 from obj1)."""
    result = shape_mod.cut(obj1, obj2, name)
    output(result)


@boolean.command("intersect")
@click.argument("obj1")
@click.argument("obj2")
@click.option("--name", "-n", default="Common")
@handle_error
def boolean_intersect(obj1, obj2, name):
    """Boolean intersection of two objects."""
    result = shape_mod.intersect(obj1, obj2, name)
    output(result)


# ── Feature Commands ────────────────────────────────────────────
@cli.group()
def feature():
    """Shape feature operations (extrude, revolve, fillet, etc.)."""
    pass


@feature.command("extrude")
@click.argument("obj_name")
@click.option("--length", "-l", type=float, default=10)
@click.option("--direction", "-d", type=click.Choice(["x", "y", "z"]), default="z")
@click.option("--name", "-n", default="Extrude")
@handle_error
def feature_extrude(obj_name, length, direction, name):
    """Extrude a shape along an axis."""
    result = shape_mod.extrude(obj_name, name, length, direction)
    output(result)


@feature.command("revolve")
@click.argument("obj_name")
@click.option("--axis", "-a", type=click.Choice(["x", "y", "z"]), default="z")
@click.option("--angle", type=float, default=360)
@click.option("--name", "-n", default="Revolve")
@handle_error
def feature_revolve(obj_name, axis, angle, name):
    """Revolve a shape around an axis."""
    result = shape_mod.revolve(obj_name, name, axis, angle)
    output(result)


@feature.command("fillet")
@click.argument("obj_name")
@click.option("--radius", "-r", type=float, default=1)
@click.option("--name", "-n", default="Fillet")
@handle_error
def feature_fillet(obj_name, radius, name):
    """Apply fillet (rounded edges)."""
    result = shape_mod.fillet(obj_name, radius, name)
    output(result)


@feature.command("chamfer")
@click.argument("obj_name")
@click.option("--distance", "-d", type=float, default=1)
@click.option("--name", "-n", default="Chamfer")
@handle_error
def feature_chamfer(obj_name, distance, name):
    """Apply chamfer (beveled edges)."""
    result = shape_mod.chamfer(obj_name, distance, name)
    output(result)


@feature.command("mirror")
@click.argument("obj_name")
@click.option("--plane", "-p", type=click.Choice(["xy", "xz", "yz"]), default="xy")
@click.option("--name", "-n", default="Mirror")
@handle_error
def feature_mirror(obj_name, plane, name):
    """Mirror an object across a plane."""
    result = shape_mod.mirror(obj_name, plane, name)
    output(result)


@feature.command("translate")
@click.argument("obj_name")
@click.option("--x", type=float, default=0)
@click.option("--y", type=float, default=0)
@click.option("--z", type=float, default=0)
@handle_error
def feature_translate(obj_name, x, y, z):
    """Move/translate an object."""
    result = shape_mod.translate(obj_name, x, y, z)
    output(result)


@feature.command("rotate")
@click.argument("obj_name")
@click.option("--axis", "-a", type=click.Choice(["x", "y", "z"]), default="z")
@click.option("--angle", type=float, default=45)
@click.option("--x", type=float, default=0, help="Center X")
@click.option("--y", type=float, default=0, help="Center Y")
@click.option("--z", type=float, default=0, help="Center Z")
@handle_error
def feature_rotate(obj_name, axis, angle, x, y, z):
    """Rotate an object around an axis."""
    result = shape_mod.rotate(obj_name, axis, angle, x, y, z)
    output(result)


@feature.command("scale")
@click.argument("obj_name")
@click.option("--factor", "-f", type=float, default=2.0)
@click.option("--name", "-n", default="Scale")
@handle_error
def feature_scale(obj_name, factor, name):
    """Scale an object uniformly."""
    result = shape_mod.scale(obj_name, factor, name)
    output(result)


# ── Export Commands ─────────────────────────────────────────────
@cli.group()
def export():
    """Export/import commands."""
    pass


@export.command("to")
@click.argument("output_path")
@click.option(
    "--object", "-o", "obj_name", default=None, help="Object name (all if omitted)"
)
@click.option("--format", "-f", "fmt", default=None, help="Output format")
@handle_error
def export_to(output_path, obj_name, fmt):
    """Export objects to STEP, STL, OBJ, BREP, SVG, DXF, etc."""
    result = export_mod.export_shape(output_path, obj_name, fmt)
    output(result)


@export.command("all")
@click.argument("output_dir")
@click.option(
    "--format", "-f", "formats_str", default="step,stl", help="Comma-separated formats"
)
@handle_error
def export_all(output_dir, formats_str):
    """Export all objects to multiple formats."""
    formats_list = [f.strip() for f in formats_str.split(",")]
    result = export_mod.export_all(output_dir, formats_list)
    output(result)


@export.command("formats")
@handle_error
def export_formats():
    """List supported export/import formats."""
    result = export_mod.formats()
    output(result)


# ── Measure Commands ────────────────────────────────────────────
@cli.group()
def measure():
    """Measurement and analysis commands."""
    pass


@measure.command("properties")
@click.argument("obj_name")
@handle_error
def measure_properties(obj_name):
    """Get all properties of an object."""
    result = measure_mod.properties(obj_name)
    output(result)


@measure.command("distance")
@click.argument("obj1")
@click.argument("obj2")
@handle_error
def measure_distance(obj1, obj2):
    """Measure distance between two objects."""
    result = measure_mod.distance(obj1, obj2)
    output(result)


@measure.command("volume")
@click.argument("obj_name")
@handle_error
def measure_volume(obj_name):
    """Get volume of an object."""
    result = measure_mod.volume(obj_name)
    output(result)


@measure.command("area")
@click.argument("obj_name")
@handle_error
def measure_area(obj_name):
    """Get surface area of an object."""
    result = measure_mod.area(obj_name)
    output(result)


@measure.command("center")
@click.argument("obj_name")
@handle_error
def measure_center(obj_name):
    """Get center of mass of an object."""
    result = measure_mod.center_of_mass(obj_name)
    output(result)


@measure.command("bbox")
@click.argument("obj_name")
@handle_error
def measure_bbox(obj_name):
    """Get bounding box of an object."""
    result = measure_mod.bounding_box(obj_name)
    output(result)


@measure.command("check")
@click.argument("obj_name")
@handle_error
def measure_check(obj_name):
    """Check shape validity and report issues."""
    result = measure_mod.check_validity(obj_name)
    output(result)


# ── Mesh Commands ───────────────────────────────────────────────
@cli.group()
def mesh():
    """Mesh operation commands."""
    pass


@mesh.command("tessellate")
@click.argument("obj_name")
@click.option("--tolerance", "-t", type=float, default=0.1)
@click.option("--name", "-n", default="Mesh")
@handle_error
def mesh_tessellate(obj_name, tolerance, name):
    """Convert a solid shape to a mesh."""
    result = mesh_mod.from_shape(obj_name, tolerance, name)
    output(result)


@mesh.command("decimate")
@click.argument("obj_name")
@click.option("--reduction", "-r", type=float, default=0.5, help="Target ratio (0-1)")
@click.option("--name", "-n", default="DecimatedMesh")
@handle_error
def mesh_decimate(obj_name, reduction, name):
    """Reduce mesh face count."""
    result = mesh_mod.decimate(obj_name, reduction, name)
    output(result)


@mesh.command("info")
@click.argument("obj_name")
@handle_error
def mesh_info(obj_name):
    """Get mesh/shape info."""
    result = mesh_mod.info(obj_name)
    output(result)


@mesh.command("repair")
@click.argument("obj_name")
@click.option("--name", "-n", default="RepairedMesh")
@handle_error
def mesh_repair(obj_name, name):
    """Repair a mesh (fix non-manifold, degenerate faces)."""
    result = mesh_mod.repair(obj_name, name)
    output(result)


# ── Session Commands ────────────────────────────────────────────
@cli.group()
def session():
    """Session management commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


# ── REPL ────────────────────────────────────────────────────────
@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.freecad.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("freecad", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "doc": "new|open|save|info|list|close",
        "shape": "box|cylinder|sphere|cone|torus|tube",
        "boolean": "fuse|cut|intersect",
        "feature": "extrude|revolve|fillet|chamfer|mirror|translate|rotate|scale",
        "export": "to|all|formats",
        "measure": "properties|distance|volume|area|center|bbox|check",
        "mesh": "tessellate|decimate|info|repair",
        "session": "status|undo|redo|history",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry Point ──────────────────────────────────────────────────
def main():
    cli()


if __name__ == "__main__":
    main()
