"""Concatenation, trimming, and splitting operations.

Join, trim, and split audio/video files.
"""

import os
import tempfile
from typing import Any, Dict, List, Optional

from ..utils.ffmpeg_backend import FFmpegError, run_ffmpeg


def concat(
    input_files: List[str],
    output_file: str,
    copy_streams: bool = True,
    progress_callback=None,
) -> Dict[str, Any]:
    """Concatenate multiple media files.

    Args:
        input_files: List of source file paths.
        output_file: Destination file path.
        copy_streams: If True, use stream copy (fast, no re-encode).
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    if len(input_files) < 2:
        raise FFmpegError("Need at least 2 files to concatenate")

    # Create concat demuxer file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as f:
        concat_file = f.name
        for path in input_files:
            abs_path = os.path.abspath(path)
            f.write(f"file '{abs_path}'\n")

    try:
        args = ["-f", "concat", "-safe", "0", "-i", concat_file, "-y"]

        if copy_streams:
            args.extend(["-c", "copy"])

        args.append(output_file)

        result = run_ffmpeg(args, progress_callback=progress_callback)

        if not result.success:
            raise FFmpegError(
                f"Concatenation failed: {result.stderr[-500:]}",
                result.stderr,
                result.returncode,
            )

        return {
            "status": "success",
            "inputs": input_files,
            "output": output_file,
            "files_joined": len(input_files),
            "stream_copy": copy_streams,
            "duration_seconds": round(result.duration_seconds, 3),
        }
    finally:
        os.unlink(concat_file)


def trim(
    input_file: str,
    output_file: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    duration: Optional[str] = None,
    copy_streams: bool = True,
    progress_callback=None,
) -> Dict[str, Any]:
    """Trim/cut a media file.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        start: Start time (HH:MM:SS.ms or seconds).
        end: End time (HH:MM:SS.ms or seconds).
        duration: Duration of output (alternative to end).
        copy_streams: If True, use stream copy (fast, no re-encode).
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    args = ["-y"]

    if start:
        args.extend(["-ss", start])

    args.extend(["-i", input_file])

    if end:
        args.extend(["-to", end])
    elif duration:
        args.extend(["-t", duration])

    if copy_streams:
        args.extend(["-c", "copy"])

    args.append(output_file)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Trim failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "start": start,
        "end": end,
        "duration": duration,
        "stream_copy": copy_streams,
        "processing_seconds": round(result.duration_seconds, 3),
    }


def split(
    input_file: str,
    output_dir: str,
    segment_duration: Optional[float] = None,
    segment_count: Optional[int] = None,
    output_pattern: str = "segment_%03d",
    extension: str = ".mp4",
    copy_streams: bool = True,
    progress_callback=None,
) -> Dict[str, Any]:
    """Split a media file into segments.

    Args:
        input_file: Source file path.
        output_dir: Output directory for segments.
        segment_duration: Duration of each segment in seconds.
        segment_count: Number of segments (alternative to duration).
        output_pattern: Output filename pattern (%03d for numbering).
        extension: Output file extension.
        copy_streams: If True, use stream copy.
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{output_pattern}{extension}")

    args = ["-i", input_file, "-y"]

    if segment_duration:
        args.extend(["-f", "segment", "-segment_time", str(segment_duration)])
    elif segment_count:
        args.extend(["-f", "segment", "-segment_count", str(segment_count)])
    else:
        raise FFmpegError("Must specify either segment_duration or segment_count")

    if copy_streams:
        args.extend(["-c", "copy"])

    args.append(output_path)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Split failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    # Count output files
    import glob as glob_mod
    pattern = os.path.join(output_dir, f"*{extension}")
    output_files = sorted(glob_mod.glob(pattern))

    return {
        "status": "success",
        "input": input_file,
        "output_dir": output_dir,
        "segments_created": len(output_files),
        "segment_duration": segment_duration,
        "segment_count": segment_count,
        "output_files": output_files,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def merge_side_by_side(
    input_file1: str,
    input_file2: str,
    output_file: str,
    progress_callback=None,
) -> Dict[str, Any]:
    """Place two videos side by side.

    Args:
        input_file1: First source file path.
        input_file2: Second source file path.
        output_file: Destination file path.
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    args = [
        "-i", input_file1,
        "-i", input_file2,
        "-y",
        "-filter_complex", "[0:v]scale=iw/2:ih[left];[1:v]scale=iw/2:ih[right];[left][right]hstack=inputs=2",
        output_file,
    ]

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Side-by-side merge failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "inputs": [input_file1, input_file2],
        "output": output_file,
        "mode": "side_by_side",
        "duration_seconds": round(result.duration_seconds, 3),
    }
