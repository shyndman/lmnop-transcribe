# Technical Context: LMNOP Transcribe

## Technologies Used

-   **Python:** The primary programming language.
-   **asyncio:** Used for asynchronous programming and managing the event loop in the main process.
-   **python-evdev:** Used for reading input events from devices like the keyboard.
-   **python-sounddevice:** Used for capturing audio input.
-   **soundfile:** Used for reading and writing audio files (e.g., WAV).
-   **loguru:** Used for logging.
-   **toml:** Used for reading the configuration file (`config.toml`).
-   **multiprocessing:** (Planned) Will be used to run audio recording in a separate process.
-   **ydotool:** Used for typing the transcribed text.
-   **Wyoming Protocol:** Used for communication with the Speech-to-Text server.
-   **uv:** Used for dependency management and packaging.

## Development Setup

-   **Operating System:** Linux (specifically tested on Ubuntu 24.10).
-   **Input Devices:** Relies on standard keyboard input devices accessible via `/dev/input/`.
-   **Audio Devices:** Relies on standard audio input devices accessible via PortAudio (used by `sounddevice`).
-   **Configuration:** Project settings are managed via a `config.toml` file.
-   **Deployment:** Intended to be deployed as a user systemd service.
-   **Dependencies:** Managed using `uv` and defined in `pyproject.toml`. Dependencies can be added using `uv add <package-name>`. For example, to add the `numpy` package, you would run `uv add numpy`.

## Technical Constraints

-   **Real-time Input:** Requires low-latency processing of keyboard events for responsive triggers.
-   **Asynchronous I/O:** Audio recording and file writing must be handled asynchronously to avoid blocking the main event loop.
-   **Environment Compatibility:** Needs to function correctly across different Linux distributions and hardware configurations for input and audio devices.
