# Progress: LMNOP Transcribe

## What Works

-   Created systemd user service file and installation script for deployment.
-   Confirmed that `WorkingDirectory` in the systemd service file sets the execution directory for `ExecStart`.
-   Included stopping the service in the installation script for idempotency.
-   Basic application structure with trigger handling and audio recording components.
-   Start trigger detection using Caps Lock press.
-   Stop trigger event is now responsive during audio recording due to multiprocessing.
-   Implemented multiprocessing for audio handling.
-   Implemented the streaming audio pipeline using `multiprocessing.Queue` for inter-process communication.
-   Implemented manual trimming of a configurable duration from the beginning of the audio stream in the audio recording process.
-   Adapted the transcriber to receive audio chunks from a queue and stream to the Wyoming server.
-   Removed SoX dependencies and related code/configuration.
-   Completed integration with the Wyoming server for Speech-to-Text (STT).
-   Completed the transcription functionality.
-   Completed user feedback mechanisms.
-   Added configurable trim duration to `config.toml`.
-   Corrected type hinting for multiprocessing queues in `recorder.py`.

## What's Left to Build

- Implement automatic recording cancellation based on duration threshold (re-evaluate how this fits with the streaming approach).
- Add user feedback for cancelled recordings.
- Refine error handling and edge case management in the streaming pipeline (e.g., what happens if the Wyoming server disconnects mid-stream).
- Re-evaluate the minimum recording duration check and decide where it should be implemented in the new pipeline.

## Current Status

The core streaming audio pipeline with manual trimming is implemented. Deployment files for a user systemd service have been created, and D-Bus signaling has been implemented.

## Known Issues

-   Pylance errors in `multiprocessing/queues.py` related to static analysis of multiprocessing queues (likely not runtime bugs in project code).

## Evolution of Project Decisions

-   Decision to deploy as a user systemd service for background execution.
-   Refinement of the systemd service file `ExecStart` command based on `WorkingDirectory` behavior.
-   Development of an installation script to automate service deployment, including idempotency for stopping the service.
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
-   Decision to move from file-based audio processing to a streaming pipeline using `multiprocessing.Queue`.
-   Decision to perform manual trimming of initial audio bytes instead of using SoX/pysox.
-   Challenges encountered with using `replace_in_file` for complex code modifications, requiring fallback to `write_to_file`.
-   Refinement of type hinting for multiprocessing queues based on static analysis feedback.
-   Decision to remove "dumb comments" to improve code clarity and adhere to styling rules.
