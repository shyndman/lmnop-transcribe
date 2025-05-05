# lmnop:transcribe

## Description

lmnop:transcribe is a tool that allows you to transcribe audio files. It supports various audio formats and provides accurate transcriptions using state-of-the-art speech recognition technology.

## Installation

To install lmnop:transcribe, follow these steps:

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/lmnop-transcribe.git
    ```
2.  Navigate to the project directory:

    ```bash
    cd lmnop-transcribe
    ```
3.  Create a virtual environment:

    ```bash
    uv venv
    ```
4.  Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```
5.  Install the dependencies:

    ```bash
    uv sync --all-extras --all-groups
    ```
6.  **Install ydotool and ydotoold:** LMNOP Transcribe uses `ydotool` to type the transcribed text. Ensure `ydotool` and its daemon `ydotoold` are installed and the daemon is running as a system service. Refer to the [ydotool GitHub repository](https://github.com/ReimuNotMoe/ydotool) for installation instructions.

## Usage

LMNOP Transcribe is primarily intended to be run as a background user systemd service.

## Deployment as a Systemd Service

To deploy LMNOP Transcribe as a user systemd service, follow these steps:

    **Run the installation script:**
    ```bash
    ./scripts/install-service.sh
    ```

This script will copy the `lmnop-transcribe.service` file to `~/.config/systemd/user/`, reload the systemd configuration, enable the service to start on login, and start the service immediately.

You can check the service status using:
```bash
systemctl --user status lmnop-transcribe.service
```

To stop the service:
```bash
systemctl --user stop lmnop-transcribe.service
```

To disable the service:
```bash
systemctl --user disable lmnop-transcribe.service
```

## Configuration

The project's behavior is configured via the `config.toml` file. You can modify this file to customize settings such as:

*   `keyboard_device_name`: The name of the keyboard device to use.
*   `channels`: The number of audio channels to record.
*   `block_size`: The audio block size.
*   `filename`: The naxkeyboard_device_nameme of the output audio file.
*   `audio_cleanup_command`: The command to use for audio cleanup.
*   `trim_ms`: The number of milliseconds to trim from the start and end of the audio.
*   `use_sox_silence`: Whether to use SoX silence detection for audio cleanup.
*   `use_desktop_notifications`: Whether to use desktop notifications.
*   `feedback_sound_stop`: The path to the feedback sound file for stop recording.
*   `audio_device_name`: The name of the audio device to use.
*   `sample_rate`: The audio sample rate.

## Contributing

We welcome contributions to lmnop:transcribe! To contribute, follow these steps:

1.  Fork the repository.
2.  Create a new branch.
3.  Make your changes.
4.  Submit a pull request.

## License

This project is licensed under the MIT License.
