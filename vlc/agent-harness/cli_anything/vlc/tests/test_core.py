"""VLC CLI - Core unit tests (no real media files needed)."""

import pytest
import json
import os
import tempfile

from cli_anything.vlc.core.session import Session
from cli_anything.vlc.core.transcode import (
    TRANSCODE_PROFILES,
    list_profiles,
    get_profile,
    build_sout,
)
from cli_anything.vlc.core.probe import formats, _human_size, _parse_vlc_stderr


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


class TestTranscode:
    def test_list_profiles(self):
        profiles = list_profiles()
        assert len(profiles) >= 13
        names = [p["name"] for p in profiles]
        assert "mp4-h264-aac" in names
        assert "mp3-192k" in names
        assert "flac-lossless" in names

    def test_get_profile(self):
        p = get_profile("mp4-h264-aac")
        assert p["vcodec"] == "h264"
        assert p["extension"] == "mp4"

    def test_get_profile_unknown(self):
        with pytest.raises(ValueError):
            get_profile("nonexistent")

    def test_build_sout(self):
        sout = build_sout("mp4-h264-aac", "/tmp/out.mp4")
        assert "h264" in sout
        assert "/tmp/out.mp4" in sout

    def test_build_sout_with_overrides(self):
        sout = build_sout(
            "mp4-h264-aac",
            "/tmp/out.mp4",
            width=1280,
            height=720,
            vb_override="1000",
        )
        assert "width=1280" in sout
        assert "height=720" in sout
        assert "vb=1000" in sout


class TestProbe:
    def test_formats(self):
        fmts = formats()
        assert "input" in fmts
        assert "output" in fmts
        assert "mp4" in fmts["input"]["video"]
        assert "mp3" in fmts["input"]["audio"]

    def test_human_size(self):
        assert _human_size(512) == "512.0 B"
        assert _human_size(1024) == "1.0 KB"
        assert _human_size(1048576) == "1.0 MB"
        assert _human_size(1073741824) == "1.0 GB"

    def test_parse_vlc_stderr(self):
        stderr = (
            "main debug: fourcc: h264\nmain debug: 1920x1080\nmain debug: 1200000 t/s"
        )
        info = _parse_vlc_stderr(stderr)
        assert info.get("width") == 1920
        assert info.get("height") == 1080
