"""VLC CLI - Transcoding and format conversion."""

import os
import json
import subprocess
from typing import Dict, Any, Optional, List


TRANSCODE_PROFILES = {
    "mp4-h264-aac": {
        "description": "MP4 with H.264 video and AAC audio (universal compatibility)",
        "mux": "mp4",
        "vcodec": "h264",
        "acodec": "mp4a",
        "vb": "2000",
        "ab": "192",
        "extension": "mp4",
    },
    "mp4-h265-aac": {
        "description": "MP4 with H.265/HEVC video and AAC audio (better compression)",
        "mux": "mp4",
        "vcodec": "h265",
        "acodec": "mp4a",
        "vb": "1500",
        "ab": "192",
        "extension": "mp4",
    },
    "mkv-h264-aac": {
        "description": "Matroska with H.264 video and AAC audio",
        "mux": "mkv",
        "vcodec": "h264",
        "acodec": "mp4a",
        "vb": "2000",
        "ab": "192",
        "extension": "mkv",
    },
    "webm-vp8-vorbis": {
        "description": "WebM with VP8 video and Vorbis audio",
        "mux": "webm",
        "vcodec": "VP80",
        "acodec": "vorb",
        "vb": "2000",
        "ab": "128",
        "extension": "webm",
    },
    "webm-vp9-opus": {
        "description": "WebM with VP9 video and Opus audio (modern web)",
        "mux": "webm",
        "vcodec": "VP9",
        "acodec": "opus",
        "vb": "2000",
        "ab": "128",
        "extension": "webm",
    },
    "ts-h264-aac": {
        "description": "MPEG-TS with H.264 video and AAC audio (broadcast/streaming)",
        "mux": "ts",
        "vcodec": "h264",
        "acodec": "mp4a",
        "vb": "2000",
        "ab": "192",
        "extension": "ts",
    },
    "ogg-theora-vorbis": {
        "description": "OGG with Theora video and Vorbis audio (open source)",
        "mux": "ogg",
        "vcodec": "theo",
        "acodec": "vorb",
        "vb": "2000",
        "ab": "128",
        "extension": "ogv",
    },
    "mp3-128k": {
        "description": "MP3 audio at 128 kbps (audio only)",
        "mux": "raw",
        "acodec": "mp3",
        "ab": "128",
        "extension": "mp3",
        "no_video": True,
    },
    "mp3-192k": {
        "description": "MP3 audio at 192 kbps (audio only)",
        "mux": "raw",
        "acodec": "mp3",
        "ab": "192",
        "extension": "mp3",
        "no_video": True,
    },
    "mp3-320k": {
        "description": "MP3 audio at 320 kbps (audio only, high quality)",
        "mux": "raw",
        "acodec": "mp3",
        "ab": "320",
        "extension": "mp3",
        "no_video": True,
    },
    "ogg-vorbis-q6": {
        "description": "OGG Vorbis at quality 6 (audio only)",
        "mux": "raw",
        "acodec": "vorb",
        "ab": "192",
        "extension": "ogg",
        "no_video": True,
    },
    "flac-lossless": {
        "description": "FLAC lossless audio (audio only)",
        "mux": "raw",
        "acodec": "flac",
        "extension": "flac",
        "no_video": True,
    },
    "wav-pcm": {
        "description": "WAV uncompressed PCM (audio only)",
        "mux": "raw",
        "acodec": "s16l",
        "extension": "wav",
        "no_video": True,
    },
}


