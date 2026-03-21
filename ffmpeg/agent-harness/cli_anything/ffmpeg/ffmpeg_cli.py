"""FFmpeg CLI entry point.

Main Click group with REPL support and all command groups.
"""

import json
import os
import sys
from typing import Optional

import click

from .core import concat as concat_mod
from .core import extract as extract_mod
from .core import filter as filter_mod
from .core import probe as probe_mod
from .core import session as session_mod
from .core import transcode as transcode_mod
from .utils.ffmpeg_backend import (
    FFmpegError,
    FFmpegNotFoundError,
    ProgressInfo,
    get_codecs,
    get_filters,
    get_formats,
    get_version,
    list_presets,
)
from .utils.repl_skin import ReplSkin

_json_output = False
_skin: Optional[ReplSkin] = None


def _get_skin() -> ReplSkin:
    """Get or create the REPL skin instance."""
    global _skin
    if _skin is None:
        from . import __version__
        _skin = ReplSkin(
            software="ffmpeg",
            version=__version__,
            history_file=os.path.expanduser("~/.cli-anything-ffmpeg/history"),
        )
    return _skin


def _output(data, use_json=None):
    """Output data as JSON or human-readable."""
    global _json_output
    if use_json is None:
        use_json = _json_output

    if use_json:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        skin = _get_skin()
        if isinstance(data, dict):
            if data.get("status") == "error":
                skin.error(data.get("message", str(data)))
            elif "message" in data:
                skin.success(data["message"])
            else:
                for key, val in data.items():
                    if isinstance(val, (list, dict)):
                        click.echo(f"{key}:")
                        click.echo(json.dumps(val, indent=2, default=str))
                    else:
                        skin.status(key, str(val))
        else:
            click.echo(str(data))


def _progress_callback(info: ProgressInfo):
    """Progress callback for ffmpeg operations."""
    skin = _get_skin()
    if info.time:
        skin.progress(
            info.time_seconds,
            max(info.time_seconds + 1, 1),
            f"Processing {info.time}",
        )


# ─── Main CLI Group ─────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.version_option(version="1.0.0", prog_name="cli-anything-ffmpeg")
@click.pass_context
def cli(ctx, use_json):
    """CLI-Anything FFmpeg harness — make ffmpeg agent-native."""
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ─── Probe Commands ─────────────────────────────────────────────

@cli.group()
def probe():
    """Analyze media files using ffprobe."""
    pass


@probe.command("streams")
@click.argument("input_file")
@click.option("--type", "stream_type", type=click.Choice(["video", "audio", "subtitle"]), help="Filter by stream type")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def probe_streams_cmd(input_file, stream_type, use_json):
    """Show stream information."""
    try:
        data = probe_mod.probe_streams(input_file, stream_type)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@probe.command("metadata")
@click.argument("input_file")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def probe_metadata_cmd(input_file, use_json):
    """Show all metadata."""
    try:
        data = probe_mod.probe_metadata(input_file)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@probe.command("duration")
