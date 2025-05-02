# Integrate Wyoming ASR

**Task:** Integrate Wyoming ASR into the `lmnop-transcribe` project to enable speech-to-text functionality and insert the transcribed text at the cursor using the `clipaste` command.

**Plan:**

1.  **Orchestrator:** The Orchestrator will create a detailed plan for integrating Wyoming ASR into the `lmnop-transcribe` project. This plan will include:
    *   Modifying the `__main__.py` file to call the `transcribe_audio_with_wyoming` function from `src/lmnop_transcribe/transcriber.py`.
    *   Adding configuration options to the `config.py` file for the Wyoming ASR server address.
    *   Ensuring that the necessary dependencies (e.g., `wyoming`) are installed.
2.  **Architect (You):** The Architect (you) will review the plan created by the Orchestrator. You will ensure that the plan is technically sound, aligns with the project's goals, and incorporates best practices. You will also verify that the plan includes the correct code snippets and instructions for the Coder.
3.  **Coder:** The Coder will implement the plan approved by the Architect. The Coder will modify the `__main__.py` and `config.py` files, install the necessary dependencies, and test the integration to ensure that it functions correctly.

**Instructions:**

1.  The Orchestrator should create a new task in Code mode with the detailed plan.
2.  Before the Coder begins implementation, switch to Architect mode and review the plan.
3.  Provide feedback to the Orchestrator if any changes are needed.
4.  Once the plan is approved, switch to Code mode and instruct the Coder to implement the plan.

**Code Snippet:**

```python
import subprocess
import socket
import wave
from wyoming.audio import AudioChunk, AudioStop, AudioStart
from wyoming.asr import Transcript, Transcribe
from wyoming.event import Event, write_event, read_event
import argparse
import queue
import select
from typing import cast

import evdev
import sounddevice as sd

from .audio_processor import cleanup_audio
from .audio_recorder import record_audio
from .config import Config
from .input_handler import get_keyboard_device
from .user_feedback import play_sound, send_notification

```python
import subprocess
import queue
import select
import argparse
from typing import cast

import evdev
import sounddevice as sd

from .audio_processor import cleanup_audio
from .audio_recorder import record_audio
from .config import Config
from .input_handler import get_keyboard_device
from .user_feedback import play_sound, send_notification
from .transcriber import transcribe_audio_with_wyoming


def main():
    parser = argparse.ArgumentParser(description="Record audio from keyboard input.")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
    args = parser.parse_args()

    print("Starting recorder.py")

    config_instance = Config(args.config)
    device_name = config_instance.audio_device_name
    sample_rate = config_instance.sample_rate

    if device_name == "list":
        print("Available audio devices:")
        devices = cast(tuple[dict[str, str | int], ...], sd.query_devices())
        for i, device in enumerate(devices):
            is_input = cast(int, device["max_input_channels"]) > 0
            print(f"  - {i}: {device['name']} (input={is_input})")
        return

    keyboard_device = get_keyboard_device()

    if keyboard_device is None:
        return

    q = queue.Queue()

    try:
        print("Starting audio stream...")
        if config_instance.use_desktop_notifications:
            send_notification("Recording started...")
        play_sound("start")

        recording = True
        for audio_written in record_audio(q, device_name, int(sample_rate)):
            if not audio_written:
                continue

            r, _, _ = select.select([keyboard_device], [], [], 0)
            if r:
                for event in keyboard_device.read():
                    if event.type == evdev.ecodes.EV_KEY:
                        print("Stopping recording...")
                        recording = False
                        break
            if not recording:
                break

        print("Audio stream stopped.")
        if config_instance.use_desktop_notifications:
            send_notification("Recording stopped.")
        play_sound("stop")
        if config_instance.use_sox_silence:
            cleanup_audio(config_instance.filename)

        # Add Wyoming ASR transcription
        wyoming_server_address = "localhost:8080"  # Replace with your server address
        transcribed_text = transcribe_audio_with_wyoming(config_instance.filename, wyoming_server_address)

        if transcribed_text:
            print(f"Transcribed text: {transcribed_text}")

            # Execute clipaste command
            try:
                subprocess.run(["clipaste", transcribed_text], check=True)
                print("Text inserted at cursor using clipaste.")
            except subprocess.CalledProcessError as e:
                print(f"Error executing clipaste: {e}")
        else:
            print("Transcription failed.")

    except Exception as e:
        print(f"Error: {e}")
        return


if __name__ == "__main__":
    main()
