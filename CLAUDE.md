# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This project uses a Python virtual environment. Before running any Python code or tests, activate the virtual environment:

```bash
source .venv/bin/activate
```

## Running Tests

To run the test suite:

```bash
source .venv/bin/activate
python -m pytest test_pipeline.py -v
uv run pytest tests/
```

## Running the Project

To run the project, activate the venv and run `uv run transcribe`

## Project Overview

This project is for building an audio transcription pipeline using RxPY (ReactiveX for Python). The `pipeline_in_ts.ts` file serves as a reference implementation written in TypeScript/RxJS that demonstrates the desired reactive architecture and flow.

## Architecture (Target Implementation)

The system will be a reactive pipeline handling:

- Audio recording control via keyboard events (play/stop/cancel)
- Real-time audio chunk buffering during recording sessions
- Audio processing (trimming, optional WAV file export)
- Integration with transcription services
- Result publishing via D-Bus notifications

## Key RxPY Patterns to Implement

Based on the TypeScript reference:

1. **Event Mapping**: Transform keyboard events to control commands
2. **State Management**: Track recording state with `scan()` operator using TypedDict
3. **Conditional Streaming**: Use `switchMap()` for session-based processing
4. **Audio Buffering**: Implement `buffer()` with timing constraints
5. **Cancellation**: Use `take_until()` for cleanup and cancellation
6. **Side Effects**: Handle notifications and D-Bus publishing with `tap()`

## Type Safety

The implementation uses TypedDict for state management:

- `RecordingState`: Tracks recording status, timestamps, and actions
- `ProcessedRecording`: Final recording output with trimmed audio chunks
- All timestamps are delta-based (milliseconds from session/recording start)

## Configuration Structure

The system should support:
- `save_wav_files`: Boolean for WAV file output
- `trim_duration_ms`: Initial audio trimming amount
- `minimum_recording_ms`: Minimum viable recording length

## RxPY Documentation

The `docs/` folder contains comprehensive RxPY documentation covering:
- Core concepts (Observable, Observer, operators)
- Operator chaining and custom operators
- Concurrency with ThreadPoolScheduler and AsyncIOScheduler
- Testing patterns for reactive code
- Migration notes from previous versions

## Development Approach

When implementing the Python version:
1. Reference the TypeScript implementation for reactive flow patterns
2. Use RxPY equivalents for RxJS operators (`pipe()`, `map()`, `filter()`, etc.)
3. Implement Python-specific audio handling and D-Bus integration
4. Follow the concurrency patterns documented in the RxPY guide