import argparse
import asyncio  # Added asyncio import here as it was removed in the previous diff
import multiprocessing
import os

import aiodebug.hang_inspection
import aiodebug.log_slow_callbacks
from loguru import logger
from sdbus import request_default_bus_name_async

from lmnop_transcribe.logger import initialize_logging

from .dbus_service import BUS_NAME, OBJECT_PATH, DbusService

# Set the multiprocessing start method to 'spawn'
# This is necessary for compatibility when using multiprocessing with asyncio
# and libraries like aiomultiprocess, especially on systems where the default is 'fork'.
try:
  multiprocessing.set_start_method("spawn", force=True)
except ValueError as e:
  logger.warning(f"Could not set multiprocessing start method to 'spawn': {e}")


# Removed unused imports: cleanup_audio, transcribe_audio_with_wyoming, subprocess
from .config import Config
from .input_handler import get_keyboard_device
from .recorder import record


def initialize_asyncio_debugging():
  # Create directory for hang inspection logs if it doesn't exist
  log_dir = "aiodebug_logs"
  os.makedirs(log_dir, exist_ok=True)
  # Enable aiodebug features
  aiodebug.log_slow_callbacks.enable(0.05)  # Log callbacks slower than 50ms
  # Enable aiodebug features
  aiodebug.log_slow_callbacks.enable(0.05)  # Log callbacks slower than 50ms
  # Dump stack traces if hangs for > 0.25s
  return aiodebug.hang_inspection.start(log_dir, interval=0.25)


async def main_async():
  parser = argparse.ArgumentParser(description="Record audio from keyboard input.")
  parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
  config = Config(parser.parse_args().config)

  # Configure Loguru with the log level from the config
  initialize_logging(config)
  logger.info("Starting recorder.py")

  # Enable checks for bad asynchronous API usage
  dumper = initialize_asyncio_debugging()

  keyboard_device = get_keyboard_device()
  if keyboard_device is None:
    return

  # Removed unused queue: q = asyncio.Queue()

  # Create D-Bus interface instance
  dbus = DbusService()

  try:
    # Request bus name and export the D-Bus object
    await request_default_bus_name_async(BUS_NAME)
    dbus.export_to_dbus(OBJECT_PATH)
    logger.info(f"D-Bus service '{BUS_NAME}' exported at '{OBJECT_PATH}'")

    # The record function now contains the main loop and handles post-recording steps.
    # We just need to await it. It will run indefinitely until interrupted.
    await record(keyboard_device, config, dbus)

  except asyncio.CancelledError:
    logger.info("Main task cancelled, shutting down.")
  except Exception as e:
    logger.exception(f"An unexpected error occurred in main_async: {e}")
  finally:
    logger.info("Cleaning up asyncio debugging...")
    # Stop hang inspection on exit
    if "dumper" in locals() and dumper:
      await aiodebug.hang_inspection.stop_wait(dumper)


def main():
  asyncio.run(main_async())  # Run the async main function
