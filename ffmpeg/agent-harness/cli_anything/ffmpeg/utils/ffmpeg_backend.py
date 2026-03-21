"""FFmpeg backend wrapper.

Subprocess wrapper for ffmpeg and ffprobe executables.
Handles argument construction, execution, progress parsing, and error handling.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


class FFmpegError(Exception):
    """FFmpeg execution error."""

    def __init__(self, message: str, stderr: str = "", returncode: int = 1):
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


class FFmpegNotFoundError(FFmpegError):
    """FFmpeg binary not found."""

    def __init__(self):
        super().__init__(
            "ffmpeg not found. Install it with:\n"
            "  Ubuntu/Debian: sudo apt install ffmpeg\n"
            "  macOS: brew install ffmpeg\n"
            "  Windows: download from https://ffmpeg.org/download.html"
        )


@dataclass
class ProgressInfo:
    """Progress information from ffmpeg."""

    time: str = ""
    time_seconds: float = 0.0
    frame: int = 0
    fps: float = 0.0
    bitrate: str = ""
    speed: str = ""
    size: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "time_seconds": self.time_seconds,
            "frame": self.frame,
            "fps": self.fps,
            "bitrate": self.bitrate,
            "speed": self.speed,
            "size": self.size,
        }


@dataclass
class FFmpegResult:
    """Result of an ffmpeg/ffprobe execution."""

    success: bool
    returncode: int
    stdout: str
    stderr: str
    command: List[str]
    output_file: Optional[str] = None
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "success" if self.success else "error",
            "returncode": self.returncode,
            "command": " ".join(self.command),
            "output_file": self.output_file,
            "duration_seconds": round(self.duration_seconds, 3),
            "stderr_summary": self.stderr[-500:] if self.stderr else "",
        }


def _find_ffmpeg() -> str:
    """Find ffmpeg binary path."""
    path = shutil.which("ffmpeg")
    if path is None:
        raise FFmpegNotFoundError()
    return path


def _find_ffprobe() -> str:
    """Find ffprobe binary path."""
    path = shutil.which("ffprobe")
    if path is None:
        raise FFmpegNotFoundError()
    return path


def _parse_time_to_seconds(time_str: str) -> float:
    """Parse HH:MM:SS.ms to seconds."""
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        else:
            return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


_PROGRESS_RE = re.compile(
    r"frame=\s*(\d+)\s+fps=\s*([\d.]+)\s+q=[\d.-]+\s+(?:L?size=\s*(\S+)\s+)?time=\s*(\S+)\s+bitrate=\s*(\S+)\s+speed=\s*(\S+)"
)


def parse_progress_line(line: str) -> Optional[ProgressInfo]:
    """Parse a progress line from ffmpeg stderr."""
    line = line.strip()
    if not line:
        return None

    match = _PROGRESS_RE.search(line)
    if not match:
        return None

    frame, fps, size, time_str, bitrate, speed = match.groups()
    info = ProgressInfo(
        time=time_str,
        time_seconds=_parse_time_to_seconds(time_str),
        frame=int(frame),
        fps=float(fps),
        bitrate=bitrate,
        speed=speed,
        size=size or "",
    )
    return info


def run_ffmpeg(
    args: List[str],
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
    timeout: Optional[int] = None,
) -> FFmpegResult:
    """Run ffmpeg with given arguments.

    Args:
        args: Arguments to pass to ffmpeg (excluding 'ffmpeg' itself).
        progress_callback: Optional callback for progress updates.
        timeout: Optional timeout in seconds.

    Returns:
        FFmpegResult with execution details.

    Raises:
        FFmpegNotFoundError: If ffmpeg is not installed.
        FFmpegError: If ffmpeg fails and no error handling is done.
    """
    ffmpeg_bin = _find_ffmpeg()
    cmd = [ffmpeg_bin] + args
    start_time = _monotonic_time()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        stderr_lines = []
        last_progress = None

        for line in process.stderr:
            stderr_lines.append(line)
            if progress_callback:
                progress = parse_progress_line(line)
                if progress:
                    last_progress = progress
                    progress_callback(progress)

        process.wait(timeout=timeout)
        stderr = "".join(stderr_lines)
        duration = _monotonic_time() - start_time

        # Find output file from args
        output_file = None
        for i, arg in enumerate(args):
            if arg == "-i" and i + 1 < len(args):
                continue
            if not arg.startswith("-") and i > 0 and args[i - 1] != "-i":
                output_file = arg

        success = process.returncode == 0
        return FFmpegResult(
            success=success,
            returncode=process.returncode,
            stdout="",
            stderr=stderr,
            command=cmd,
            output_file=output_file,
            duration_seconds=duration,
        )

    except subprocess.TimeoutExpired:
        process.kill()
        raise FFmpegError(f"ffmpeg timed out after {timeout} seconds")
    except FileNotFoundError:
        raise FFmpegNotFoundError()


def run_ffprobe(
    args: List[str],
    timeout: Optional[int] = 30,
) -> FFmpegResult:
    """Run ffprobe with given arguments.

    Args:
        args: Arguments to pass to ffprobe.
        timeout: Optional timeout in seconds.

    Returns:
        FFmpegResult with stdout containing the output.
    """
    ffprobe_bin = _find_ffprobe()
    cmd = [ffprobe_bin] + args
    start_time = _monotonic_time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = _monotonic_time() - start_time

        return FFmpegResult(
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            command=cmd,
            duration_seconds=duration,
        )

    except subprocess.TimeoutExpired:
        raise FFmpegError(f"ffprobe timed out after {timeout} seconds")
    except FileNotFoundError:
        raise FFmpegNotFoundError()


def probe_json(input_file: str) -> Dict[str, Any]:
    """Probe a media file and return JSON metadata.

    Args:
        input_file: Path to the media file.

    Returns:
        Dict with format and stream information.
    """
    result = run_ffprobe([
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        input_file,
    ])

    if not result.success:
        raise FFmpegError(
            f"Failed to probe {input_file}: {result.stderr}",
            result.stderr,
            result.returncode,
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise FFmpegError(f"Failed to parse ffprobe JSON output: {e}")


def get_version() -> str:
    """Get ffmpeg version string."""
    try:
        result = run_ffmpeg(["-version"])
        if result.stderr:
            first_line = result.stderr.split("\n")[0]
            return first_line
        return "unknown"
    except FFmpegError:
        return "unknown"


def get_codecs() -> List[Dict[str, str]]:
    """Get list of available codecs."""
    result = run_ffprobe(["-codecs", "-v", "quiet"])
    if not result.stdout:
        return []

    codecs = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line or line.startswith("------") or line.startswith("Codecs"):
            continue
        # Parse codec line: flags codec name description
        parts = line.split(None, 3)
        if len(parts) >= 3:
            flags = parts[0]
            codec_name = parts[1]
            description = parts[2] if len(parts) == 3 else parts[3]
            codecs.append({
                "name": codec_name,
                "flags": flags,
                "description": description,
                "decoding": "D" in flags,
                "encoding": "E" in flags,
                "video": "V" in flags,
                "audio": "A" in flags,
                "subtitle": "S" in flags,
            })

    return codecs


def get_formats() -> List[Dict[str, str]]:
    """Get list of available formats/muxers."""
    result = run_ffprobe(["-formats", "-v", "quiet"])
    if not result.stdout:
        return []

    formats = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line or line.startswith("--") or line.startswith("File"):
            continue
        parts = line.split(None, 2)
        if len(parts) >= 2:
            flags = parts[0]
            name = parts[1]
            description = parts[2] if len(parts) > 2 else ""
            formats.append({
                "name": name,
                "flags": flags,
                "description": description,
                "demuxing": "D" in flags,
                "muxing": "E" in flags,
            })

    return formats


def get_filters() -> List[Dict[str, str]]:
    """Get list of available filters."""
    result = run_ffprobe(["-filters", "-v", "quiet"])
    if not result.stdout:
        return []

    filters = []
    for line in result.stdout.split("\n"):
        line = line.strip()
        if not line or line.startswith("--") or line.startswith("Filters"):
            continue
        parts = line.split(None, 3)
        if len(parts) >= 3:
            flags = parts[0]
            name = parts[1]
            description = parts[2] if len(parts) == 3 else parts[3]
            filters.append({
                "name": name,
                "flags": flags,
                "description": description,
                "timeline": "T" in flags,
                "slice": "S" in flags,
            })

    return filters


def _monotonic_time() -> float:
    """Get monotonic time for duration measurement."""
    if sys.version_info >= (3, 7):
        import time
        return time.monotonic()
    else:
        import time
        return time.time()


# Preset definitions
PRESETS = {
    "web-hd": {
        "description": "Web-optimized HD (1080p H.264)",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "crf": 23,
        "preset": "medium",
        "resolution": "1920x1080",
    },
    "web-4k": {
        "description": "Web-optimized 4K (H.264)",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "crf": 23,
        "preset": "slow",
        "resolution": "3840x2160",
    },
    "web-hd-h265": {
        "description": "Web-optimized HD (1080p H.265/HEVC)",
        "video_codec": "libx265",
        "audio_codec": "aac",
        "crf": 28,
        "preset": "medium",
        "resolution": "1920x1080",
    },
    "gif": {
        "description": "Animated GIF",
        "video_codec": "gif",
        "audio_codec": None,
        "fps": 15,
        "resolution": "480x-1",
    },
    "audio-only": {
        "description": "Extract audio as AAC",
        "video_codec": None,
        "audio_codec": "aac",
        "audio_bitrate": "192k",
    },
    "mp3": {
        "description": "Extract audio as MP3",
        "video_codec": None,
        "audio_codec": "libmp3lame",
        "audio_bitrate": "192k",
    },
    "thumbnail": {
        "description": "Extract single frame as JPEG",
        "video_codec": "mjpeg",
        "audio_codec": None,
        "frames": 1,
    },
    "copy": {
        "description": "Stream copy (no re-encoding)",
        "video_codec": "copy",
        "audio_codec": "copy",
    },
}


def get_preset(name: str) -> Optional[Dict[str, Any]]:
    """Get a preset by name."""
    return PRESETS.get(name)


def list_presets() -> List[Dict[str, str]]:
    """List all available presets."""
    return [
        {"name": name, "description": preset["description"]}
        for name, preset in PRESETS.items()
    ]


def preset_to_args(preset_name: str) -> List[str]:
    """Convert a preset to ffmpeg arguments.

    Args:
        preset_name: Name of the preset.

    Returns:
        List of ffmpeg arguments.

    Raises:
        FFmpegError: If preset not found.
    """
    preset = PRESETS.get(preset_name)
    if preset is None:
        raise FFmpegError(f"Unknown preset: {preset_name}. Available: {', '.join(PRESETS.keys())}")

    args = []

    # Video codec
    if preset.get("video_codec"):
        args.extend(["-c:v", preset["video_codec"]])
    elif preset.get("video_codec") is None and "audio_codec" in preset:
        args.extend(["-vn"])

    # Audio codec
    if preset.get("audio_codec"):
        args.extend(["-c:a", preset["audio_codec"]])
    elif preset.get("audio_codec") is None and "video_codec" in preset:
        args.extend(["-an"])

    # CRF
    if "crf" in preset:
        args.extend(["-crf", str(preset["crf"])])

    # Encoding preset
    if "preset" in preset:
        args.extend(["-preset", preset["preset"]])

    # Resolution
    if "resolution" in preset:
        w, h = preset["resolution"].split("x")
        if h == "-1":
            args.extend(["-vf", f"scale={w}:-1"])
        else:
            args.extend(["-s", preset["resolution"]])

    # FPS
    if "fps" in preset:
        args.extend(["-r", str(preset["fps"])])

    # Audio bitrate
    if "audio_bitrate" in preset:
        args.extend(["-b:a", preset["audio_bitrate"]])

    # Frame count
    if "frames" in preset:
        args.extend(["-frames:v", str(preset["frames"])])

    return args
