# VLC: Project-Specific Analysis & SOP

## Architecture Summary

VLC (VideoLAN Client) is a cross-platform multimedia player and framework built on
**libVLC** — a portable multimedia engine with a modular architecture.

```
┌──────────────────────────────────────────────┐
│                   VLC GUI                    │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │  Qt/GTK  │ │ Playlist │ │  Controls   │  │
│  │  Interface│ │ Manager  │ │   (Qt)      │  │
│  └────┬──────┘ └────┬─────┘ └──────┬──────┘  │
│       │             │              │          │
│  ┌────┴─────────────┴──────────────┴───────┐ │
│  │            libVLC Core                  │ │
│  │  Module loading, input/output, codec    │ │
│  └─────────────────┬───────────────────────┘ │
└────────────────────┼─────────────────────────┘
                     │
         ┌───────────┴──────────────────┐
         │  Plugin Modules              │
         │  ├── codecs (h264, vp8, ...) │
         │  ├── demuxers (mp4, mkv, ..) │
         │  ├── outputs (alsa, pulse)   │
         │  ├── filters (deinterlace)   │
         │  └── access (http, file, ..) │
         └──────────────────────────────┘
```

## CLI Strategy: cvlc + sout chains

VLC's command-line interface (`cvlc` — console VLC) provides powerful media
operations without a GUI. Our strategy:

1. **cvlc** — Headless VLC for all operations (transcoding, playback, streaming)
2. **sout chains** — VLC's output chain syntax for transcoding/streaming pipelines
3. **--verbose parsing** — Extract media info from VLC's debug output
4. **M3U playlists** — Standard playlist format for batch/concat operations

### Why cvlc?

- Available on all platforms (Linux, macOS, Windows)
- Supports 100+ input formats and 50+ output formats
- Built-in transcoding with configurable codecs, bitrates, resolution
- HTTP/UDP/RTP streaming out of the box
- No external dependencies beyond VLC itself

## Command Map: GUI Action -> CLI Command

| GUI Action | CLI Command |
|-----------|-------------|
| Media -> Open File | `playback play <file>` |
| Playback -> Speed | `playback play <file> --rate 1.5` |
| Video -> Take Snapshot | `playback screenshot <file> <out> --time 00:01:30` |
| Media -> Convert/Save | `transcode convert <in> <out> --profile mp4-h264-aac` |
| Media -> Convert -> Audio Only | `playback extract-audio <in> <out>` |
| Tools -> Media Information | `probe info <file>` |
| Media -> Open Network Stream | `stream http <file>` |
| Media -> Save Playlist | `playlist create <files> -o list.m3u` |

## Transcode Profiles

| Profile | Container | Video | Audio | Use Case |
|---------|-----------|-------|-------|----------|
| mp4-h264-aac | MP4 | H.264 | AAC | Universal playback |
| mp4-h265-aac | MP4 | H.265 | AAC | Better compression |
| webm-vp9-opus | WebM | VP9 | Opus | Modern web |
| ts-h264-aac | MPEG-TS | H.264 | AAC | Broadcasting |
| mp3-192k | - | - | MP3 192k | Audio extraction |
| flac-lossless | - | - | FLAC | Archival audio |

## sout Chain Syntax

VLC uses `--sout` chains for output pipelines:

```
#transcode{vcodec=h264,vb=2000,acodec=mp4a,ab=192}:standard{access=file,mux=mp4,dst=output.mp4}
```

Components:
- `#transcode{...}` — Transcode filter with codec/bitrate settings
- `:standard{...}` — Output sink (file, http, udp, etc.)
- `mux` — Container format (mp4, mkv, ts, webm, ogg)
- `access` — Output method (file, http, udp, rtp)

## MRL (Media Resource Locator) Syntax

```
file:///path/to/file         Local file
http://host[:port]/file      HTTP stream
ftp://host[:port]/file       FTP
mms://host[:port]/file       MMS stream
screen://                    Screen capture
dvd://[device]               DVD
vcd://[device]               VCD
cdda://[device]              Audio CD
udp://[@addr][:port]         UDP stream
vlc://pause:<seconds>        Pause in playlist
vlc://quit                   Quit after this item
```

## Supported Formats

### Input
Video: MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, TS, VOB, OGV, 3GP
Audio: MP3, OGG, FLAC, WAV, AAC, WMA, M4A, OPUS, AIFF, AC3
Stream: HTTP, HTTPS, RTSP, RTMP, UDP, RTP, MMS
Disc: DVD, VCD, CDDA, Blu-ray

### Output
Video: MP4, MKV, AVI, WebM, TS, FLV, OGG
Audio: MP3, OGG, FLAC, WAV, AAC, OPUS

## Test Coverage Plan

1. **Unit tests** (`test_core.py`): No VLC required
   - Session create/status/undo/redo
   - Profile listing and validation
   - sout chain construction
   - Format listing
   - Utility functions

2. **E2E tests** (`test_full_e2e.py`): Requires VLC
   - Media probing
   - Audio transcoding (WAV -> MP3)
   - Playlist create/parse
   - Screenshot capture

## Rendering Gap Assessment: **Low**

VLC's CLI is extremely capable. Almost all GUI operations have direct CLI
equivalents. The main gaps are:
- No built-in video editing (trimming is time-based, not frame-accurate)
- Limited filter controls compared to GUI's full filter chain UI
- Some advanced features (e.g., custom equalizer) require Lua scripting
