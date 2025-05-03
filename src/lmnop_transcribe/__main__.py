import argparse
import asyncio
import logging
import multiprocessing
import os
import subprocess
import sys

import aiodebug.hang_inspection
import aiodebug.log_slow_callbacks
from loguru import logger

# Set the multiprocessing start method to 'spawn'
# This is necessary for compatibility when using multiprocessing with asyncio
# and libraries like aiomultiprocess, especially on systems where the default is 'fork'.
try:
  multiprocessing.set_start_method("spawn", force=True)
  logger.info("Multiprocessing start method set to 'spawn'.")
except ValueError as e:
  logger.warning(f"Could not set multiprocessing start method to 'spawn': {e}")


from .audio_processor import cleanup_audio
from .config import Config
from .input_handler import get_keyboard_device
from .recorder import record
from .transcriber import transcribe_audio_with_wyoming


def initialize_asyncio_debugging():
  logging.basicConfig(level=logging.DEBUG)

  # Enable aiodebug features
  aiodebug.log_slow_callbacks.enable(0.05)  # Log callbacks slower than 50ms
  # Enable aiodebug features
  aiodebug.log_slow_callbacks.enable(0.05)  # Log callbacks slower than 50ms

  # Create directory for hang inspection logs if it doesn't exist
  log_dir = "aiodebug_logs"
  os.makedirs(log_dir, exist_ok=True)
  # Dump stack traces if hangs for > 0.25s
  return aiodebug.hang_inspection.start(log_dir, interval=0.25)


async def main_async():
  parser = argparse.ArgumentParser(description="Record audio from keyboard input.")
  parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
  config_instance = Config(parser.parse_args().config)

  # Configure Loguru with the log level from the config
  logger.add(sys.stderr, format="{time} {level} {message}", level=config_instance.log_level)
  logger.info("Starting recorder.py")

  # Enable checks for bad asynchronous API usage
  dumper = initialize_asyncio_debugging()

  device_name = config_instance.audio_device_name
  sample_rate = config_instance.sample_rate
  keyboard_device = get_keyboard_device()
  if keyboard_device is None:
    return

  q = asyncio.Queue()  # Use asyncio.Queue

  try:
    # Need to make record async and await it
    await record(keyboard_device, config_instance)
    if config_instance.use_sox_silence:
      # cleanup_audio is likely blocking, run in executor if necessary
      cleanup_audio(config_instance.filename)

    # Run transcription in a thread pool executor
    loop = asyncio.get_event_loop()
    transcribed_text = await loop.run_in_executor(
      None, transcribe_audio_with_wyoming, config_instance.filename, config_instance.wyoming_server_address
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
  finally:
    # Stop hang inspection on exit
    if "dumper" in locals() and dumper:
      await aiodebug.hang_inspection.stop_wait(dumper)


if __name__ == "__main__":
  asyncio.run(main_async(), debug=True)  # Run the async main function
