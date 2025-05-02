import argparse
import queue
import subprocess

from .audio_processor import cleanup_audio
from .config import Config
from .input_handler import get_keyboard_device
from .recorder import record
from .transcriber import transcribe_audio_with_wyoming


def main():
  parser = argparse.ArgumentParser(description="Record audio from keyboard input.")
  parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
  args = parser.parse_args()

  print("Starting recorder.py")

  config_instance = Config(args.config)
  device_name = config_instance.audio_device_name
  sample_rate = config_instance.sample_rate
  keyboard_device = get_keyboard_device()

  if keyboard_device is None:
    return

  q = queue.Queue()

  try:
    record(q, device_name, sample_rate, keyboard_device, config_instance)
    if config_instance.use_sox_silence:
      cleanup_audio(config_instance.filename)

    # Add Wyoming ASR transcription
    wyoming_server_address = config_instance.wyoming_server_address
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
