# FFmpeg: Software SOP Analysis

## Overview
FFmpeg is a complete, cross-platform solution for recording, converting and streaming audio and video. It includes libavcodec - the leading audio/video codec library. FFmpeg is CLI-native, making it an ideal candidate for CLI-Anything as there is no GUI to wrap.

## Key Components

### 1. FFmpeg (Main Encoder/Decoder)
- **Purpose**: Audio/video processing, transcoding, filtering
- **CLI Interface**: `ffmpeg [options] [[infile options] -i infile]... {[outfile options] outfile}...`
- **Key Features**:
  - Format conversion (container and codec)
  - Video/audio filtering (scale, crop, overlay, eq, etc.)
  - Stream manipulation (map, copy, select)
  - Metadata handling
  - Hardware acceleration support

### 2. FFprobe (Media Analyzer)
- **Purpose**: Stream analysis, metadata extraction
- **CLI Interface**: `ffprobe [options] input_file`
- **Key Features**:
  - Stream information (codec, duration, bitrate)
  - Container format analysis
  - Frame-level analysis
  - JSON/XML output support

### 3. Common Workflows

#### Transcoding
```bash
# Basic format conversion
ffmpeg -i input.avi output.mp4

# Specific codec
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4

# Quality control
ffmpeg -i input.mp4 -crf 23 output.mp4
```

#### Filtering
```bash
# Scale video
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4

# Crop
ffmpeg -i input.mp4 -vf "crop=640:480:100:100" output.mp4

# Multiple filters
ffmpeg -i input.mp4 -vf "scale=1280:720,eq=brightness=0.06" output.mp4
```

#### Stream Operations
```bash
# Extract audio
ffmpeg -i input.mp4 -vn -acodec copy output.aac

# Extract video
ffmpeg -i input.mp4 -an -vcodec copy output.mp4

# Concatenate
ffmpeg -f concat -i filelist.txt -c copy output.mp4
```

## CLI Architecture for CLI-Anything

### Command Groups
1. **probe** - Media analysis using ffprobe
2. **transcode** - Format conversion with presets
3. **filter** - Video/audio filter chains
4. **concat** - Join, trim, split operations
5. **extract** - Stream extraction (audio, video, subtitles)
6. **session** - Undo/redo with command history
7. **export** - Preset-based rendering

### State Model
- **Stateless**: Each ffmpeg invocation is independent
- **Session Tracking**: Command history for undo/redo (no project files)
- **Progress**: Parse ffmpeg stderr for time progress

### Output Formats
- **Human-readable**: Default with progress bars and status
- **JSON**: Structured output for all commands via `--json`

## Key Parameters Reference

### Input Options
- `-i <file>`: Input file
- `-ss <time>`: Seek start time
- `-t <time>`: Duration
- `-frames:v <n>`: Number of video frames

### Output Options
- `-c:v <codec>`: Video codec
- `-c:a <codec>`: Audio codec
- `-b:v <bitrate>`: Video bitrate
- `-b:a <bitrate>`: Audio bitrate
- `-r <fps>`: Frame rate
- `-s <WxH>`: Frame size

### Filter Syntax
- `-vf <filtergraph>`: Video filter
- `-af <filtergraph>`: Audio filter
- Filter syntax: `filter1=param1=val1:param2=val2,filter2=...`

### Common Codecs
- **Video**: libx264, libx265, libvpx-vp9, h264_nvenc
- **Audio**: aac, libmp3lame, libopus, flac
- **Containers**: mp4, mkv, avi, webm, mov

## Testing Strategy

### Unit Tests
- Mock subprocess calls to ffmpeg/ffprobe
- Test argument construction
- Test JSON output parsing
- Test filter graph building

### E2E Tests
- Real ffmpeg invocations
- Test with sample media files
- Verify output files exist and are valid
- Test progress parsing

### Edge Cases
- Missing ffmpeg installation
- Invalid input files
- Codec not available
- Hardware acceleration fallbacks

## Critical Considerations

1. **Progress Parsing**: FFmpeg outputs progress to stderr with format `time=HH:MM:SS.ms`
2. **Error Handling**: FFmpeg returns non-zero on error, stderr contains error message
3. **Filter Syntax**: Complex filtergraphs need careful escaping
4. **Hardware Acceleration**: Different flags for different GPU vendors (NVENC, QSV, VAAPI)
5. **Streaming**: RTMP, HLS, DASH require specific protocol options

## Implementation Notes

### Backend Wrapper Pattern
```python
# Simplified wrapper pattern
def run_ffmpeg(input_file, output_file, options):
    cmd = ["ffmpeg", "-i", input_file] + options + [output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise FFmpegError(result.stderr)
    return result
```

### Progress Extraction
```python
# Parse stderr for progress
def parse_progress(stderr_line):
    if "time=" in stderr_line:
        time_str = stderr_line.split("time=")[1].split(" ")[0]
        return time_str
    return None
```

### JSON Output from FFprobe
```bash
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

This analysis provides the foundation for building a comprehensive FFmpeg CLI harness that structures FFmpeg's complex CLI into discoverable, composable subcommands with JSON output, session state, and undo/redo capabilities.