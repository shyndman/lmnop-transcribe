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
    python3 -m venv venv
    ```
4.  Activate the virtual environment:

    ```bash
    source venv/bin/activate
    ```
5.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use lmnop:transcribe, run the following command:

```bash
python -m lmnop_transcribe --config config.toml
```

This command uses the configuration options specified in the `config.toml` file. You can modify the `config.toml` file to customize the project's behavior. The available configuration options are:

*   `xkeyboard_device_name`: The name of the keyboard device to use.
*   `channels`: The number of audio channels to record.
*   `block_size`: The audio block size.
*   `filename`: The name of the output audio file.
*   `audio_cleanup_command`: The command to use for audio cleanup.
*   `trim_ms`: The number of milliseconds to trim from the start and end of the audio.
*   `use_sox_silence`: Whether to use SoX silence detection for audio cleanup.
*   `use_desktop_notifications`: Whether to use desktop notifications.
*   `feedback_sound_start`: The path to the feedback sound file for start recording.
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
