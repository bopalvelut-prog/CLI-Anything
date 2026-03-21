---
name: >-
  cli-anything-vlc
description: >-
  Command-line interface for VLC - Media playback, transcoding, streaming,
  screenshot capture, and audio extraction via cvlc...
---

# cli-anything-vlc

A stateful command-line interface for media operations, built on VLC. Designed for AI agents and power users who need to transcode, stream, capture, and analyze media files.

## Installation

```bash
pip install cli-anything-vlc
```

**Prerequisites:**
- Python 3.10+
- VLC must be installed (`apt install vlc`)

## Command Groups

### Probe

| Command | Description |
|---------|-------------|
| `info` | Probe a media file (codec, duration, resolution, bitrate) |
| `formats` | List supported formats and transcode profiles |

### Playback

| Command | Description |
|---------|-------------|
| `play` | Play a media file |
| `screenshot` | Capture a frame at a specific time |
| `record` | Record/trim a segment |
| `extract-audio` | Extract audio track to MP3/OGG/FLAC/WAV |

### Transcode

| Command | Description |
|---------|-------------|
| `convert` | Convert using a profile (mp4-h264-aac, webm-vp9-opus, etc.) |
| `resize` | Resize video to specific dimensions |
| `profiles` | List available transcode profiles |
| `profile-info` | Show profile details |
| `batch` | Batch convert multiple files |

### Playlist

| Command | Description |
|---------|-------------|
| `create` | Create an M3U playlist |
| `parse` | Parse and display a playlist |
| `play` | Play a playlist |
| `concat` | Concatenate multiple files |

### Stream

| Command | Description |
|---------|-------------|
| `http` | Stream over HTTP |
| `udp` | Stream over UDP multicast |
| `rtp` | Stream over RTP |
| `transcode` | Transcode and stream over HTTP |
| `record` | Record a network stream |

### Session

| Command | Description |
|---------|-------------|
| `status` | Show session status |
| `undo` | Undo last operation |
| `redo` | Redo last undone operation |
| `history` | Show undo history |

## Examples

```bash
# Probe a file
cli-anything-vlc --json probe info video.mp4

# Convert to WebM with VP9/Opus
cli-anything-vlc transcode convert input.mp4 output.webm --profile webm-vp9-opus

# Extract audio as FLAC
cli-anything-vlc playback extract-audio concert.mkv audio.flac --codec flac

# Screenshot at 90 seconds
cli-anything-vlc playback screenshot movie.mp4 thumb.png --time 90

# Batch convert all MKVs to MP4
cli-anything-vlc transcode batch *.mkv --output-dir converted/ --profile mp4-h264-aac

# Stream over HTTP
cli-anything-vlc stream http video.mp4 --port 8080
```

## Version

1.0.0
