"""Stream extraction operations.

Extract audio, video, subtitles, and thumbnails from media files.
"""

import os
from typing import Any, Dict, Optional

from ..utils.ffmpeg_backend import FFmpegError, run_ffmpeg


def extract_audio(
    input_file: str,
    output_file: str,
    codec: Optional[str] = None,
    bitrate: Optional[str] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """Extract audio stream from a media file.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        codec: Audio codec (auto-detected from extension if None).
        bitrate: Audio bitrate (e.g., '192k').
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with extraction results.
    """
    args = ["-i", input_file, "-y", "-vn"]

    if codec:
        args.extend(["-c:a", codec])
    if bitrate:
        args.extend(["-b:a", bitrate])

    args.append(output_file)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Audio extraction failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "type": "audio",
        "codec": codec or "auto",
        "bitrate": bitrate,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def extract_video(
    input_file: str,
    output_file: str,
    codec: Optional[str] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """Extract video stream from a media file.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        codec: Video codec (stream copy if None).
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with extraction results.
    """
    args = ["-i", input_file, "-y", "-an"]

    if codec:
        args.extend(["-c:v", codec])
    else:
        args.extend(["-c:v", "copy"])

    args.append(output_file)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Video extraction failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "type": "video",
        "codec": codec or "copy",
        "duration_seconds": round(result.duration_seconds, 3),
    }


def extract_subtitles(
    input_file: str,
    output_file: str,
    stream_index: Optional[int] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """Extract subtitle stream from a media file.

    Args:
        input_file: Source file path.
        output_file: Destination file path (.srt, .ass, .vtt).
        stream_index: Subtitle stream index (first subtitle stream if None).
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with extraction results.
    """
    if stream_index is not None:
        map_arg = f"0:s:{stream_index}"
    else:
        map_arg = "0:s:0"

    args = [
        "-i", input_file,
        "-y",
        "-map", map_arg,
        "-c:s", "copy",
        output_file,
    ]

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Subtitle extraction failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "type": "subtitles",
        "stream_index": stream_index,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def extract_thumbnail(
    input_file: str,
    output_file: str,
    time: str = "00:00:01",
    quality: int = 2,
    progress_callback=None,
) -> Dict[str, Any]:
    """Extract a single frame as a thumbnail.

    Args:
        input_file: Source file path.
        output_file: Destination file path (.jpg, .png).
        time: Time position to extract (HH:MM:SS.ms or seconds).
        quality: JPEG quality (2-31, lower=better).
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with extraction results.
    """
    args = [
        "-i", input_file,
        "-y",
        "-ss", time,
        "-frames:v", "1",
        "-q:v", str(quality),
        output_file,
    ]

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Thumbnail extraction failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "type": "thumbnail",
        "time": time,
        "quality": quality,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def extract_frames(
    input_file: str,
    output_dir: str,
    fps: Optional[float] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    pattern: str = "frame_%04d",
    extension: str = ".png",
    progress_callback=None,
) -> Dict[str, Any]:
    """Extract all frames or frames at a specific rate.

    Args:
        input_file: Source file path.
        output_dir: Output directory for frames.
        fps: Extract at this FPS (all frames if None).
        start: Start time.
        end: End time.
        pattern: Output filename pattern.
        extension: Output file extension.
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with extraction results.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{pattern}{extension}")

    args = ["-y"]

    if start:
        args.extend(["-ss", start])

    args.extend(["-i", input_file])

    if end:
        args.extend(["-to", end])

    if fps:
        args.extend(["-vf", f"fps={fps}"])

    args.append(output_path)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Frame extraction failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    import glob as glob_mod
    output_files = sorted(glob_mod.glob(os.path.join(output_dir, f"*{extension}")))

    return {
        "status": "success",
        "input": input_file,
        "output_dir": output_dir,
        "frames_extracted": len(output_files),
        "fps": fps,
        "duration_seconds": round(result.duration_seconds, 3),
    }
