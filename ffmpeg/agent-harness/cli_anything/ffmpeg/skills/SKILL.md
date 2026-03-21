---
name: cli-anything-ffmpeg
version: 1.0.0
description: CLI-Anything harness for FFmpeg — make ffmpeg agent-native
system_package: ffmpeg
install_cmd: apt install ffmpeg
entry_point: cli-anything-ffmpeg
category: video
---

# CLI-Anything FFmpeg

FFmpeg CLI harness that structures FFmpeg's complex CLI into discoverable, composable subcommands with JSON output, session state, and undo/redo.

## Installation

```bash
# Install system dependency
apt install ffmpeg    # Ubuntu/Debian
brew install ffmpeg   # macOS

# Install the harness
cd ffmpeg/agent-harness
pip install -e .
```

## Usage

### Interactive REPL
```bash
cli-anything-ffmpeg
```

### Probe Media Files
```bash
# Get file summary
cli-anything-ffmpeg probe info input.mp4 --json

# List streams
cli-anything-ffmpeg probe streams input.mp4

# Get duration
cli-anything-ffmpeg probe duration input.mp4 --json
```

### Transcode
```bash
# Convert with preset
cli-anything-ffmpeg transcode convert input.avi -o output.mp4 --preset web-hd

# Convert with specific codec
cli-anything-ffmpeg transcode convert input.mp4 -o out.mp4 -vc libx264 -crf 23 -ac aac
```

### Filters
```bash
# Scale video
cli-anything-ffmpeg filter apply input.mp4 -o out.mp4 --scale 1280x720

# Adjust volume
cli-anything-ffmpeg filter apply input.mp4 -o out.mp4 --volume 1.5

# Raw filter string
cli-anything-ffmpeg filter apply input.mp4 -o out.mp4 --vf "eq=brightness=0.1"
```

### Concatenation
```bash
# Join files
cli-anything-ffmpeg concat join part1.mp4 part2.mp4 -o merged.mp4

# Trim
cli-anything-ffmpeg concat trim input.mp4 -o clip.mp4 --start 00:01:00 --end 00:02:00

# Split
cli-anything-ffmpeg concat split input.mp4 -o segments/ --segment-duration 60
```

### Extract
```bash
# Extract audio
cli-anything-ffmpeg extract audio input.mp4 -o audio.aac

# Extract thumbnail
cli-anything-ffmpeg extract thumbnail input.mp4 -o thumb.jpg --time 00:00:30
```

### Session (Undo/Redo)
```bash
cli-anything-ffmpeg session status
cli-anything-ffmpeg session history --limit 10
cli-anything-ffmpeg session undo
cli-anything-ffmpeg session redo
```

## Command Groups

| Group | Description |
|-------|-------------|
| `probe` | Analyze media files (streams, codecs, metadata) |
| `transcode` | Convert between formats with presets |
| `filter` | Apply video/audio filters |
| `concat` | Join, trim, split operations |
| `extract` | Extract audio, video, thumbnails |
| `export` | Render with named presets |
| `session` | Undo/redo with command history |

## Presets

| Preset | Description |
|--------|-------------|
| `web-hd` | 1080p H.264 for web |
| `web-4k` | 4K H.264 |
| `web-hd-h265` | 1080p H.265/HEVC |
| `gif` | Animated GIF (480p, 15fps) |
| `audio-only` | Extract as AAC |
| `mp3` | Extract as MP3 |
| `thumbnail` | Single frame JPEG |
| `copy` | Stream copy (no re-encoding) |

## JSON Output

All commands support `--json` for machine-readable output:

```bash
cli-anything-ffmpeg probe info input.mp4 --json
```

```json
{
  "file": "input.mp4",
  "format": "QuickTime / MOV",
  "duration": "120.5",
  "video": {
    "codec": "h264",
    "width": 1920,
    "height": 1080,
    "fps": "30/1"
  }
}
```

## For AI Agents

- Use `--json` flag for structured output
- Use `probe info` to understand input files before processing
- Use `session undo` to revert mistakes
- Presets provide safe defaults for common operations
- All operations are idempotent when output paths don't exist
