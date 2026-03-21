"""VLC CLI - Media probing and info extraction."""

import json
import os
import re
import subprocess
from typing import Dict, Any, Optional


def _run_vlc(args: list, timeout: int = 30) -> tuple:
    """Run a VLC command and return (stdout, stderr, returncode)."""
    cmd = ["vlc"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        raise RuntimeError("VLC not found. Install with: apt install vlc")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"VLC command timed out after {timeout}s")


def _run_cvlc(args: list, timeout: int = 30) -> tuple:
    """Run cvlc (console VLC) and return (stdout, stderr, returncode)."""
    cmd = ["cvlc"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        raise RuntimeError("cvlc not found. Install with: apt install vlc")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"cvlc command timed out after {timeout}s")


def probe(path: str) -> Dict[str, Any]:
    """Probe a media file and return structured info.

    Uses VLC's --sout '#transcode{}' trick and stderr parsing
    to extract codec, duration, resolution, etc.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    abs_path = os.path.abspath(path)
    file_size = os.path.getsize(abs_path)

    # Use vlc --verbose to get media info from stderr
    stdout, stderr, rc = _run_vlc(
        [
            "--verbose",
            "2",
            "--no-audio",
            "--no-video",
            "--run-time",
            "1",
            "--play-and-exit",
            abs_path,
        ],
        timeout=10,
    )

    info = {
        "path": abs_path,
        "filename": os.path.basename(abs_path),
        "size_bytes": file_size,
        "size_human": _human_size(file_size),
    }

    # Parse codec info from stderr
    info.update(_parse_vlc_stderr(stderr))

    # Extract extension-based format hint
    ext = os.path.splitext(abs_path)[1].lower().lstrip(".")
    info["container"] = ext

    return info


def _parse_vlc_stderr(stderr: str) -> Dict[str, Any]:
    """Parse VLC verbose output for media information."""
    info = {}

    # Duration
    dur_match = re.search(r"duration:\s*(\d+)", stderr)
    if dur_match:
        info["duration_ms"] = int(dur_match.group(1))

    # Video codec
    vcodec_match = re.search(r"fourcc:\s*(\w+)", stderr)
    if vcodec_match:
        info["video_codec"] = vcodec_match.group(1)

    # Audio codec
    acodec_match = re.search(r"fourcc:\s*(\w+)", stderr)
    if acodec_match:
        info["audio_codec"] = acodec_match.group(1)

    # Resolution from demux
    res_match = re.search(r"(\d{2,5})\s*x\s*(\d{2,5})", stderr)
    if res_match:
        info["width"] = int(res_match.group(1))
        info["height"] = int(res_match.group(2))

    # Frame rate
    fps_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:fps|f/s|t/s)", stderr)
    if fps_match:
        info["fps"] = float(fps_match.group(1))

    # Sample rate
    sr_match = re.search(r"(\d{4,6})\s*Hz", stderr)
    if sr_match:
        info["sample_rate"] = int(sr_match.group(1))

    # Channels
    ch_match = re.search(r"(\d)\s*channels?", stderr)
    if ch_match:
        info["channels"] = int(ch_match.group(1))

    # Bitrate
    br_match = re.search(r"bitrate:\s*(\d+)", stderr)
    if br_match:
        info["bitrate"] = int(br_match.group(1))

    return info


def _human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def formats() -> Dict[str, Any]:
    """List supported input/output formats."""
    return {
        "input": {
            "video": [
                "mp4",
                "mkv",
                "avi",
                "mov",
                "wmv",
                "flv",
                "webm",
                "m4v",
                "ts",
                "vob",
                "ogv",
                "3gp",
            ],
            "audio": [
                "mp3",
                "ogg",
                "flac",
                "wav",
                "aac",
                "wma",
                "m4a",
                "opus",
                "aiff",
                "ac3",
            ],
            "stream": ["http", "https", "rtsp", "rtmp", "udp", "rtp", "mms"],
            "disc": ["dvd", "vcd", "cdda", "bluray"],
        },
        "output": {
            "video": ["mp4", "mkv", "avi", "webm", "ts", "flv", "ogg"],
            "audio": ["mp3", "ogg", "flac", "wav", "aac", "opus"],
        },
        "transcode_profiles": [
            "mp4-h264-aac",
            "mp4-h265-aac",
            "mkv-h264-aac",
            "webm-vp8-vorbis",
            "webm-vp9-opus",
            "ts-h264-aac",
            "ogg-theora-vorbis",
            "mp3-128k",
            "mp3-192k",
            "mp3-320k",
            "ogg-vorbis-q6",
            "flac-lossless",
            "wav-pcm",
        ],
    }
