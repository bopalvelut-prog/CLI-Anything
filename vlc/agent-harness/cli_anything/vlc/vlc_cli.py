#!/usr/bin/env python3
"""VLC CLI — A stateful command-line interface for media operations.

This CLI wraps VLC's powerful media capabilities into a structured,
agent-friendly interface with JSON output, project state, and REPL mode.

Usage:
    # One-shot commands
    cli-anything-vlc probe video.mp4
    cli-anything-vlc transcode convert video.mp4 output.webm --profile webm-vp9-opus
    cli-anything-vlc playback screenshot video.mp4 frame.png --time 00:01:30
    cli-anything-vlc playback extract-audio video.mp4 audio.mp3

    # Interactive REPL
    cli-anything-vlc
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.vlc.core.session import Session
from cli_anything.vlc.core import probe as probe_mod
from cli_anything.vlc.core import playback as pb_mod
from cli_anything.vlc.core import transcode as tc_mod
from cli_anything.vlc.core import playlist as pl_mod
from cli_anything.vlc.core import streaming as st_mod

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_not_found"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except (ValueError, IndexError, RuntimeError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except FileExistsError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "file_exists"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI Group ──────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """VLC CLI — Stateful media operations from the command line.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Probe Commands ──────────────────────────────────────────────
@cli.group()
def probe():
    """Media file analysis commands."""
    pass


@probe.command("info")
@click.argument("path")
@handle_error
def probe_info(path):
    """Probe a media file and show its properties."""
    info = probe_mod.probe(path)
    output(info)


@probe.command("formats")
@handle_error
def probe_formats():
    """List supported input/output formats and transcode profiles."""
    fmts = probe_mod.formats()
    output(fmts)


# ── Playback Commands ──────────────────────────────────────────
@cli.group()
def playback():
    """Playback and capture commands."""
    pass


@playback.command("play")
@click.argument("input_path")
@click.option(
    "--start", "start_time", default=None, help="Start time (HH:MM:SS or seconds)"
)
@click.option(
    "--stop", "stop_time", default=None, help="Stop time (HH:MM:SS or seconds)"
)
@click.option("--volume", "-v", type=int, default=None, help="Volume (0-256)")
@click.option("--fullscreen", "-f", is_flag=True, help="Fullscreen mode")
@click.option("--loop", is_flag=True, help="Loop playback")
@click.option("--no-video", is_flag=True, help="Audio-only mode")
@click.option("--rate", type=float, default=None, help="Playback rate (e.g. 1.5)")
@handle_error
def playback_play(
    input_path, start_time, stop_time, volume, fullscreen, loop, no_video, rate
):
    """Play a media file."""
    result = pb_mod.play(
        input_path,
        start_time=start_time,
        stop_time=stop_time,
        volume=volume,
        fullscreen=fullscreen,
        loop=loop,
        no_video=no_video,
        rate=rate,
    )
    output(result)


@playback.command("screenshot")
@click.argument("input_path")
@click.argument("output_path")
@click.option(
    "--time", "time_offset", default="0", help="Time offset (HH:MM:SS or seconds)"
)
@click.option("--width", "-w", type=int, default=None, help="Output width")
@click.option("--height", "-h", type=int, default=None, help="Output height")
@handle_error
def playback_screenshot(input_path, output_path, time_offset, width, height):
    """Capture a screenshot from a video at a specific time."""
    result = pb_mod.screenshot(
        input_path,
        output_path,
        time_offset=time_offset,
        width=width,
        height=height,
    )
    output(result, f"Screenshot saved to: {output_path}")


@playback.command("record")
@click.argument("input_path")
@click.argument("output_path")
@click.option(
    "--duration", "-d", default=None, help="Recording duration (HH:MM:SS or seconds)"
)
@click.option("--start", "start_time", default=None, help="Start time offset")
@handle_error
def playback_record(input_path, output_path, duration, start_time):
    """Record/trim a segment of a media file."""
    result = pb_mod.record(
        input_path,
        output_path,
        duration=duration,
        start_time=start_time,
    )
    output(result)