@click.argument("input_file")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def probe_duration_cmd(input_file, use_json):
    """Get duration in seconds."""
    try:
        duration = probe_mod.probe_duration(input_file)
        _output({"duration_seconds": duration}, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@probe.command("codec")
@click.argument("input_file")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def probe_codec_cmd(input_file, use_json):
    """Show codec information for all streams."""
    try:
        data = probe_mod.probe_codecs(input_file)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@probe.command("info")
@click.argument("input_file")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def probe_info_cmd(input_file, use_json):
    """Show human-readable summary of a media file."""
    try:
        data = probe_mod.summary(input_file)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


# ─── Transcode Commands ────────────────────────────────────────

@cli.group()
def transcode():
    """Convert media between formats."""
    pass


@transcode.command("convert")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--video-codec", "-vc", help="Video codec (e.g., libx264, copy)")
@click.option("--audio-codec", "-ac", help="Audio codec (e.g., aac, copy)")
@click.option("--crf", type=int, help="Quality (0-51, lower=better)")
@click.option("--preset", "enc_preset", help="Encoding speed (ultrafast..veryslow)")
@click.option("--bitrate", "-b", help="Target video bitrate (e.g., 5M)")
@click.option("--resolution", "-s", help="Output resolution (e.g., 1920x1080)")
@click.option("--fps", "-r", type=float, help="Output frame rate")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def transcode_convert(input_file, output_file, video_codec, audio_codec, crf, enc_preset, bitrate, resolution, fps, use_json):
    """Convert a media file."""
    try:
        data = transcode_mod.convert(
            input_file, output_file,
            video_codec=video_codec,
            audio_codec=audio_codec,
            crf=crf,
            preset=enc_preset,
            bitrate=bitrate,
            resolution=resolution,
            fps=fps,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("transcode.convert", {
            "input": input_file, "output": output_file,
            "video_codec": video_codec, "audio_codec": audio_codec,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@transcode.command("preset-list")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def preset_list(use_json):
    """List available conversion presets."""
    data = list_presets()
    _output(data, use_json)


@transcode.command("preset-info")
@click.argument("preset_name")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def preset_info(preset_name, use_json):
    """Show details for a specific preset."""
    from .utils.ffmpeg_backend import get_preset, preset_to_args
    preset = get_preset(preset_name)
    if preset is None:
        _output({"status": "error", "message": f"Unknown preset: {preset_name}"}, use_json)
        return
    data = {
        "name": preset_name,
        "description": preset.get("description", ""),
        "args": preset_to_args(preset_name),
        "config": {k: v for k, v in preset.items() if k != "description"},
    }
    _output(data, use_json)


# ─── Filter Commands ────────────────────────────────────────────

@cli.group()
def filter():
    """Apply video and audio filters."""
    pass


@filter.command("list")
@click.option("--type", "filter_type", type=click.Choice(["video", "audio"]), help="Filter by type")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def filter_list(filter_type, use_json):
    """List available filters."""
    data = filter_mod.list_filters(filter_type)
    _output(data, use_json)


@filter.command("apply")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--vf", "video_filter", help="Video filter string")
@click.option("--af", "audio_filter", help="Audio filter string")
@click.option("--scale", help="Shortcut: scale=WxH")
@click.option("--crop", help="Shortcut: crop=W:H:X:Y")
@click.option("--volume", help="Shortcut: volume level (e.g., 1.5, +10dB)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def filter_apply(input_file, output_file, video_filter, audio_filter, scale, crop, volume, use_json):
    """Apply filters to a media file."""
    try:
        # Build filter strings from shortcuts
        vf_parts = []
        if video_filter:
            vf_parts.append(video_filter)
        if scale:
            vf_parts.append(f"scale={scale.replace('x', ':')}")
        if crop:
            vf_parts.append(f"crop={crop.replace(':', ':')}")

        af_parts = []
        if audio_filter:
            af_parts.append(audio_filter)
        if volume:
            af_parts.append(f"volume={volume}")

        vf = ",".join(vf_parts) if vf_parts else None
        af = ",".join(af_parts) if af_parts else None

        data = filter_mod.apply_filters(
            input_file, output_file,
            video_filter=vf,
            audio_filter=af,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("filter.apply", {
            "input": input_file, "output": output_file,
            "vf": vf, "af": af,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


# ─── Concat Commands ────────────────────────────────────────────

@cli.group()
def concat():
    """Join, trim, and split media files."""
    pass


@concat.command("join")
@click.argument("input_files", nargs=-1, required=True)
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--reencode", is_flag=True, help="Re-encode instead of stream copy")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def concat_join(input_files, output_file, reencode, use_json):
    """Join multiple media files."""
    try:
        data = concat_mod.concat(
            list(input_files), output_file,
            copy_streams=not reencode,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("concat.join", {
            "inputs": list(input_files), "output": output_file,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@concat.command("trim")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--start", "-ss", help="Start time (HH:MM:SS.ms)")
@click.option("--end", "-to", help="End time (HH:MM:SS.ms)")
@click.option("--duration", "-t", help="Duration (HH:MM:SS.ms)")
@click.option("--reencode", is_flag=True, help="Re-encode instead of stream copy")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def concat_trim(input_file, output_file, start, end, duration, reencode, use_json):
    """Trim/cut a media file."""
    try:
        data = concat_mod.trim(
            input_file, output_file,
            start=start, end=end, duration=duration,
            copy_streams=not reencode,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("concat.trim", {
            "input": input_file, "output": output_file,
            "start": start, "end": end, "duration": duration,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@concat.command("split")
@click.argument("input_file")
@click.option("-o", "--output-dir", required=True, help="Output directory")
@click.option("--segment-duration", "-d", type=float, help="Segment duration in seconds")
@click.option("--segment-count", "-n", type=int, help="Number of segments")
@click.option("--extension", "-e", default=".mp4", help="Output file extension")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def concat_split(input_file, output_dir, segment_duration, segment_count, extension, use_json):
    """Split a media file into segments."""
    try:
        data = concat_mod.split(
            input_file, output_dir,
            segment_duration=segment_duration,
            segment_count=segment_count,
            extension=extension,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("concat.split", {
            "input": input_file, "output_dir": output_dir,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


# ─── Extract Commands ───────────────────────────────────────────

@cli.group()
def extract():
    """Extract audio, video, subtitles, or thumbnails."""
    pass


@extract.command("audio")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--codec", "-c", help="Audio codec (auto from extension if omitted)")
@click.option("--bitrate", "-b", help="Audio bitrate (e.g., 192k)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def extract_audio(input_file, output_file, codec, bitrate, use_json):
    """Extract audio stream."""
    try:
        data = extract_mod.extract_audio(
            input_file, output_file,
            codec=codec, bitrate=bitrate,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("extract.audio", {
            "input": input_file, "output": output_file,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@extract.command("video")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--codec", "-c", help="Video codec (stream copy if omitted)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def extract_video_cmd(input_file, output_file, codec, use_json):
    """Extract video stream."""
    try:
        data = extract_mod.extract_video(
            input_file, output_file,
            codec=codec,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("extract.video", {
            "input": input_file, "output": output_file,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@extract.command("thumbnail")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--time", "-t", "time_pos", default="00:00:01", help="Time position (HH:MM:SS.ms)")
@click.option("--quality", "-q", default=2, type=int, help="JPEG quality (2-31)")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def extract_thumbnail(input_file, output_file, time_pos, quality, use_json):
    """Extract a single frame as thumbnail."""
    try:
        data = extract_mod.extract_thumbnail(
            input_file, output_file,
            time=time_pos, quality=quality,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("extract.thumbnail", {
            "input": input_file, "output": output_file,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


# ─── Export Commands ────────────────────────────────────────────

@cli.group()
def export():
    """Render using presets."""
    pass


@export.command("render")
@click.argument("input_file")
@click.option("-o", "--output", "output_file", required=True, help="Output file path")
@click.option("--preset", "preset_name", required=True, help="Preset name")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def export_render(input_file, output_file, preset_name, use_json):
    """Render using a named preset."""
    try:
        data = transcode_mod.convert_with_preset(
            input_file, output_file,
            preset_name,
            progress_callback=_progress_callback if not use_json else None,
        )
        session_mod.get_session().record("export.render", {
            "input": input_file, "output": output_file, "preset": preset_name,
        }, data)
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@export.command("presets")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def export_presets(use_json):
    """List available rendering presets."""
    data = list_presets()
    _output(data, use_json)


# ─── Session Commands ───────────────────────────────────────────

@cli.group()
def session():
    """Session history and undo/redo."""
    pass


@session.command("status")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def session_status(use_json):
    """Show session status."""
    data = session_mod.get_session().status()
    _output(data, use_json)


@session.command("history")
@click.option("--limit", "-n", type=int, help="Limit number of entries")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def session_history(limit, use_json):
    """Show command history."""
    data = session_mod.get_session().history(limit)
    _output(data, use_json)


@session.command()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def undo(use_json):
    """Undo the last command."""
    entry = session_mod.get_session().undo()
    if entry:
        _output({"status": "success", "undone": entry.to_dict()}, use_json)
    else:
        _output({"status": "error", "message": "Nothing to undo"}, use_json)


@session.command()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def redo(use_json):
    """Redo the last undone command."""
    entry = session_mod.get_session().redo()
    if entry:
        _output({"status": "success", "redone": entry.to_dict()}, use_json)
    else:
        _output({"status": "error", "message": "Nothing to redo"}, use_json)


# ─── Info Commands ──────────────────────────────────────────────

@cli.command("version")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def version_cmd(use_json):
    """Show ffmpeg version."""
    try:
        data = {"ffmpeg_version": get_version()}
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@cli.command("codecs")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def codecs_cmd(use_json):
    """List available codecs."""
    try:
        data = get_codecs()
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@cli.command("formats")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def formats_cmd(use_json):
    """List available formats."""
    try:
        data = get_formats()
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


@cli.command("filters")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def filters_cmd(use_json):
    """List available filters."""
    try:
        data = get_filters()
        _output(data, use_json)
    except FFmpegError as e:
        _output({"status": "error", "message": str(e)}, use_json)


# ─── REPL Mode ──────────────────────────────────────────────────

@cli.command()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def repl(use_json):
    """Start interactive REPL mode."""
    global _json_output
    _json_output = use_json
    skin = _get_skin()
    skin.print_banner()

    try:
        while True:
            try:
                user_input = skin.get_input(None)
                if not user_input:
                    continue
                user_input = user_input.strip()
                if user_input in ("quit", "exit", "q"):
                    skin.print_goodbye()
                    break
                if user_input == "help":
                    _print_help()
                    continue
                if user_input == "json":
                    _json_output = not _json_output
                    skin.info(f"JSON output: {'on' if _json_output else 'off'}")
                    continue

                # Parse and execute as CLI command
                args = user_input.split()
                try:
                    cli.main(args=args, standalone_mode=False)
                except SystemExit:
                    pass
                except FFmpegError as e:
                    skin.error(str(e))
                except Exception as e:
                    skin.error(f"Error: {e}")

            except (EOFError, KeyboardInterrupt):
                skin.print_goodbye()
                break
    except Exception as e:
        skin.error(f"REPL error: {e}")


def _print_help():
    """Print REPL help."""
    skin = _get_skin()
    commands = {
        "probe <file>": "Analyze media file",
        "transcode convert <file> -o <out>": "Convert format",
        "filter apply <file> -o <out> --vf <filter>": "Apply filter",
        "concat join <file1> <file2> -o <out>": "Join files",
        "concat trim <file> -o <out> --start <time>": "Trim file",
        "extract audio <file> -o <out>": "Extract audio",
        "extract thumbnail <file> -o <out>": "Extract thumbnail",
        "export render <file> -o <out> --preset <name>": "Render with preset",
        "session status": "Show session info",
        "session undo": "Undo last command",
        "session redo": "Redo last undone",
        "json": "Toggle JSON output",
        "quit/exit/q": "Exit REPL",
    }
    skin.help(commands)


def main():
    """Entry point for CLI-Anything FFmpeg."""
    try:
        cli()
    except FFmpegNotFoundError as e:
        skin = _get_skin()
        skin.error(str(e))
        sys.exit(1)
    except FFmpegError as e:
        skin = _get_skin()
        skin.error(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
