"""Media probing using ffprobe.

Provides structured metadata extraction for audio/video files.
"""

import json
from typing import Any, Dict, List, Optional

from ..utils.ffmpeg_backend import FFmpegError, probe_json, run_ffprobe


def probe_streams(input_file: str, stream_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Probe streams in a media file.

    Args:
        input_file: Path to the media file.
        stream_type: Optional filter by type ('video', 'audio', 'subtitle').

    Returns:
        List of stream information dicts.
    """
    data = probe_json(input_file)
    streams = data.get("streams", [])

    if stream_type:
        type_map = {"video": "video", "audio": "audio", "subtitle": "subtitle", "sub": "subtitle"}
        filter_type = type_map.get(stream_type.lower(), stream_type)
        streams = [s for s in streams if s.get("codec_type") == filter_type]

    return streams


def probe_format(input_file: str) -> Dict[str, Any]:
    """Get container format information.

    Args:
        input_file: Path to the media file.

    Returns:
        Dict with format information.
    """
    data = probe_json(input_file)
    return data.get("format", {})


def probe_duration(input_file: str) -> float:
    """Get duration in seconds.

    Args:
        input_file: Path to the media file.

    Returns:
        Duration in seconds, or 0 if unknown.
    """
    fmt = probe_format(input_file)
    try:
        return float(fmt.get("duration", 0))
    except (ValueError, TypeError):
        return 0.0


def probe_codecs(input_file: str) -> List[Dict[str, str]]:
    """Get codec information for all streams.

    Args:
        input_file: Path to the media file.

    Returns:
        List of dicts with codec info per stream.
    """
    streams = probe_streams(input_file)
    return [
        {
            "index": s.get("index", 0),
            "type": s.get("codec_type", "unknown"),
            "codec": s.get("codec_name", "unknown"),
            "codec_long": s.get("codec_long_name", ""),
        }
        for s in streams
    ]


def probe_metadata(input_file: str) -> Dict[str, Any]:
    """Get all metadata (format + tags).

    Args:
        input_file: Path to the media file.

    Returns:
        Dict with format and tag metadata.
    """
    data = probe_json(input_file)
    result = {
        "format": data.get("format", {}),
        "streams": [],
    }

    for s in data.get("streams", []):
        stream_info = {
            "index": s.get("index"),
            "type": s.get("codec_type"),
            "codec": s.get("codec_name"),
            "tags": s.get("tags", {}),
        }
        result["streams"].append(stream_info)

    return result


def probe_chapters(input_file: str) -> List[Dict[str, Any]]:
    """Get chapter information.

    Args:
        input_file: Path to the media file.

    Returns:
        List of chapter info dicts.
    """
    data = probe_json(input_file)
    return data.get("chapters", [])


def summary(input_file: str) -> Dict[str, Any]:
    """Get a human-readable summary of a media file.

    Args:
        input_file: Path to the media file.

    Returns:
        Dict with summary information.
    """
    data = probe_json(input_file)
    fmt = data.get("format", {})
    streams = data.get("streams", [])

    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    summary_info = {
        "file": input_file,
        "format": fmt.get("format_long_name", fmt.get("format_name", "unknown")),
        "duration": fmt.get("duration", "unknown"),
        "size": fmt.get("size", "unknown"),
        "bit_rate": fmt.get("bit_rate", "unknown"),
        "video_streams": len(video_streams),
        "audio_streams": len(audio_streams),
    }

    if video_streams:
        vs = video_streams[0]
        summary_info["video"] = {
            "codec": vs.get("codec_name", "unknown"),
            "width": vs.get("width"),
            "height": vs.get("height"),
            "fps": vs.get("r_frame_rate", "unknown"),
            "bit_rate": vs.get("bit_rate", "unknown"),
        }

    if audio_streams:
        aus = audio_streams[0]
        summary_info["audio"] = {
            "codec": aus.get("codec_name", "unknown"),
            "sample_rate": aus.get("sample_rate", "unknown"),
            "channels": aus.get("channels"),
            "bit_rate": aus.get("bit_rate", "unknown"),
        }

    return summary_info
