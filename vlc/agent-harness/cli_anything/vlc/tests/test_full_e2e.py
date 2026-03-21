"""VLC CLI - End-to-end tests (requires VLC installed)."""

import pytest
import json
import os
import subprocess
import tempfile


def vlc_available():
    """Check if VLC is installed."""
    try:
        result = subprocess.run(["vlc", "--version"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


requires_vlc = pytest.mark.skipif(not vlc_available(), reason="VLC not installed")


@pytest.fixture
def sample_audio(tmp_path):
    """Generate a short test WAV file using sox or ffmpeg."""
    path = str(tmp_path / "test.wav")
    try:
        subprocess.run(
            ["sox", "-n", "-r", "44100", "-c", "2", path, "synth", "2", "sine", "440"],
            capture_output=True,
            timeout=10,
        )
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=2",
                "-ar",
                "44100",
                path,
            ],
            capture_output=True,
            timeout=10,
        )
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    pytest.skip("Neither sox nor ffmpeg available for test audio generation")


@requires_vlc
class TestProbeE2E:
    def test_probe_wav(self, sample_audio):
        from cli_anything.vlc.core.probe import probe

        info = probe(sample_audio)
        assert info["path"].endswith(".wav")
        assert info["size_bytes"] > 0

    def test_formats(self):
        from cli_anything.vlc.core.probe import formats

        fmts = formats()
        assert len(fmts["transcode_profiles"]) >= 10


@requires_vlc
class TestTranscodeE2E:
    def test_convert_audio(self, sample_audio, tmp_path):
        from cli_anything.vlc.core.transcode import convert

        out = str(tmp_path / "output.mp3")
        result = convert(sample_audio, out, profile="mp3-128k")
        assert result["status"] == "success"
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0


@requires_vlc
class TestPlaylistE2E:
    def test_create_and_parse(self, tmp_path):
        from cli_anything.vlc.core.playlist import create_playlist, parse_playlist

        # Create dummy files
        f1 = str(tmp_path / "a.txt")
        f2 = str(tmp_path / "b.txt")
        open(f1, "w").close()
        open(f2, "w").close()

        pl_path = str(tmp_path / "test.m3u")
        result = create_playlist([f1, f2], pl_path, title="Test")
        assert result["status"] == "success"
        assert result["tracks"] == 2

        parsed = parse_playlist(pl_path)
        assert parsed["count"] == 2
        assert parsed["title"] == "Test"
