# System Patterns: LMNOP Transcribe

## Current Architecture

The application currently follows a single-process, asyncio-based architecture.

-   **Main Process:** Runs the asyncio event loop.
-   **Trigger Handling:** Uses `python-evdev` with `async_read_loop` in the main event loop to monitor keyboard events for start and stop triggers.
-   **Audio Recording:** Uses `python-sounddevice` with a callback to capture audio data. The callback puts data into an `asyncio.Queue`.
-   **Audio Processing/Writing:** An asyncio task (`record_audio`) in the main event loop reads data from the queue and writes it to a file using `soundfile`. (Initially blocking file write, modified to use `loop.run_in_executor` for non-blocking I/O).
-   **Inter-Task Communication:** An `asyncio.Event` (`recording_signal`) is used to signal the audio task to stop, and task cancellation is also used.

## Identified Architectural Issue

The current single-process architecture, particularly the interaction between the `sounddevice` audio callback, the audio processing task, and the `evdev` event loop within the same asyncio event loop, appears to be causing delays in processing `evdev` events when audio recording is active. This leads to unresponsiveness in the stop trigger.

## Planned Architectural Change: Multiprocessing for Audio

To address the event processing delays, the plan is to refactor the application to run the audio recording and processing in a separate process using Python's `multiprocessing` module.

-   **Main Process:** Will continue to handle trigger detection using `evdev` in its asyncio event loop. It will manage the lifecycle of the audio recording process.
-   **Audio Recording Process:** A separate process will be spawned to handle all audio capture, processing, and file writing using `sounddevice` and `soundfile`.
-   **Inter-Process Communication (IPC):** A `multiprocessing.Event` will be used by the main process to signal the audio recording process to start and stop. The audio process will monitor this event.

This multiprocessing approach aims to isolate the potentially blocking or resource-intensive audio operations from the main process's event loop, ensuring that trigger events are processed promptly.
