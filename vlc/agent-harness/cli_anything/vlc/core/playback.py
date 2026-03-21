"""VLC CLI - Playback control via cvlc and rc interface."""

import os
import subprocess
import socket
import time
import json
from typing import Dict, Any, Optional


def _run_cvlc(
    args: list, timeout: int = 30, background: bool = False
) -> Dict[str, Any]:
    """Run cvlc with given args."""
    cmd = ["cvlc", "--no-color"] + args
    try:
        if background:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {"status": "started", "pid": proc.pid, "command": " ".join(cmd)}
        else:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            return {
                "status": "success" if result.returncode == 0 else "error",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
    except FileNotFoundError:
        raise RuntimeError("cvlc not found. Install with: apt install vlc")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"cvlc timed out after {timeout}s")


def play(
    input_path: str,
    start_time: Optional[str] = None,
    stop_time: Optional[str] = None,
    volume: Optional[int] = None,
    fullscreen: bool = False,
    loop: bool = False,
    no_video: bool = False,
    repeat: bool = False,
    rate: Optional[float] = None,
) -> Dict[str, Any]:
    """Play a media file with cvlc (one-shot, waits for completion)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    args = [os.path.abspath(input_path)]

    if start_time:
        args = ["--start-time", str(_parse_time(start_time))] + args
    if stop_time:
        args = ["--stop-time", str(_parse_time(stop_time))] + args
    if volume is not None:
        args = ["--volume", str(max(0, min(256, volume)))] + args
    if fullscreen:
        args = ["--fullscreen"] + args
    if loop:
        args = ["--loop"] + args
    if repeat:
        args = ["--repeat"] + args
    if no_video:
        args = ["--no-video"] + args
    if rate:
        args = ["--rate", str(rate)] + args

    args = ["--play-and-exit"] + args
    return _run_cvlc(args, timeout=3600)


def screenshot(
    input_path: str,
    output_path: str,
    time_offset: str = "0",
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Dict[str, Any]:
    """Take a screenshot of a video at a specific time."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    abs_in = os.path.abspath(input_path)
    abs_out = os.path.abspath(output_path)
    out_dir = os.path.dirname(abs_out) or "."
    out_name = os.path.splitext(os.path.basename(abs_out))[0]

    args = [
        abs_in,
        "--rate",
        "1",
        "--no-audio",
        "--video-filter",
        "scene",
        "--scene-format",
        "png",
        "--scene-path",
        out_dir,
        "--scene-prefix",
        out_name,
        "--scene-replace",
        "--scene-ratio",
        "1",
        "--start-time",
        str(_parse_time(time_offset)),
        "--stop-time",
        str(_parse_time(time_offset) + 1),
        "--play-and-exit",
        "vlc://quit",
    ]

    if width and height:
        args = ["--width", str(width), "--height", str(height)] + args

    result = _run_cvlc(args, timeout=15)

    # VLC names the file with prefix + sequential number
    expected = os.path.join(out_dir, f"{out_name}000001.png")
    if os.path.exists(expected):
        if expected != abs_out:
            os.rename(expected, abs_out)
        return {
            "status": "success",
            "output": abs_out,
            "time": time_offset,
            "width": width,
            "height": height,
        }

    # Try alternate naming
    for f in os.listdir(out_dir):
        if f.startswith(out_name) and f.endswith(".png"):
            src = os.path.join(out_dir, f)
            if src != abs_out:
                os.rename(src, abs_out)
            return {
                "status": "success",
                "output": abs_out,
                "time": time_offset,
            }

    return {
        "status": "error",
        "message": "Screenshot may have failed",
        "stderr": result.get("stderr", ""),
    }


def record(
    input_path: str,
    output_path: str,
    duration: Optional[str] = None,
    start_time: Optional[str] = None,
) -> Dict[str, Any]:
    """Record/trim a media file (extract a segment)."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    abs_in = os.path.abspath(input_path)
    abs_out = os.path.abspath(output_path)

    args = [abs_in, "--sout", f"#standard{{access=file,mux=ts,dst={abs_out}}}"]

    if start_time:
        args = ["--start-time", str(_parse_time(start_time))] + args
    if duration:
        args = ["--run-time", str(_parse_time(duration))] + args

    args = ["--play-and-exit"] + args
    result = _run_cvlc(args, timeout=3600)

    if os.path.exists(abs_out):
        return {
            "status": "success",
            "output": abs_out,
            "size_bytes": os.path.getsize(abs_out),
        }
    return {
        "status": "error",
        "message": "Recording failed",
        "stderr": result.get("stderr", ""),
    }


def _parse_time(t: str) -> float:
    """Parse time string to seconds. Supports 'HH:MM:SS', 'MM:SS', or plain seconds."""
    if ":" not in t:
        return float(t)
    parts = t.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(t)
