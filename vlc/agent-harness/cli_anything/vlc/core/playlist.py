"""VLC CLI - Playlist management."""

import os
import json
import subprocess
from typing import Dict, Any, Optional, List


def create_playlist(
    files: list, output_path: str, title: Optional[str] = None
) -> Dict[str, Any]:
    """Create an M3U playlist file."""
    abs_out = os.path.abspath(output_path)

    entries = []
    for f in files:
        abs_f = os.path.abspath(f)
        if not os.path.exists(abs_f):
            raise FileNotFoundError(f"File not found: {f}")
        entries.append(abs_f)

    with open(abs_out, "w") as fh:
        fh.write("#EXTM3U\n")
        if title:
            fh.write(f"#PLAYLIST:{title}\n")
        for entry in entries:
            name = os.path.splitext(os.path.basename(entry))[0]
            fh.write(f"#EXTINF:-1,{name}\n")
            fh.write(f"{entry}\n")

    return {
        "status": "success",
        "output": abs_out,
        "tracks": len(entries),
        "title": title or os.path.splitext(os.path.basename(abs_out))[0],
    }


def parse_playlist(path: str) -> Dict[str, Any]:
    """Parse an M3U/M3U8 playlist and return track info."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {path}")

    tracks = []
    title = None
    current_info = None

    with open(abs_path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#EXTM3U"):
                continue
            if line.startswith("#PLAYLIST:"):
                title = line[10:]
                continue
            if line.startswith("#EXTINF:"):
                info_str = line[8:]
                parts = info_str.split(",", 1)
                duration = parts[0].strip()
                name = parts[1].strip() if len(parts) > 1 else None
                current_info = {
                    "duration": int(duration)
                    if duration.lstrip("-").isdigit()
                    else None,
                    "name": name,
                }
                continue
            if line.startswith("#"):
                continue
            # This is a file path or URL
            track = {
                "path": line,
                "filename": os.path.basename(line),
                "exists": os.path.exists(line),
            }
            if current_info:
                track.update(current_info)
                current_info = None
            tracks.append(track)

    return {
        "path": abs_path,
        "title": title,
        "tracks": tracks,
        "count": len(tracks),
    }


def play_playlist(
    playlist_path: str,
    random: bool = False,
    loop: bool = False,
    repeat: bool = False,
    start_index: Optional[int] = None,
) -> Dict[str, Any]:
    """Play a playlist with cvlc."""
    abs_path = os.path.abspath(playlist_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {playlist_path}")

    args = [abs_path, "--play-and-exit"]

    if random:
        args = ["--random"] + args
    if loop:
        args = ["--loop"] + args
    if repeat:
        args = ["--repeat"] + args
    if start_index is not None:
        args = ["--playlist-start", str(start_index)] + args

    cmd = ["cvlc", "--no-color"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        return {
            "status": "success" if result.returncode == 0 else "error",
            "returncode": result.returncode,
        }
    except FileNotFoundError:
        raise RuntimeError("cvlc not found. Install with: apt install vlc")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Playback timed out")


def concat(
    files: list, output_path: str, profile: str = "mp4-h264-aac"
) -> Dict[str, Any]:
    """Concatenate multiple media files into one."""
    from cli_anything.vlc.core.transcode import (
        build_sout,
        TRANSCODE_PROFILES,
        _run_cvlc,
    )

    abs_out = os.path.abspath(output_path)

    # Build input list
    inputs = []
    for f in files:
        abs_f = os.path.abspath(f)
        if not os.path.exists(abs_f):
            raise FileNotFoundError(f"File not found: {f}")
        inputs.append(abs_f)

    # VLC concat via sout
    # Use the gather and concatenate approach
    input_args = []
    for inp in inputs:
        input_args.extend([inp])

    # Build a simpler concat approach using VLC's vod
    # Actually, let's use VLC's --sout with gather
    concat_input = " ".join(f'"{i}"' for i in inputs)

    prof = TRANSCODE_PROFILES.get(profile, TRANSCODE_PROFILES["mp4-h264-aac"])
    mux = prof.get("mux", "mp4")

    # Use subprocess with multiple input files and VLC's concat
    cmd = ["cvlc", "--no-color"]
    for inp in inputs:
        cmd.append(inp)
    cmd.extend(
        [
            "--sout",
            f"#gather:standard{{access=file,mux={mux},dst={abs_out}}}",
            "--play-and-exit",
            "--run-time",
            "1",
        ]
    )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if os.path.exists(abs_out):
            return {
                "status": "success",
                "output": abs_out,
                "inputs": inputs,
                "size_bytes": os.path.getsize(abs_out),
            }
        return {"status": "error", "message": "Concat failed", "stderr": result.stderr}
    except FileNotFoundError:
        raise RuntimeError("cvlc not found")
    except subprocess.TimeoutExpired:
        # Timeout is expected for concat with --run-time
        if os.path.exists(abs_out):
            return {
                "status": "success",
                "output": abs_out,
                "inputs": inputs,
            }
        return {"status": "error", "message": "Concat timed out"}