@playback.command("extract-audio")
@click.argument("input_path")
@click.argument("output_path")
@click.option(
    "--codec",
    "-c",
    default="mp3",
    type=click.Choice(["mp3", "ogg", "flac", "wav", "aac"]),
)
@click.option("--bitrate", "-b", default="192", help="Audio bitrate (kbps)")
@handle_error
def playback_extract_audio(input_path, output_path, codec, bitrate):
    """Extract audio track from a video file."""
    result = tc_mod.extract_audio(input_path, output_path, codec=codec, bitrate=bitrate)
    output(result)


# ── Transcode Commands ──────────────────────────────────────────
@cli.group()
def transcode():
    """Transcoding and format conversion commands."""
    pass


@transcode.command("convert")
@click.argument("input_path")
@click.argument("output_path")
@click.option("--profile", "-p", default="mp4-h264-aac", help="Transcode profile")
@click.option("--start", "start_time", default=None, help="Start time offset")
@click.option("--stop", "stop_time", default=None, help="Stop time offset")
@click.option("--width", "-w", type=int, default=None, help="Output width")
@click.option("--height", "-h", type=int, default=None, help="Output height")
@click.option("--fps", type=float, default=None, help="Output frame rate")
@click.option("--vb", "video_bitrate", default=None, help="Video bitrate (kbps)")
@click.option("--ab", "audio_bitrate", default=None, help="Audio bitrate (kbps)")
@click.option("--vcodec", "video_codec", default=None, help="Video codec override")
@click.option("--acodec", "audio_codec", default=None, help="Audio codec override")
@click.option("--no-audio", is_flag=True, help="Strip audio")
@click.option("--no-video", is_flag=True, help="Strip video")
@handle_error
def transcode_convert(
    input_path,
    output_path,
    profile,
    start_time,
    stop_time,
    width,
    height,
    fps,
    video_bitrate,
    audio_bitrate,
    video_codec,
    audio_codec,
    no_audio,
    no_video,
):
    """Convert/transcode a media file using a profile."""
    result = tc_mod.convert(
        input_path,
        output_path,
        profile=profile,
        start_time=start_time,
        stop_time=stop_time,
        width=width,
        height=height,
        fps=fps,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        video_codec=video_codec,
        audio_codec=audio_codec,
        no_audio=no_audio,
        no_video=no_video,
    )
    output(result)


@transcode.command("resize")
@click.argument("input_path")
@click.argument("output_path")
@click.option("--width", "-w", type=int, required=True, help="Output width")
@click.option("--height", "-h", type=int, required=True, help="Output height")
@click.option("--profile", "-p", default="mp4-h264-aac", help="Transcode profile")
@handle_error
def transcode_resize(input_path, output_path, width, height, profile):
    """Resize a video to specific dimensions."""
    result = tc_mod.resize(input_path, output_path, width, height, profile=profile)
    output(result)


@transcode.command("profiles")
@handle_error
def transcode_profiles():
    """List available transcode profiles."""
    profiles = tc_mod.list_profiles()
    output(profiles, "Available transcode profiles:")


@transcode.command("profile-info")
@click.argument("name")
@handle_error
def transcode_profile_info(name):
    """Show details of a transcode profile."""
    info = tc_mod.get_profile(name)
    output(info)


@transcode.command("batch")
@click.argument("inputs", nargs=-1, required=True)
@click.option("--output-dir", "-o", required=True, help="Output directory")
@click.option("--profile", "-p", default="mp4-h264-aac", help="Transcode profile")
@handle_error
def transcode_batch(inputs, output_dir, profile):
    """Batch convert multiple files."""
    results = tc_mod.batch_convert(list(inputs), output_dir, profile=profile)
    output(results)


# ── Playlist Commands ──────────────────────────────────────────
@cli.group()
def playlist():
    """Playlist management commands."""
    pass


@playlist.command("create")
@click.argument("files", nargs=-1, required=True)
@click.option("--output", "-o", required=True, help="Output playlist path (.m3u)")
@click.option("--title", "-t", default=None, help="Playlist title")
@handle_error
def playlist_create(files, output, title):
    """Create an M3U playlist from a list of files."""
    result = pl_mod.create_playlist(list(files), output, title=title)
    output(result)


@playlist.command("parse")
@click.argument("path")
@handle_error
def playlist_parse(path):
    """Parse and display an M3U playlist."""
    result = pl_mod.parse_playlist(path)
    output(result)


