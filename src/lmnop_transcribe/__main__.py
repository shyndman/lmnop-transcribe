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
  except Exception as e:
    print(f"Error: {e}")
    return


if __name__ == "__main__":
  main()
