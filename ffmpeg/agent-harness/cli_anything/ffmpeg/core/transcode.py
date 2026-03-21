"""Transcoding operations.

Format conversion with presets and quality control.
"""

import os
from typing import Any, Dict, List, Optional

from ..utils.ffmpeg_backend import (
    FFmpegError,
    ProgressInfo,
    list_presets,
    preset_to_args,
    run_ffmpeg,
)


def convert(
    input_file: str,
    output_file: str,
    video_codec: Optional[str] = None,
    audio_codec: Optional[str] = None,
    crf: Optional[int] = None,
    preset: Optional[str] = None,
    bitrate: Optional[str] = None,
    resolution: Optional[str] = None,
    fps: Optional[float] = None,
    extra_args: Optional[List[str]] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """Convert a media file.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        video_codec: Video codec (e.g., 'libx264', 'copy').
        audio_codec: Audio codec (e.g., 'aac', 'copy').
        crf: Constant Rate Factor (quality, 0-51, lower=better).
        preset: Encoding speed preset (ultrafast..veryslow).
        bitrate: Target bitrate (e.g., '5M', '192k').
        resolution: Output resolution (e.g., '1920x1080').
        fps: Output frame rate.
        extra_args: Additional ffmpeg arguments.
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with conversion results.
    """
    args = ["-i", input_file, "-y"]

    if video_codec:
        args.extend(["-c:v", video_codec])
    if audio_codec:
        args.extend(["-c:a", audio_codec])
    if crf is not None:
        args.extend(["-crf", str(crf)])
    if preset:
        args.extend(["-preset", preset])
    if bitrate:
        args.extend(["-b:v", bitrate])
    if resolution:
        w, h = resolution.split("x")
        args.extend(["-vf", f"scale={w}:{h}"])
    if fps is not None:
        args.extend(["-r", str(fps)])
    if extra_args:
        args.extend(extra_args)

    args.append(output_file)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Conversion failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "duration_seconds": round(result.duration_seconds, 3),
        "command": " ".join(result.command),
    }


def convert_with_preset(
    input_file: str,
    output_file: str,
    preset_name: str,
    progress_callback=None,
) -> Dict[str, Any]:
    """Convert using a named preset.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        preset_name: Name of the preset (e.g., 'web-hd', 'gif').
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with conversion results.
    """
    preset_args = preset_to_args(preset_name)
    args = ["-i", input_file, "-y"] + preset_args + [output_file]

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Preset conversion failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "preset": preset_name,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def batch_convert(
    input_files: List[str],
    output_dir: str,
    video_codec: Optional[str] = None,
    audio_codec: Optional[str] = None,
    extension: Optional[str] = None,
    progress_callback=None,
) -> List[Dict[str, Any]]:
    """Batch convert multiple files.

    Args:
        input_files: List of source file paths.
        output_dir: Output directory.
        video_codec: Video codec to use.
        audio_codec: Audio codec to use.
        extension: Output file extension (auto-detected from codec if None).
        progress_callback: Optional callback for progress updates.

    Returns:
        List of result dicts per file.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for input_file in input_files:
        basename = os.path.splitext(os.path.basename(input_file))[0]
        ext = extension or _codec_to_extension(video_codec, audio_codec)
        output_file = os.path.join(output_dir, f"{basename}{ext}")

        try:
            result = convert(
                input_file,
                output_file,
                video_codec=video_codec,
                audio_codec=audio_codec,
                progress_callback=progress_callback,
            )
            results.append(result)
        except FFmpegError as e:
            results.append({
                "status": "error",
                "input": input_file,
                "error": str(e),
            })

    return results


def _codec_to_extension(
    video_codec: Optional[str],
    audio_codec: Optional[str],
) -> str:
    """Map codec to common file extension."""
    codec_ext = {
        "libx264": ".mp4",
        "libx265": ".mp4",
        "libvpx-vp9": ".webm",
        "libvorbis": ".ogg",
        "libmp3lame": ".mp3",
        "aac": ".m4a",
        "flac": ".flac",
        "gif": ".gif",
        "copy": ".mkv",
    }

    if video_codec and video_codec in codec_ext:
        return codec_ext[video_codec]
    if audio_codec and audio_codec in codec_ext:
        return codec_ext[audio_codec]
    return ".mp4"
