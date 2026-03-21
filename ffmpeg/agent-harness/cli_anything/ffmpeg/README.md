"""CLI-Anything FFmpeg harness README.

Installation:
    cd ffmpeg/agent-harness
    pip install -e .

Usage:
    cli-anything-ffmpeg [COMMAND] [OPTIONS]

    Interactive REPL:
        cli-anything-ffmpeg

    Probe a file:
        cli-anything-ffmpeg probe info input.mp4
        cli-anything-ffmpeg probe streams input.mp4 --json

    Transcode:
        cli-anything-ffmpeg transcode convert input.avi -o output.mp4 --preset web-hd
        cli-anything-ffmpeg transcode convert input.mp4 -o output.mp4 -vc libx264 -crf 23

    Filter:
        cli-anything-ffmpeg filter apply input.mp4 -o out.mp4 --scale 1280x720
        cli-anything-ffmpeg filter apply input.mp4 -o out.mp4 --vf "eq=brightness=0.1"

    Concat:
        cli-anything-ffmpeg concat join part1.mp4 part2.mp4 -o merged.mp4
        cli-anything-ffmpeg concat trim input.mp4 -o clip.mp4 --start 00:01:00 --end 00:02:00
        cli-anything-ffmpeg concat split input.mp4 -o segments/ --segment-duration 60

    Extract:
        cli-anything-ffmpeg extract audio input.mp4 -o audio.aac
        cli-anything-ffmpeg extract video input.mp4 -o video.mp4
        cli-anything-ffmpeg extract thumbnail input.mp4 -o thumb.jpg --time 00:00:30

    Export (preset-based):
        cli-anything-ffmpeg export render input.mp4 -o out.mp4 --preset web-hd

    Session:
        cli-anything-ffmpeg session status
        cli-anything-ffmpeg session history --limit 10
        cli-anything-ffmpeg session undo

    Info:
        cli-anything-ffmpeg version
        cli-anything-ffmpeg codecs --json
        cli-anything-ffmpeg formats --json
        cli-anything-ffmpeg filters --json

JSON Output:
    All commands support --json for machine-readable output.
    Use 'json' in REPL to toggle.

Presets:
    web-hd      — 1080p H.264 for web
    web-4k      — 4K H.264
    web-hd-h265 — 1080p H.265/HEVC
    gif         — Animated GIF (480p, 15fps)
    audio-only  — Extract as AAC
    mp3         — Extract as MP3
    thumbnail   — Single frame JPEG
    copy        — Stream copy (no re-encoding)

Requirements:
    - Python >= 3.10
    - ffmpeg installed and in PATH
    - click >= 8.0
    - prompt-toolkit >= 3.0
"""

__version__ = "1.0.0"
