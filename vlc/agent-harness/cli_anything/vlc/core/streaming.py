"""VLC CLI - Streaming and network output."""

import os
import subprocess
import json
from typing import Dict, Any, Optional


def _run_cvlc(
    args: list, timeout: int = 3600, background: bool = False
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


def stream_file(
    input_path: str,
    port: int = 8080,
    mux: str = "ts",
    address: str = "0.0.0.0",
    ttl: int = 1,
) -> Dict[str, Any]:
    """Stream a file over HTTP/UDP."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    abs_in = os.path.abspath(input_path)

    # HTTP streaming
    sout = f"#standard{{access=http,mux={mux},dst={address}:{port}}}"
    args = [abs_in, "--sout", sout, "--repeat"]

    return _run_cvlc(args, background=True)


def stream_udp(
    input_path: str,
    address: str = "239.255.12.42",
    port: int = 1234,
    mux: str = "ts",
    ttl: int = 1,
) -> Dict[str, Any]:
    """Stream a file over UDP multicast."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    abs_in = os.path.abspath(input_path)
    sout = f"#standard{{access=udp,mux={mux},dst={address}:{port},ttl={ttl}}}"
    args = [abs_in, "--sout", sout, "--repeat"]

    return _run_cvlc(args, background=True)


def stream_rtp(
    input_path: str, address: str = "239.255.12.42", port: int = 5004, mux: str = "ts"
) -> Dict[str, Any]:
    """Stream a file over RTP."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    abs_in = os.path.abspath(input_path)
    sout = f"#rtp{{dst={address},port={port},mux={mux}}}"
    args = [abs_in, "--sout", sout, "--repeat"]

    return _run_cvlc(args, background=True)


def transcode_stream(
    input_path: str,
    port: int = 8080,
    profile: str = "mp4-h264-aac",
    address: str = "0.0.0.0",
) -> Dict[str, Any]:
    """Transcode and stream a file over HTTP."""
    from cli_anything.vlc.core.transcode import TRANSCODE_PROFILES

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    prof = TRANSCODE_PROFILES.get(profile)
    if not prof:
        raise ValueError(f"Unknown profile: {profile}")

    abs_in = os.path.abspath(input_path)
    vcodec = prof.get("vcodec", "h264")
    acodec = prof.get("acodec", "mp4a")
    vb = prof.get("vb", "2000")
    ab = prof.get("ab", "192")
    mux = prof.get("mux", "ts")

    no_video = ""
    if prof.get("no_video"):
        no_video = ",vcodec=none"

    sout = (
        f"#transcode{{vcodec={vcodec},vb={vb},acodec={acodec},ab={ab}{no_video}}}"
        f":standard{{access=http,mux={mux},dst={address}:{port}}}"
    )

    args = [abs_in, "--sout", sout, "--repeat"]
    return _run_cvlc(args, background=True)


def record_stream(
    url: str, output_path: str, duration: Optional[str] = None, mux: str = "ts"
) -> Dict[str, Any]:
    """Record a network stream to a file."""
    abs_out = os.path.abspath(output_path)

    sout = f"#standard{{access=file,mux={mux},dst={abs_out}}}"
    args = [url, "--sout", sout, "--play-and-exit"]

    if duration:
        args = ["--run-time", str(_parse_time(duration))] + args

    timeout = 3600
    if duration:
        timeout = int(_parse_time(duration)) + 30

    result = _run_cvlc(args, timeout=timeout)

    if os.path.exists(abs_out):
        return {
            "status": "success",
            "output": abs_out,
            "source": url,
            "size_bytes": os.path.getsize(abs_out),
        }
    return {
        "status": "error",
        "message": "Recording failed",
        "stderr": result.get("stderr", ""),
    }


def _parse_time(t: str) -> float:
    """Parse time string to seconds."""
    if ":" not in t:
        return float(t)
    parts = t.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    return float(t)
