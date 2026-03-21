# Test Plan: CLI-Anything FFmpeg Harness

## Overview
Test suite for the FFmpeg CLI harness covering unit tests (mocked) and E2E tests (real ffmpeg).

## Test Categories

### Unit Tests (test_core.py)
Tests with mocked subprocess calls — no ffmpeg required.

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestTimeParsing | 4 | HH:MM:SS, MM:SS, seconds, invalid |
| TestProgressParsing | 4 | Valid progress, empty, non-progress, to_dict |
| TestPresets | 8 | List, get, web-hd, gif, audio-only, copy, invalid |
| TestFFmpegResult | 2 | Success/error to_dict |
| TestFilterModule | 6 | List filters, video/audio types, build scale/volume, unknown |
| TestSession | 7 | Record/history, undo/redo, empty undo/redo, status, clear, save/load |

**Total: 31 unit tests**

### E2E Tests (test_full_e2e.py)
Tests with real ffmpeg — requires ffmpeg installed.

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestProbeE2E | 5 | Streams, format, duration, codecs, summary |
| TestTranscodeE2E | 3 | Basic convert, CRF, preset |
| TestFilterE2E | 2 | Scale, volume |
| TestConcatE2E | 2 | Join, trim |
| TestExtractE2E | 3 | Audio, video, thumbnail |
| TestCLIIntegrationE2E | 3 | CLI probe JSON, CLI convert, CLI thumbnail |

**Total: 18 E2E tests**

## Running Tests

```bash
# Unit tests only
python -m pytest cli_anything/ffmpeg/tests/test_core.py -v

# E2E tests (requires ffmpeg)
python -m pytest cli_anything/ffmpeg/tests/test_full_e2e.py -v

# All tests
python -m pytest cli_anything/ffmpeg/tests/ -v
```

## Test Requirements
- Python >= 3.10
- pytest (for test runner)
- ffmpeg installed and in PATH (for E2E tests)
- click (for CLI integration tests)

## Test Results
(To be filled after first run)

| Date | Unit | E2E | Total | Status |
|------|------|-----|-------|--------|
| TBD | TBD | TBD | TBD | TBD |
