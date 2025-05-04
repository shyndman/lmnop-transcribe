# Progress: LMNOP Transcribe

## What Works

-   Basic application structure with trigger handling and audio recording components.
-   Start trigger detection using Caps Lock press.
-   Audio recording and saving to a WAV file.
-   Stop trigger event is now responsive during audio recording.
-   Non-blocking file writing using `loop.run_in_executor` has been implemented.
-   The post-recording processing (cleanup, transcription, pasting) is correctly integrated into the main application loop in `recorder.py`.
-   `aiodebug` has been installed and integrated into `__main__.py` for performance monitoring.
-   The Pylance error related to the `clippaste` subprocess call in `recorder.py` has been addressed.
-   Added logging for time elapsed during audio recording.
-   Added timing measurements for external calls (SoX, transcription, clipboard paste).
-   Implemented multiprocessing for audio handling to resolve trigger responsiveness issues.
-   Completed integration with the Wyoming server for Speech-to-Text (STT).
-   Completed the transcription functionality.
-   Completed user feedback mechanisms.

## What's Left to Build

Nothing is left to build.

## Current Status

All core features of the LMNOP Transcribe project have been implemented.

## Known Issues

None

## Evolution of Project Decisions

-   Initial focus on a single-process asyncio architecture.
-   Debugging revealed event loop blocking due to audio recording.
-   Attempted non-blocking file writing as a potential solution (did not resolve the issue).
-   Identified multiprocessing as a potential architectural change to isolate audio handling and resolve trigger responsiveness.
-   Discovered that the `playSound` function, specifically the execution of `pw-play` within it, was a significant source of event processing delay when run concurrently with audio recording.
-   Resolved the immediate trigger responsiveness issue by removing the start noise in `playSound`.
-   Refactored the application flow to integrate post-recording steps into the main recording loop.
-   Addressed a Pylance error related to the `clippaste` subprocess call.
-   Implemented multiprocessing for audio handling.
-   Completed integration with the Wyoming server for Speech-to-Text (STT).
-   Completed the transcription functionality.
-   Completed user feedback mechanisms.
