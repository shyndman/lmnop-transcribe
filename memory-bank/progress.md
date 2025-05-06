# Progress: LMNOP Transcribe

## What Works

-   Implemented immediate audio streaming by running the synchronous transcription function concurrently in a thread pool using `asyncio.get_event_loop().run_in_executor`.
-   Refactored handler functions (`handle_stop`, `handle_cancel`) using a new asynchronous helper function `_stop_recording_process`.
-   Awaited concurrent audio process and transcription tasks using `asyncio.gather`.
-   Used asynchronous subprocess (`asyncio.create_subprocess_exec`) for pasting transcribed text.
-   Removed unnecessary local variable assignments in handler functions.
-   Removed dumb comments from `recorder.py`.
-   Fixed Pylance type hinting errors related to `asyncio.gather` results.
-   Removed unused async streaming function from `transcriber.py`.
-   Created systemd user service file and installation script for deployment. (Keeping previous relevant points)
-   Confirmed that `WorkingDirectory` in the systemd service file sets the execution directory for `ExecStart`. (Keeping previous relevant points)
-   Included stopping the service in the installation script for idempotency. (Keeping previous relevant points)
-   Basic application structure with trigger handling and audio recording components. (Keeping previous relevant points)
-   Start trigger detection using Caps Lock press. (Keeping previous relevant points)
-   Stop trigger event is now responsive during audio recording due to multiprocessing. (Keeping previous relevant points)
-   Implemented multiprocessing for audio handling. (Keeping previous relevant points)
-   Implemented the streaming audio pipeline using `multiprocessing.Queue` for inter-process communication. (Keeping previous relevant points)
-   Implemented manual trimming of a configurable duration from the beginning of the audio stream in the audio recording process. (Keeping previous relevant points)
-   Adapted the transcriber to receive audio chunks from a queue and stream them incrementally to the Wyoming server. (Keeping previous relevant points)
-   Removed SoX dependencies and related code/configuration. (Keeping previous relevant points)
-   Completed integration with the Wyoming server for Speech-to-Text (STT). (Keeping previous relevant points)
-   Completed the transcription functionality. (Keeping previous relevant points)
-   Completed user feedback mechanisms. (Keeping previous relevant points)
-   Added configurable trim duration to `config.toml`. (Keeping previous relevant points)
-   Corrected type hinting for multiprocessing queues in `recorder.py`. (Keeping previous relevant points)


## What's Left to Build

- Implement automatic recording cancellation based on duration threshold (re-evaluate how this fits with the streaming approach).
- Add user feedback for cancelled recordings.
- Refine error handling and edge case management in the streaming pipeline (e.g., what happens if the Wyoming server disconnects mid-stream).
- Re-evaluate the minimum recording duration check and decide where it should be implemented in the new pipeline.

## Current Status

The immediate audio streaming pipeline is implemented and refined. Code quality improvements have been made by refactoring handlers, using asynchronous subprocesses, and removing unnecessary code/comments. Deployment files for a user systemd service have been created, and D-Bus signaling has been implemented.

## Known Issues

-   Pylance errors in `multiprocessing/queues.py` related to static analysis of multiprocessing queues (likely not runtime bugs in project code).

## Evolution of Project Decisions

-   Decision to implement immediate audio streaming by running the existing synchronous transcription function (`transcribe_audio_with_wyoming`) in a thread pool using `asyncio.get_event_loop().run_in_executor` concurrently with the audio recording process.
-   Decision to use `asyncio.gather` with `return_exceptions=True` to await concurrent tasks and handle potential exceptions in the main process.
-   Decision to use `asyncio.create_subprocess_exec` for asynchronous execution of the `ydotool` command in `paste_transcribed_text`.
-   Decision to remove unnecessary local variable assignments in handler functions for clarity.
-   Decision to remove dumb comments based on code style rules to improve readability.
-   Decision to deploy as a user systemd service for background execution. (Keeping previous relevant decisions)
-   Refinement of the systemd service file `ExecStart` command based on `WorkingDirectory` behavior. (Keeping previous relevant decisions)
-   Development of an installation script to automate service deployment, including idempotency for stopping the service. (Keeping previous relevant decisions)
-   Initial focus on a single-process asyncio architecture. (Keeping previous relevant decisions)
-   Debugging revealed event loop blocking due to audio recording. (Keeping previous relevant decisions)
-   Attempted non-blocking file writing as a potential solution (did not resolve the issue). (Keeping previous relevant decisions)
-   Identified multiprocessing as a potential architectural change to isolate audio handling and resolve trigger responsiveness. (Keeping previous relevant decisions)
-   Discovered that the `playSound` function, specifically the execution of `pw-play` within it, was a significant source of event processing delay when run concurrently with audio recording. (Keeping previous relevant decisions)
-   Resolved the immediate trigger responsiveness issue by removing the start noise in `playSound`. (Keeping previous relevant decisions)
-   Refactored the application flow to integrate post-recording steps into the main recording loop. (Keeping previous relevant decisions)
-   Addressed a Pylance error related to the `clippaste` subprocess call. (Keeping previous relevant decisions)
-   Implemented multiprocessing for audio handling. (Keeping previous relevant decisions)
-   Completed integration with the Wyoming server for Speech-to-Text (STT). (Keeping previous relevant decisions)
-   Completed the transcription functionality. (Keeping previous relevant decisions)
-   Completed user feedback mechanisms. (Keeping previous relevant decisions)
-   Decision to move from file-based audio processing to a streaming pipeline using `multiprocessing.Queue`. (Keeping previous relevant decisions)
-   Decision to perform manual trimming of initial audio bytes instead of using SoX/pysox. (Keeping previous relevant decisions)
-   Challenges encountered with using `replace_in_file` for complex code modifications, requiring fallback to `write_to_file`. (Keeping previous relevant decisions)
-   Refinement of type hinting for multiprocessing queues based on static analysis feedback. (Keeping previous relevant decisions)
-   Decision to remove "dumb comments" to improve code clarity and adhere to styling rules. (Keeping previous relevant decisions)
