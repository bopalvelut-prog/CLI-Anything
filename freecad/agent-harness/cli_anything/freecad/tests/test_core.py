"""FreeCAD CLI - Core unit tests (no FreeCAD required)."""

import pytest
import json
import os

from cli_anything.freecad.core.session import Session
from cli_anything.freecad.core.export import EXPORT_FORMATS, formats
from cli_anything.freecad.core.engine import wrap_script


class TestSession:
    def test_new_session(self):
        s = Session()
        assert not s.has_project()
        assert s.status()["has_project"] is False

    def test_set_project(self):
        s = Session()
        proj = {"name": "test", "metadata": {}}
        s.set_project(proj, "/tmp/test.json")
        assert s.has_project()
        assert s.status()["project_name"] == "test"

    def test_undo_redo(self):
        s = Session()
        proj = {"name": "v1", "metadata": {}}
        s.set_project(proj)
        s.snapshot("change name")
        s.project["name"] = "v2"
        desc = s.undo()
        assert s.project["name"] == "v1"
        desc = s.redo()
        assert s.project["name"] == "v2"

    def test_undo_empty(self):
        s = Session()
        proj = {"name": "test", "metadata": {}}
        s.set_project(proj)
        with pytest.raises(RuntimeError):
            s.undo()

    def test_history(self):
        s = Session()
        proj = {"name": "test", "metadata": {}}
        s.set_project(proj)
        s.snapshot("first")
        s.project["x"] = 1
        s.snapshot("second")
        s.project["x"] = 2
        history = s.list_history()
        assert len(history) == 2


class TestExportFormats:
    def test_all_formats_have_extension(self):
        for name, info in EXPORT_FORMATS.items():
            assert "ext" in info
            assert "desc" in info

    def test_formats_function(self):
        fmts = formats()
        assert "export" in fmts
        assert "import" in fmts
        assert "step" in fmts["export"]
        assert "stl" in fmts["export"]

    def test_step_in_formats(self):
        assert "step" in EXPORT_FORMATS
        assert EXPORT_FORMATS["step"]["ext"] == ".step"

    def test_stl_in_formats(self):
        assert "stl" in EXPORT_FORMATS
        assert EXPORT_FORMATS["stl"]["ext"] == ".stl"


class TestScriptEngine:
    def test_wrap_script(self):
        script = wrap_script('result = {"status": "ok"}')
        assert "import FreeCAD" in script
        assert "import Part" in script
        assert 'result = {"status": "ok"}' in script
        assert "json.dumps" in script

    def test_wrap_script_custom_output(self):
        script = wrap_script("x = 42", output_var="x")
        assert "print(json.dumps(x" in script
