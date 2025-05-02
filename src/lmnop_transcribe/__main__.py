import argparse
import asyncio  # Import asyncio
import subprocess

from .audio_processor import cleanup_audio
from .config import Config
from .input_handler import get_keyboard_device
from .recorder import record
from .transcriber import transcribe_audio_with_wyoming


async def main_async():  # Define an async main function
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

  q = asyncio.Queue()  # Use asyncio.Queue

  try:
    # Need to make record async and await it
    await record(q, device_name, sample_rate, keyboard_device, config_instance)
    if config_instance.use_sox_silence:
      # cleanup_audio is likely blocking, run in executor if necessary
      cleanup_audio(config_instance.filename)

    # Add Wyoming ASR transcription
    wyoming_server_address = config_instance.wyoming_server_address
    # Run transcription in a thread pool executor
    loop = asyncio.get_event_loop()
    transcribed_text = await loop.run_in_executor(
      None, transcribe_audio_with_wyoming, config_instance.filename, wyoming_server_address
    )

    if transcribed_text:
      print(f"Transcribed text: {transcribed_text}")

      # Execute clippaste command in a thread pool executor using a lambda
      try:
        await loop.run_in_executor(None, lambda: subprocess.run(["clippaste", transcribed_text], check=True))
        print("Text inserted at cursor using clippaste.")
      except subprocess.CalledProcessError as e:
        print(f"Error executing clippaste: {e}")
    else:
      print("Transcription failed.")

  except Exception as e:
    print(f"Error: {e}")
    # The main async function should probably not return here,
    # but handle exceptions or signals to stop the main loop.
    # For now, we'll keep the return for basic structure.
    return


if __name__ == "__main__":
  asyncio.run(main_async())  # Run the async main function
