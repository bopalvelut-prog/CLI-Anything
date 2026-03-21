"""E2E tests for FFmpeg CLI harness.

These tests require ffmpeg to be installed and in PATH.
They create temporary media files and verify real ffmpeg operations.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

# Add harness to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def _resolve_cli(name):
    """Resolve CLI binary path."""
    path = shutil.which(name)
    if path is None:
        raise unittest.SkipTest(f"{name} not found in PATH")
    return path


def _create_test_video(path, duration=2, size="320x240", color="blue"):
    """Create a test video using ffmpeg."""
    ffmpeg = _resolve_cli("ffmpeg")
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi",
        "-i", f"color={color}:s={size}:d={duration}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create test video: {result.stderr}")


def _create_test_audio(path, duration=2):
    """Create a test audio file using ffmpeg."""
    ffmpeg = _resolve_cli("ffmpeg")
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi",
        "-i", f"sine=frequency=440:duration={duration}",
        "-c:a", "aac",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create test audio: {result.stderr}")


class TestProbeE2E(unittest.TestCase):
    """E2E tests for probing operations."""

    @classmethod
    def setUpClass(cls):
        _resolve_cli("ffmpeg")
        cls.tmpdir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.tmpdir, "test.mp4")
        _create_test_video(cls.test_video)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_probe_streams(self):
        from cli_anything.ffmpeg.core.probe import probe_streams
        streams = probe_streams(self.test_video)
        self.assertIsInstance(streams, list)
        self.assertGreater(len(streams), 0)
        self.assertEqual(streams[0].get("codec_type"), "video")

    def test_probe_format(self):
        from cli_anything.ffmpeg.core.probe import probe_format
        fmt = probe_format(self.test_video)
        self.assertIn("format_name", fmt)
        self.assertIn("duration", fmt)

    def test_probe_duration(self):
        from cli_anything.ffmpeg.core.probe import probe_duration
        duration = probe_duration(self.test_video)
        self.assertGreater(duration, 0)
        self.assertAlmostEqual(duration, 2.0, delta=0.5)

    def test_probe_codecs(self):
        from cli_anything.ffmpeg.core.probe import probe_codecs
        codecs = probe_codecs(self.test_video)
        self.assertIsInstance(codecs, list)
        codec_types = [c["type"] for c in codecs]
        self.assertIn("video", codec_types)

    def test_probe_summary(self):
        from cli_anything.ffmpeg.core.probe import summary
        info = summary(self.test_video)
        self.assertEqual(info["video_streams"], 1)
        self.assertIn("video", info)


class TestTranscodeE2E(unittest.TestCase):
    """E2E tests for transcoding operations."""

    @classmethod
    def setUpClass(cls):
        _resolve_cli("ffmpeg")
        cls.tmpdir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.tmpdir, "test.mp4")
        _create_test_video(cls.test_video)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_convert_basic(self):
        from cli_anything.ffmpeg.core.transcode import convert
        output = os.path.join(self.tmpdir, "converted.mp4")
        result = convert(self.test_video, output, video_codec="libx264")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))

    def test_convert_with_crf(self):
        from cli_anything.ffmpeg.core.transcode import convert
        output = os.path.join(self.tmpdir, "crf.mp4")
        result = convert(self.test_video, output, video_codec="libx264", crf=28)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))

    def test_convert_with_preset(self):
        from cli_anything.ffmpeg.core.transcode import convert_with_preset
        output = os.path.join(self.tmpdir, "preset.mp4")
        result = convert_with_preset(self.test_video, output, "web-hd")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))


class TestFilterE2E(unittest.TestCase):
    """E2E tests for filter operations."""

    @classmethod
    def setUpClass(cls):
        _resolve_cli("ffmpeg")
        cls.tmpdir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.tmpdir, "test.mp4")
        _create_test_video(cls.test_video)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_scale_filter(self):
        from cli_anything.ffmpeg.core.filter import apply_video_filter
        output = os.path.join(self.tmpdir, "scaled.mp4")
        result = apply_video_filter(self.test_video, output, "scale=160:120")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))

    def test_volume_filter(self):
        from cli_anything.ffmpeg.core.filter import apply_audio_filter
        input_audio = os.path.join(self.tmpdir, "test_audio.m4a")
        _create_test_audio(input_audio)
        output = os.path.join(self.tmpdir, "volume.m4a")
        result = apply_audio_filter(input_audio, output, "volume=0.5")
        self.assertEqual(result["status"], "success")


class TestConcatE2E(unittest.TestCase):
    """E2E tests for concatenation operations."""

    @classmethod
    def setUpClass(cls):
        _resolve_cli("ffmpeg")
        cls.tmpdir = tempfile.mkdtemp()
        cls.video1 = os.path.join(cls.tmpdir, "part1.mp4")
        cls.video2 = os.path.join(cls.tmpdir, "part2.mp4")
        _create_test_video(cls.video1, duration=1)
        _create_test_video(cls.video2, duration=1)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_concat_join(self):
        from cli_anything.ffmpeg.core.concat import concat
        output = os.path.join(self.tmpdir, "joined.mp4")
        result = concat([self.video1, self.video2], output)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))

    def test_trim(self):
        from cli_anything.ffmpeg.core.concat import trim
        output = os.path.join(self.tmpdir, "trimmed.mp4")
        result = trim(self.video1, output, start="00:00:00", duration="0.5")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))


class TestExtractE2E(unittest.TestCase):
    """E2E tests for extraction operations."""

    @classmethod
    def setUpClass(cls):
        _resolve_cli("ffmpeg")
        cls.tmpdir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.tmpdir, "test.mp4")
        _create_test_video(cls.test_video)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_extract_audio(self):
        from cli_anything.ffmpeg.core.extract import extract_audio
        output = os.path.join(self.tmpdir, "audio.aac")
        result = extract_audio(self.test_video, output)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))

    def test_extract_video(self):
        from cli_anything.ffmpeg.core.extract import extract_video
        output = os.path.join(self.tmpdir, "video.mp4")
        result = extract_video(self.test_video, output)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))

    def test_extract_thumbnail(self):
        from cli_anything.ffmpeg.core.extract import extract_thumbnail
        output = os.path.join(self.tmpdir, "thumb.jpg")
        result = extract_thumbnail(self.test_video, output, time="00:00:01")
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(output))


class TestCLIIntegrationE2E(unittest.TestCase):
    """E2E tests for CLI integration."""

    @classmethod
    def setUpClass(cls):
        cls.ffmpeg_cli = _resolve_cli("ffmpeg")
        cls.tmpdir = tempfile.mkdtemp()
        cls.test_video = os.path.join(cls.tmpdir, "test.mp4")
        _create_test_video(cls.test_video)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_cli_probe_json(self):
        from click.testing import CliRunner
        from cli_anything.ffmpeg.ffmpeg_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["probe", "duration", self.test_video, "--json"])
        self.assertEqual(result.exit_code, 0)
        data = json.loads(result.output)
        self.assertIn("duration_seconds", data)
        self.assertGreater(data["duration_seconds"], 0)

    def test_cli_transcode_convert(self):
        from click.testing import CliRunner
        from cli_anything.ffmpeg.ffmpeg_cli import cli
        runner = CliRunner()
        output = os.path.join(self.tmpdir, "cli_converted.mp4")
        result = runner.invoke(cli, [
            "transcode", "convert", self.test_video,
            "-o", output, "--preset", "web-hd",
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(output))

    def test_cli_extract_thumbnail(self):
        from click.testing import CliRunner
        from cli_anything.ffmpeg.ffmpeg_cli import cli
        runner = CliRunner()
        output = os.path.join(self.tmpdir, "cli_thumb.jpg")
        result = runner.invoke(cli, [
            "extract", "thumbnail", self.test_video,
            "-o", output, "--time", "00:00:01",
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(output))


if __name__ == "__main__":
    unittest.main()
