"""Video and audio filter operations.

Provides filter chain construction and application.
"""

from typing import Any, Dict, List, Optional

from ..utils.ffmpeg_backend import FFmpegError, ProgressInfo, run_ffmpeg


# Common filter definitions
VIDEO_FILTERS = {
    "scale": {
        "description": "Resize video",
        "params": {"width": "Output width", "height": "Output height (-1 for auto)"},
        "template": "scale={width}:{height}",
    },
    "crop": {
        "description": "Crop video",
        "params": {"w": "Width", "h": "Height", "x": "X offset", "y": "Y offset"},
        "template": "crop={w}:{h}:{x}:{y}",
    },
    "fps": {
        "description": "Change frame rate",
        "params": {"fps": "Target FPS"},
        "template": "fps={fps}",
    },
    "eq": {
        "description": "Adjust brightness/contrast/saturation",
        "params": {
            "brightness": "Brightness (-1.0 to 1.0)",
            "contrast": "Contrast (0 to 2.0)",
            "saturation": "Saturation (0 to 3.0)",
        },
        "template": "eq=brightness={brightness}:contrast={contrast}:saturation={saturation}",
    },
    "hflip": {
        "description": "Flip horizontally",
        "params": {},
        "template": "hflip",
    },
    "vflip": {
        "description": "Flip vertically",
        "params": {},
        "template": "vflip",
    },
    "rotate": {
        "description": "Rotate video",
        "params": {"angle": "Rotation angle in radians"},
        "template": "rotate={angle}",
    },
    "transpose": {
        "description": "Transpose/rotate (0=90ccw,1=90cw,2=90cw+vflip,3=180)",
        "params": {"dir": "Direction (0-3)"},
        "template": "transpose={dir}",
    },
    "overlay": {
        "description": "Overlay one video on another",
        "params": {"x": "X position", "y": "Y position"},
        "template": "overlay={x}:{y}",
    },
    "pad": {
        "description": "Add padding",
        "params": {"w": "Width", "h": "Height", "x": "X offset", "y": "Y offset"},
        "template": "pad={w}:{h}:{x}:{y}",
    },
    "fade": {
        "description": "Fade in/out",
        "params": {
            "type": "in or out",
            "start": "Start time (seconds)",
            "duration": "Duration (seconds)",
        },
        "template": "fade=t={type}:st={start}:d={duration}",
    },
    "drawtext": {
        "description": "Draw text on video",
        "params": {"text": "Text to draw", "fontsize": "Font size", "fontcolor": "Font color"},
        "template": "drawtext=text='{text}':fontsize={fontsize}:fontcolor={fontcolor}",
    },
    "setpts": {
        "description": "Change playback speed (0.5=2x speed, 2.0=0.5x speed)",
        "params": {"factor": "Speed factor"},
        "template": "setpts={factor}*PTS",
    },
}

AUDIO_FILTERS = {
    "volume": {
        "description": "Adjust volume",
        "params": {"level": "Volume level (0.0-2.0, or dB like +10dB)"},
        "template": "volume={level}",
    },
    "atempo": {
        "description": "Change playback speed (0.5-2.0)",
        "params": {"speed": "Speed factor (0.5-2.0)"},
        "template": "atempo={speed}",
    },
    "afade": {
        "description": "Audio fade in/out",
        "params": {
            "type": "in or out",
            "start": "Start time (seconds)",
            "duration": "Duration (seconds)",
        },
        "template": "afade=t={type}:st={start}:d={duration}",
    },
    "lowpass": {
        "description": "Low-pass filter",
        "params": {"freq": "Cutoff frequency (Hz)"},
        "template": "lowpass=f={freq}",
    },
    "highpass": {
        "description": "High-pass filter",
        "params": {"freq": "Cutoff frequency (Hz)"},
        "template": "highpass=f={freq}",
    },
    "aecho": {
        "description": "Add echo",
        "params": {
            "in_gain": "Input gain (0-1)",
            "out_gain": "Output gain (0-1)",
            "delays": "Delay times (ms)",
            "decays": "Decay values",
        },
        "template": "aecho={in_gain}:{out_gain}:{delays}:{decays}",
    },
}


def list_filters(filter_type: Optional[str] = None) -> List[Dict[str, str]]:
    """List available filters.

    Args:
        filter_type: 'video', 'audio', or None for both.

    Returns:
        List of filter info dicts.
    """
    filters = []

    if filter_type in (None, "video"):
        for name, info in VIDEO_FILTERS.items():
            filters.append({
                "name": name,
                "type": "video",
                "description": info["description"],
            })

    if filter_type in (None, "audio"):
        for name, info in AUDIO_FILTERS.items():
            filters.append({
                "name": name,
                "type": "audio",
                "description": info["description"],
            })

    return filters


def build_filter(
    filter_name: str,
    filter_type: str = "video",
    **params,
) -> str:
    """Build a filter string from name and parameters.

    Args:
        filter_name: Name of the filter.
        filter_type: 'video' or 'audio'.
        **params: Filter parameters.

    Returns:
        Filter string for use with -vf or -af.

    Raises:
        FFmpegError: If filter not found or params missing.
    """
    filter_defs = VIDEO_FILTERS if filter_type == "video" else AUDIO_FILTERS
    filter_def = filter_defs.get(filter_name)

    if filter_def is None:
        raise FFmpegError(f"Unknown {filter_type} filter: {filter_name}")

    template = filter_def["template"]

    try:
        return template.format(**params)
    except KeyError as e:
        missing = str(e)
        required = list(filter_def["params"].keys())
        raise FFmpegError(
            f"Missing parameter {missing} for filter '{filter_name}'. "
            f"Required: {required}"
        )


def apply_video_filter(
    input_file: str,
    output_file: str,
    filter_string: str,
    progress_callback=None,
) -> Dict[str, Any]:
    """Apply a video filter to a file.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        filter_string: Video filter string (e.g., 'scale=1280:720').
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    args = ["-i", input_file, "-y", "-vf", filter_string, output_file]
    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Video filter failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "filter": filter_string,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def apply_audio_filter(
    input_file: str,
    output_file: str,
    filter_string: str,
    progress_callback=None,
) -> Dict[str, Any]:
    """Apply an audio filter to a file.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        filter_string: Audio filter string (e.g., 'volume=1.5').
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    args = ["-i", input_file, "-y", "-af", filter_string, output_file]
    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Audio filter failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "filter": filter_string,
        "duration_seconds": round(result.duration_seconds, 3),
    }


def apply_filters(
    input_file: str,
    output_file: str,
    video_filter: Optional[str] = None,
    audio_filter: Optional[str] = None,
    progress_callback=None,
) -> Dict[str, Any]:
    """Apply video and/or audio filters.

    Args:
        input_file: Source file path.
        output_file: Destination file path.
        video_filter: Video filter string.
        audio_filter: Audio filter string.
        progress_callback: Optional callback for progress updates.

    Returns:
        Dict with operation results.
    """
    args = ["-i", input_file, "-y"]

    if video_filter:
        args.extend(["-vf", video_filter])
    if audio_filter:
        args.extend(["-af", audio_filter])

    args.append(output_file)

    result = run_ffmpeg(args, progress_callback=progress_callback)

    if not result.success:
        raise FFmpegError(
            f"Filter application failed: {result.stderr[-500:]}",
            result.stderr,
            result.returncode,
        )

    return {
        "status": "success",
        "input": input_file,
        "output": output_file,
        "video_filter": video_filter,
        "audio_filter": audio_filter,
        "duration_seconds": round(result.duration_seconds, 3),
    }
