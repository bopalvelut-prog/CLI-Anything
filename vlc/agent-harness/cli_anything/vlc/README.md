# cli-anything-vlc

A stateful command-line interface for media operations, built on VLC. Designed for AI agents and power users who need to transcode, stream, capture, and analyze media files without a GUI.

## Features

- **Probe** — Analyze media files (codec, duration, resolution, bitrate)
- **Transcode** — Convert between 13+ profiles (H.264, H.265, VP8, VP9, MP3, FLAC, etc.)
- **Playback** — Play, screenshot, record segments, extract audio
- **Playlist** — Create, parse, play, and concatenate M3U playlists
- **Stream** — HTTP, UDP multicast, and RTP streaming
- **Batch** — Convert multiple files in one command
- **JSON output** — Machine-readable output with `--json` flag
- **REPL** — Interactive session with undo/redo history

## Installation

```bash
cd agent-harness
pip install -e .
```

## Quick Start

```bash
# Probe a media file
cli-anything-vlc probe info video.mp4

# Convert video to WebM
cli-anything-vlc transcode convert video.mp4 output.webm --profile webm-vp9-opus

# Extract audio
cli-anything-vlc playback extract-audio video.mp4 audio.mp3

# Take a screenshot at 1:30
cli-anything-vlc playback screenshot video.mp4 frame.png --time 00:01:30

# Stream over HTTP
cli-anything-vlc stream http video.mp4 --port 8080
```
