# System Patterns: LMNOP Transcribe

## Current Architecture: Multiprocessing with Streaming Pipeline

The application now follows a multiprocessing architecture with a streaming audio pipeline.

-   **Main Process:** Runs the asyncio event loop. Handles trigger detection using `python-evdev`. Manages the lifecycle of the audio recording process. Receives audio chunks from the audio process via a `multiprocessing.Queue`. Sends audio chunks to the transcriber for streaming to the Wyoming server.
-   **Audio Recording Process:** A separate process spawned by the main process. Captures audio data using `python-sounddevice`. Buffers initial audio chunks. Performs manual trimming of a configurable duration from the beginning of the buffered audio. Sends the trimmed audio and subsequent chunks to the main process via a `multiprocessing.Queue`. Monitors a `multiprocessing.Event` to stop recording.
-   **Inter-Process Communication (IPC):** A `multiprocessing.Event` is used by the main process to signal the audio recording process to stop. A `multiprocessing.Queue` is used to stream audio data from the audio recording process to the main process. `None` is used as a sentinel value in the queue to signal the end of the audio stream.
-   **Transcription:** Handled by the transcriber, which receives audio chunks from the queue and streams them to the Wyoming server using the Wyoming protocol.
-   **Transcription Output:** Transcribed text is typed directly using `ydotool`.

## Identified Architectural Issue

The previously identified issue with trigger responsiveness due to single-process audio handling has been resolved by the implemented multiprocessing architecture and streaming pipeline.

## Architectural Changes and Evolution

To address the event processing delays and improve efficiency, the application was refactored to run audio recording and processing in a separate process using Python's `multiprocessing` module and implement a streaming audio pipeline. This involved moving away from file-based audio processing and implementing manual trimming of audio data chunks.

This multiprocessing and streaming approach successfully isolates potentially blocking audio operations from the main process's event loop, ensuring prompt trigger processing and enabling efficient, real-time-like transcription.