def _run_cvlc(args: list, timeout: int = 3600) -> Dict[str, Any]:
    """Run cvlc with given args."""
    cmd = ["cvlc", "--no-color"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
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


def build_sout(
    profile_name: str,
    output_path: str,
    vcodec_override: Optional[str] = None,
    acodec_override: Optional[str] = None,
    vb_override: Optional[str] = None,
    ab_override: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: Optional[float] = None,
    channels: Optional[int] = None,
    samplerate: Optional[int] = None,
) -> str:
    """Build a VLC sout chain string from a profile."""
    profile = TRANSCODE_PROFILES.get(profile_name)
    if not profile:
        raise ValueError(
            f"Unknown profile: {profile_name}. Use 'transcode profiles' to list."
        )

    vcodec = vcodec_override or profile.get("vcodec")
    acodec = acodec_override or profile.get("acodec")
    vb = vb_override or profile.get("vb")
    ab = ab_override or profile.get("ab")
    mux = profile["mux"]

    # Build transcode options
    tc_opts = []
    if vcodec:
        tc_opts.append(f"vcodec={vcodec}")
    if acodec:
        tc_opts.append(f"acodec={acodec}")
    if vb:
        tc_opts.append(f"vb={vb}")
    if ab:
        tc_opts.append(f"ab={ab}")
    if width:
        tc_opts.append(f"width={width}")
    if height:
        tc_opts.append(f"height={height}")
    if fps:
        tc_opts.append(f"fps={fps}")
    if channels:
        tc_opts.append(f"channels={channels}")
    if samplerate:
        tc_opts.append(f"samplerate={samplerate}")
    if profile.get("no_video"):
        tc_opts.append("vcodec=none")

    tc_str = ",".join(tc_opts)
    return f"#transcode{{{tc_str}}}:standard{{access=file,mux={mux},dst={output_path}}}"


def convert(
    input_path: str,
    output_path: str,
    profile: str = "mp4-h264-aac",
    start_time: Optional[str] = None,
    stop_time: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: Optional[float] = None,
    video_bitrate: Optional[str] = None,
    audio_bitrate: Optional[str] = None,
    audio_codec: Optional[str] = None,
    video_codec: Optional[str] = None,
    no_audio: bool = False,
    no_video: bool = False,
) -> Dict[str, Any]:
    """Convert/transcode a media file."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    abs_in = os.path.abspath(input_path)
    abs_out = os.path.abspath(output_path)

    # Handle no-audio / no-video shortcuts
    actual_profile = profile
    if no_audio and "mp4" in profile:
        actual_profile = "mp4-h264-aac"
    if no_video and "mp3" not in profile:
        actual_profile = "mp3-192k"

    sout = build_sout(
        actual_profile,
        abs_out,
        vcodec_override=video_codec,
        acodec_override=audio_codec,
        vb_override=video_bitrate,
        ab_override=audio_bitrate,
        width=width,
        height=height,
        fps=fps,
    )

    args = [abs_in, "--sout", sout, "--play-and-exit"]

    if start_time:
        args = ["--start-time", str(_parse_time(start_time))] + args
    if stop_time:
        args = ["--stop-time", str(_parse_time(stop_time))] + args

    result = _run_cvlc(args, timeout=3600)

    if os.path.exists(abs_out):
        size = os.path.getsize(abs_out)
        return {
            "status": "success",
            "input": abs_in,
            "output": abs_out,
            "profile": actual_profile,
            "size_bytes": size,
            "size_human": _human_size(size),
            "start_time": start_time,
            "stop_time": stop_time,
        }

    return {
        "status": "error",
        "message": "Conversion failed",
        "profile": actual_profile,
        "stderr": result.get("stderr", ""),
    }


def extract_audio(
    input_path: str, output_path: str, codec: str = "mp3", bitrate: str = "192"
) -> Dict[str, Any]:
    """Extract audio track from a video file."""
    profile_map = {
        "mp3": "mp3-192k",
        "ogg": "ogg-vorbis-q6",
        "flac": "flac-lossless",
        "wav": "wav-pcm",
        "aac": "mp4-h264-aac",
    }
    profile = profile_map.get(codec, "mp3-192k")
    return convert(
        input_path,
        output_path,
        profile=profile,
        no_video=True,
        audio_bitrate=bitrate,
    )


def resize(
    input_path: str,
    output_path: str,
    width: int,
    height: int,
    profile: str = "mp4-h264-aac",
) -> Dict[str, Any]:
    """Resize/transcode video to specific dimensions."""
    return convert(
        input_path,
        output_path,
        profile=profile,
        width=width,
        height=height,
    )


def batch_convert(
    inputs: list, output_dir: str, profile: str = "mp4-h264-aac", **kwargs
) -> List[Dict[str, Any]]:
    """Batch convert multiple files."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    prof = TRANSCODE_PROFILES.get(profile, {})
    ext = prof.get("extension", "mp4")

    for inp in inputs:
        base = os.path.splitext(os.path.basename(inp))[0]
        out_path = os.path.join(output_dir, f"{base}.{ext}")
        result = convert(inp, out_path, profile=profile, **kwargs)
        results.append(result)

    return results


def list_profiles() -> List[Dict[str, str]]:
    """List available transcode profiles."""
    return [
        {
            "name": name,
            "description": p["description"],
            "extension": p.get("extension", ""),
        }
        for name, p in TRANSCODE_PROFILES.items()
    ]


def get_profile(name: str) -> Dict[str, Any]:
    """Get details of a transcode profile."""
    if name not in TRANSCODE_PROFILES:
        raise ValueError(f"Unknown profile: {name}")
    return {"name": name, **TRANSCODE_PROFILES[name]}


def _human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
