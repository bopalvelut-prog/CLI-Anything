"""FreeCAD CLI - End-to-end tests (requires FreeCAD installed)."""

import pytest
import json
import os
import subprocess
import tempfile


def freecad_available():
    """Check if FreeCAD is installed."""
    for cmd in ["freecadcmd", "/usr/bin/freecadcmd"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, timeout=10)
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return False


requires_freecad = pytest.mark.skipif(
    not freecad_available(), reason="FreeCAD not installed"
)


@requires_freecad
class TestDocumentE2E:
    def test_create_document(self, tmp_path):
        from cli_anything.freecad.core.document import create, save

        result = create("TestDoc")
        assert result.get("status") == "success" or result.get("name") == "TestDoc"

    def test_create_box(self, tmp_path):
        from cli_anything.freecad.core.document import create
        from cli_anything.freecad.core.shapes import box

        create("TestDoc")
        result = box("TestBox", 20, 10, 5)
        assert result.get("status") == "success"
        assert result.get("volume_mm3") == pytest.approx(1000.0, rel=1e-3)


@requires_freecad
class TestShapesE2E:
    def test_cylinder(self):
        from cli_anything.freecad.core.document import create
        from cli_anything.freecad.core.shapes import cylinder

        create("TestCyl")
        result = cylinder("Cyl", radius=5, height=10)
        assert result.get("status") == "success"
        expected_vol = 3.14159 * 25 * 10  # pi * r^2 * h
        assert result.get("volume_mm3") == pytest.approx(expected_vol, rel=1e-2)

    def test_boolean_cut(self):
        from cli_anything.freecad.core.document import create
        from cli_anything.freecad.core.shapes import box, cylinder, cut

        create("TestBool")
        box("BaseBox", 20, 20, 10)
        cylinder("Hole", radius=3, height=12, x=10, y=10)
        result = cut("BaseBox", "Hole", "Bracket")
        assert result.get("status") == "success"
        assert result.get("volume_mm3") < 20 * 20 * 10


@requires_freecad
class TestExportE2E:
    def test_export_step(self, tmp_path):
        from cli_anything.freecad.core.document import create
        from cli_anything.freecad.core.shapes import box
        from cli_anything.freecad.core.export import export_shape

        create("TestExport")
        box("Box", 10, 10, 10)
        out = str(tmp_path / "test.step")
        result = export_shape(out)
        assert result.get("status") == "success"
        assert os.path.exists(out)
