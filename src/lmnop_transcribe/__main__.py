import argparse
import asyncio  # Import asyncio
import subprocess
import sys

from loguru import logger

from .audio_processor import cleanup_audio
from .config import Config
from .input_handler import get_keyboard_device
from .recorder import record
from .transcriber import transcribe_audio_with_wyoming


async def main_async():  # Define an async main function
  parser = argparse.ArgumentParser(description="Record audio from keyboard input.")
  parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
  args = parser.parse_args()

  config_instance = Config(args.config)

  # Configure Loguru with the log level from the config
  logger.add(sys.stderr, format="{time} {level} {message}", level=config_instance.log_level)

  logger.info("Starting recorder.py")

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
      logger.bind(transcribed_text=transcribed_text).info("Transcribed text available.")

      # Execute clippaste command in a thread pool executor using a lambda
      try:
        await loop.run_in_executor(None, lambda: subprocess.run(["clippaste", transcribed_text], check=True))
        logger.info("Text inserted at cursor using clippaste.")
      except subprocess.CalledProcessError as e:
        logger.error(f"Error executing clippaste: {e}")
    else:
      logger.warning("Transcription failed.")

  except Exception as e:
    logger.exception(f"Error: {e}")
    # The main async function should probably not return here,
    # but handle exceptions or signals to stop the main loop.
    # For now, we'll keep the return for basic structure.
    return


if __name__ == "__main__":
  asyncio.run(main_async())  # Run the async main function
