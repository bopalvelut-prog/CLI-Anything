"""Unit tests for FFmpeg CLI harness.

Tests use mocked subprocess calls to verify argument construction
and output parsing without requiring ffmpeg to be installed.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Add harness to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cli_anything.ffmpeg.utils.ffmpeg_backend import (
    FFmpegError,
    FFmpegNotFoundError,
    FFmpegResult,
    ProgressInfo,
    _parse_time_to_seconds,
    parse_progress_line,
    preset_to_args,
    list_presets,
    get_preset,
    PRESETS,
)


class TestTimeParsing(unittest.TestCase):
    """Test time string parsing."""

    def test_parse_hhmmss(self):
        self.assertAlmostEqual(_parse_time_to_seconds("01:30:45"), 5445.0)

    def test_parse_mmss(self):
        self.assertAlmostEqual(_parse_time_to_seconds("02:30"), 150.0)

    def test_parse_seconds(self):
        self.assertAlmostEqual(_parse_time_to_seconds("90.5"), 90.5)

    def test_parse_invalid(self):
        self.assertEqual(_parse_time_to_seconds("invalid"), 0.0)


class TestProgressParsing(unittest.TestCase):
    """Test ffmpeg progress line parsing."""

    def test_parse_valid_progress(self):
        line = "frame=  120 fps=30.0 q=28.0 size=    512kB time=00:00:04.00 bitrate=1048.6kbits/s speed=1.01x"
        info = parse_progress_line(line)
        self.assertIsNotNone(info)
        self.assertEqual(info.frame, 120)
        self.assertAlmostEqual(info.fps, 30.0)
        self.assertEqual(info.time, "00:00:04.00")
        self.assertAlmostEqual(info.time_seconds, 4.0)
        self.assertEqual(info.speed, "1.01x")

    def test_parse_empty_line(self):
        self.assertIsNone(parse_progress_line(""))

    def test_parse_non_progress_line(self):
        self.assertIsNone(parse_progress_line("Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'test.mp4':"))

    def test_progress_to_dict(self):
        info = ProgressInfo(
            time="00:01:00.00",
            time_seconds=60.0,
            frame=1800,
            fps=30.0,
            bitrate="2000k",
            speed="1.0x",
            size="15000kB",
        )
        d = info.to_dict()
        self.assertEqual(d["time"], "00:01:00.00")
        self.assertEqual(d["frame"], 1800)
        self.assertAlmostEqual(d["time_seconds"], 60.0)


class TestPresets(unittest.TestCase):
    """Test preset handling."""

    def test_list_presets(self):
        presets = list_presets()
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)
        names = [p["name"] for p in presets]
        self.assertIn("web-hd", names)
        self.assertIn("gif", names)
        self.assertIn("audio-only", names)

    def test_get_preset(self):
        preset = get_preset("web-hd")
        self.assertIsNotNone(preset)
        self.assertEqual(preset["video_codec"], "libx264")

    def test_get_nonexistent_preset(self):
        self.assertIsNone(get_preset("nonexistent"))

    def test_preset_to_args_web_hd(self):
        args = preset_to_args("web-hd")
        self.assertIn("-c:v", args)
        self.assertIn("libx264", args)
        self.assertIn("-c:a", args)
        self.assertIn("aac", args)
        self.assertIn("-crf", args)

    def test_preset_to_args_gif(self):
        args = preset_to_args("gif")
        self.assertIn("-c:v", args)
        self.assertIn("gif", args)
        self.assertIn("-r", args)

    def test_preset_to_args_audio_only(self):
        args = preset_to_args("audio-only")
        self.assertIn("-vn", args)
        self.assertIn("-c:a", args)
        self.assertIn("aac", args)

    def test_preset_to_args_copy(self):
        args = preset_to_args("copy")
        self.assertIn("-c:v", args)
        self.assertIn("copy", args)
        self.assertIn("-c:a", args)

    def test_preset_to_args_invalid(self):
        with self.assertRaises(FFmpegError):
            preset_to_args("nonexistent")


class TestFFmpegResult(unittest.TestCase):
    """Test FFmpegResult."""

    def test_success_to_dict(self):
        result = FFmpegResult(
            success=True,
            returncode=0,
            stdout="",
            stderr="",
            command=["ffmpeg", "-i", "test.mp4"],
            output_file="out.mp4",
            duration_seconds=1.5,
        )
        d = result.to_dict()
        self.assertEqual(d["status"], "success")
        self.assertEqual(d["output_file"], "out.mp4")
        self.assertAlmostEqual(d["duration_seconds"], 1.5)

    def test_error_to_dict(self):
        result = FFmpegResult(
            success=False,
            returncode=1,
            stdout="",
            stderr="Error message",
            command=["ffmpeg", "-i", "bad.mp4"],
        )
        d = result.to_dict()
        self.assertEqual(d["status"], "error")


class TestFilterModule(unittest.TestCase):
    """Test filter module."""

    def test_list_filters(self):
        from cli_anything.ffmpeg.core.filter import list_filters
        filters = list_filters()
        self.assertIsInstance(filters, list)
        names = [f["name"] for f in filters]
        self.assertIn("scale", names)
        self.assertIn("volume", names)

    def test_list_video_filters(self):
        from cli_anything.ffmpeg.core.filter import list_filters
        filters = list_filters("video")
        for f in filters:
            self.assertEqual(f["type"], "video")

    def test_list_audio_filters(self):
        from cli_anything.ffmpeg.core.filter import list_filters
        filters = list_filters("audio")
        for f in filters:
            self.assertEqual(f["type"], "audio")

    def test_build_scale_filter(self):
        from cli_anything.ffmpeg.core.filter import build_filter
        result = build_filter("scale", width="1280", height="720")
        self.assertEqual(result, "scale=1280:720")

    def test_build_volume_filter(self):
        from cli_anything.ffmpeg.core.filter import build_filter
        result = build_filter("volume", level="1.5", filter_type="audio")
        self.assertEqual(result, "volume=1.5")

    def test_build_unknown_filter(self):
        from cli_anything.ffmpeg.core.filter import build_filter
        with self.assertRaises(FFmpegError):
            build_filter("nonexistent")


class TestSession(unittest.TestCase):
    """Test session management."""

    def test_record_and_history(self):
        from cli_anything.ffmpeg.core.session import Session
        sess = Session()
        sess.record("convert", {"input": "a.mp4", "output": "b.mp4"})
        history = sess.history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], "convert")

    def test_undo_redo(self):
        from cli_anything.ffmpeg.core.session import Session
        sess = Session()
        sess.record("convert", {"input": "a.mp4"})
        sess.record("trim", {"input": "b.mp4"})

        undone = sess.undo()
        self.assertEqual(undone.action, "trim")
        self.assertEqual(len(sess.history()), 1)

        redone = sess.redo()
        self.assertEqual(redone.action, "trim")
        self.assertEqual(len(sess.history()), 2)

    def test_undo_empty(self):
        from cli_anything.ffmpeg.core.session import Session
        sess = Session()
        self.assertIsNone(sess.undo())

    def test_redo_empty(self):
        from cli_anything.ffmpeg.core.session import Session
        sess = Session()
        self.assertIsNone(sess.redo())

    def test_status(self):
        from cli_anything.ffmpeg.core.session import Session
        sess = Session()
        sess.record("test", {})
        status = sess.status()
        self.assertEqual(status["total_commands"], 1)
        self.assertTrue(status["undo_available"])
        self.assertFalse(status["redo_available"])

    def test_clear(self):
        from cli_anything.ffmpeg.core.session import Session
        sess = Session()
        sess.record("test", {})
        sess.clear()
        self.assertEqual(len(sess.history()), 0)

    def test_save_load(self):
        from cli_anything.ffmpeg.core.session import Session
        import tempfile
        sess = Session()
        sess.record("convert", {"input": "a.mp4"})

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            sess.save(path)
            sess2 = Session()
            sess2.load(path)
            self.assertEqual(len(sess2.history()), 1)
            self.assertEqual(sess2.history()[0]["action"], "convert")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
