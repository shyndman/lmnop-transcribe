# Progress: LMNOP Transcribe

## What Works

-   Basic application structure with trigger handling and audio recording components.
-   Start trigger detection using Caps Lock press.
-   Audio recording and saving to a WAV file.
-   Stop trigger event is eventually received and detected by the application.
-   Non-blocking file writing using `loop.run_in_executor` has been implemented (although it did not resolve the trigger responsiveness issue).
-   Temporary audio bypass for testing confirmed audio recording is the source of trigger delay.
-   `aiodebug` has been installed and integrated into `__main__.py` for performance monitoring.

## What's Left to Build

-   Refactoring the audio recording and processing to run in a separate process using `multiprocessing`.
-   Implementing inter-process communication (IPC) using `multiprocessing.Event` for start/stop signaling.
-   Integrating the multiprocessing audio handling with the existing trigger logic in `recorder.py`.
-   Testing the application with the multiprocessing implementation to confirm improved stop trigger responsiveness.
-   Implementing the transcription logic (currently a placeholder).
-   Implementing user feedback mechanisms (sounds and notifications are present but need full integration).

## Current Status

The primary issue of the unresponsive stop trigger has been diagnosed. It is caused by the audio recording process interfering with the main process's ability to promptly handle `evdev` events. The plan to address this by using `multiprocessing` for audio handling has been agreed upon.

## Known Issues

-   Delayed and batched processing of `evdev` events when audio recording is active, leading to an unresponsive stop trigger. The `playSound` function, specifically the execution of `pw-play` within it, has been identified as the direct cause of this delay.
-   A Pylance error in `recorder.py` related to `asyncio.create_task` (potential false positive or secondary issue).
-   Log inconsistencies (duplicate messages with different timestamp formats).

## Evolution of Project Decisions

-   Initial focus on a single-process asyncio architecture.
-   Debugging revealed event loop blocking due to audio recording.
-   Attempted non-blocking file writing as a potential solution (did not resolve the issue).
-   Identified multiprocessing as the necessary architectural change to isolate audio handling and resolve trigger responsiveness.
-   Discovered that the `playSound` function is the direct cause of the event processing delay.
-   Decided to use `aiodebug` to further diagnose the event loop performance and the interaction with `playSound`.
