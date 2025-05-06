# Active Context: LMNOP Transcribe

## Current Work Focus

Implementing the streaming audio pipeline with manual trimming.

## Recent Changes

-   **Removed SoX Dependencies:** Removed SoX-related configuration options from `config.toml` and `src/lmnop_transcribe/config.py`. Removed the `cleanup_audio` function from `src/lmnop_transcribe/audio_processor.py`.
-   **Refactored Audio Recorder:** Extracted the core processing logic into `_process_incoming_audio` in `src/lmnop_transcribe/audio_recorder.py` to improve readability and reduce indentation.
-   **Implemented Buffering and Manual Trimming:** Added logic in `src/lmnop_transcribe/audio_recorder.py` to buffer initial audio chunks, manually calculate and trim a configurable duration based on audio parameters, and send the trimmed audio and subsequent chunks via a `multiprocessing.Queue`. File writing has been removed from this process.
-   **Adapted Transcriber for Streaming:** Modified `src/lmnop_transcribe/transcriber.py` to receive audio chunks from a `multiprocessing.Queue` and stream them incrementally to the Wyoming server using the Wyoming protocol. Removed file-based audio reading.
-   **Updated Recorder for Pipeline:** Modified `src/lmnop_transcribe/recorder.py` to create and manage the `multiprocessing.Queue`, spawn the audio recording process with the queue, pass the queue to the adapted transcriber, and handle the process lifecycle and stream termination signal (`None` in the queue).
-   **Cleaned Up Comments:** Reviewed and removed "dumb comments" (obvious or redundant explanations) from `src/lmnop_transcribe/config.py`, `src/lmnop_transcribe/audio_processor.py`, `src/lmnop_transcribe/audio_recorder.py`, `src/lmnop_transcribe/transcriber.py`, and `src/lmnop_transcribe/recorder.py` according to code styling rules.
-   **Corrected Type Hinting:** Addressed Pylance errors related to type hints for `multiprocessing.Queue` in `src/lmnop_transcribe/recorder.py` and removed incorrect variable reassignments.

## Active Decisions and Considerations

-   **Streaming Pipeline:** Decided to move from a file-based audio processing approach to a streaming pipeline using `multiprocessing.Queue` for better efficiency and responsiveness.
-   **Manual Trimming:** Opted for manual trimming of initial audio bytes based on configuration and audio parameters instead of using external tools like SoX or libraries like pysox to reduce dependencies and simplify the process.
-   **Inter-Process Communication:** Confirmed `multiprocessing.Queue` as the mechanism for transferring audio data between the recording and main processes.
-   **End of Stream Signal:** Decided to use `None` as a sentinel value put onto the audio queue by the recording process to signal the end of the audio stream to the transcriber.
-   **Pylance Errors in Standard Library:** Acknowledged remaining Pylance errors in `multiprocessing/queues.py` as likely static analysis issues rather than bugs in the project code.

## Learnings and Project Insights

-   Implementing significant architectural changes (like moving to a streaming pipeline) requires careful planning and iterative development, often revealing unforeseen challenges (e.g., adapting existing code, handling inter-process communication nuances).
-   Debugging issues related to multiprocessing and asynchronous programming requires close attention to process lifecycles, shared resources, and signaling mechanisms.
-   The `replace_in_file` tool can be challenging for complex code modifications, sometimes requiring fallback to `write_to_file` for extensive changes.
-   Explicit and accurate type hinting, especially with libraries like `multiprocessing` and `aiomultiprocess`, is crucial for catching potential issues early and improving code clarity, although static analysis tools may sometimes struggle with complex interactions.
-   Adhering to code styling rules, such as avoiding "dumb comments" and initializing variables where used, contributes to a cleaner and more maintainable codebase.

## Pending Tasks and Next Steps

- Implement automatic recording cancellation based on duration threshold (re-evaluate how this fits with the streaming approach).
- Add user feedback for cancelled recordings.
- Refine error handling and edge case management in the streaming pipeline (e.g., what happens if the Wyoming server disconnects mid-stream).
- Re-evaluate the minimum recording duration check and decide where it should be implemented in the new pipeline.