@playlist.command("play")
@click.argument("path")
@click.option("--random", "-r", is_flag=True, help="Random order")
@click.option("--loop", is_flag=True, help="Loop playlist")
@click.option("--repeat", is_flag=True, help="Repeat current")
@click.option(
    "--start", "start_index", type=int, default=None, help="Start at track index"
)
@handle_error
def playlist_play(path, random, loop, repeat, start_index):
    """Play a playlist."""
    result = pl_mod.play_playlist(
        path,
        random=random,
        loop=loop,
        repeat=repeat,
        start_index=start_index,
    )
    output(result)


@playlist.command("concat")
@click.argument("files", nargs=-1, required=True)
@click.option("--output", "-o", required=True, help="Output file path")
@click.option("--profile", "-p", default="mp4-h264-aac", help="Transcode profile")
@handle_error
def playlist_concat(files, output, profile):
    """Concatenate multiple media files into one."""
    result = pl_mod.concat(list(files), output, profile=profile)
    output(result)


# ── Stream Commands ─────────────────────────────────────────────
@cli.group()
def stream():
    """Streaming and network output commands."""
    pass


@stream.command("http")
@click.argument("input_path")
@click.option("--port", type=int, default=8080, help="HTTP port")
@click.option("--mux", default="ts", help="Mux format")
@click.option("--address", default="0.0.0.0", help="Bind address")
@handle_error
def stream_http(input_path, port, mux, address):
    """Stream a file over HTTP."""
    result = st_mod.stream_file(input_path, port=port, mux=mux, address=address)
    output(result)


@stream.command("udp")
@click.argument("input_path")
@click.option("--address", default="239.255.12.42", help="Multicast address")
@click.option("--port", type=int, default=1234, help="UDP port")
@click.option("--mux", default="ts", help="Mux format")
@handle_error
def stream_udp(input_path, address, port, mux):
    """Stream a file over UDP multicast."""
    result = st_mod.stream_udp(input_path, address=address, port=port, mux=mux)
    output(result)


@stream.command("rtp")
@click.argument("input_path")
@click.option("--address", default="239.255.12.42", help="RTP address")
@click.option("--port", type=int, default=5004, help="RTP port")
@click.option("--mux", default="ts", help="Mux format")
@handle_error
def stream_rtp(input_path, address, port, mux):
    """Stream a file over RTP."""
    result = st_mod.stream_rtp(input_path, address=address, port=port, mux=mux)
    output(result)


@stream.command("transcode")
@click.argument("input_path")
@click.option("--port", type=int, default=8080, help="HTTP port")
@click.option("--profile", "-p", default="mp4-h264-aac", help="Transcode profile")
@click.option("--address", default="0.0.0.0", help="Bind address")
@handle_error
def stream_transcode(input_path, port, profile, address):
    """Transcode and stream a file over HTTP."""
    result = st_mod.transcode_stream(
        input_path, port=port, profile=profile, address=address
    )
    output(result)


@stream.command("record")
@click.argument("url")
@click.argument("output_path")
@click.option("--duration", "-d", default=None, help="Recording duration")
@click.option("--mux", default="ts", help="Mux format")
@handle_error
def stream_record(url, output_path, duration, mux):
    """Record a network stream to a file."""
    result = st_mod.record_stream(url, output_path, duration=duration, mux=mux)
    output(result)


# ── Session Commands ─────────────────────────────────────────────
@cli.group()
def session():
    """Session management commands."""
    pass


@session.command("status")
@handle_error
def session_status():
    """Show session status."""
    sess = get_session()
    output(sess.status())


@session.command("undo")
@handle_error
def session_undo():
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"undone": desc}, f"Undone: {desc}")


@session.command("redo")
@handle_error
def session_redo():
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"redone": desc}, f"Redone: {desc}")


@session.command("history")
@handle_error
def session_history():
    """Show undo history."""
    sess = get_session()
    history = sess.list_history()
    output(history, "Undo history:")


# ── REPL ─────────────────────────────────────────────────────────
@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.vlc.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("vlc", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "probe": "info|formats",
        "playback": "play|screenshot|record|extract-audio",
        "transcode": "convert|resize|profiles|profile-info|batch",
        "playlist": "create|parse|play|concat",
        "stream": "http|udp|rtp|transcode|record",
        "session": "status|undo|redo|history",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            try:
                args = shlex.split(line)
            except ValueError:
                args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry Point ──────────────────────────────────────────────────
def main():
    cli()


if __name__ == "__main__":
    main()
