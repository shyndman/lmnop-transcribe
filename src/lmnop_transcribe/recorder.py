import asyncio
import os
import subprocess
import time
from typing import cast

import aiomultiprocess  # Import aiomultiprocess
from loguru import logger

from .audio_processor import cleanup_audio
from .audio_recorder import audio_recording_process  # Import the new multiprocessing function
from .config import Config  # Import Config to pass necessary values to the process
from .dbus_service import DbusService  # Import D-Bus interface class
from .transcriber import transcribe_audio_with_wyoming
from .trigger_handler import (  # Import async trigger functions
  wait_for_cancel_trigger,
  wait_for_start_trigger,
  wait_for_stop_trigger,
)
from .user_feedback import play_sound, send_notification  # These are now async functions


async def record(keyboard_device, config: Config, dbus: DbusService):
  """
  Monitors for start and stop triggers and manages audio recording process using aiomultiprocess.
  """
  logger.info("Ready to start recording. Awaiting trigger, pid={pid}", pid=os.getpid())

  while True:  # Main loop to wait for triggers
    await run_recording_cycle(keyboard_device, config, dbus)


async def run_recording_cycle(keyboard_device, config: Config, dbus: DbusService):
  """
  Runs a single audio recording and processing cycle.
  """
  audio_process = None  # Initialize audio process to None
  stop_event = None  # Initialize stop event to None

  # Wait for the start trigger
  await wait_for_start_trigger(keyboard_device, config)

  # Create a multiprocessing Event to signal the process to stop
  logger.info("Starting recording process using aiomultiprocess...")
  stop_event = aiomultiprocess.core.get_manager().Event()

  # Create an aiomultiprocess Process targeting the audio recording function
  # Pass necessary config values and the stop_event to the process
  audio_process = aiomultiprocess.Process(
    target=audio_recording_process,
    args=(
      config.audio_device_name,
      config.sample_rate,
      config.filename,
      config.channels,
      config.block_size,
      stop_event,
    ),
  )
  # Start the audio recording process asynchronously
  audio_process.start()
  logger.info("Audio recording process started.")

  if config.use_desktop_notifications:
    await send_notification("Recording started...")  # Await the async function
  _ignore = play_sound("start")  # Await the async function

  # Wait for either the stop or cancel trigger
  stop_task = asyncio.create_task(wait_for_stop_trigger(keyboard_device, config))
  cancel_task = asyncio.create_task(wait_for_cancel_trigger(keyboard_device, config))

  done, pending = await asyncio.wait([stop_task, cancel_task], return_when=asyncio.FIRST_COMPLETED)

  if stop_task in done:
    logger.info("Stop trigger received.")
    # Cancel the other task
    cancel_task.cancel()
    try:
      await cancel_task
    except asyncio.CancelledError:
      pass  # Expected cancellation

    logger.info("Stopping recording process...")
    # Set the stop event to signal the audio process to stop
    if stop_event:
      stop_event.set()
    # Wait for the audio process to finish asynchronously
    if audio_process and audio_process.is_alive():
      await audio_process.join()
      logger.info("Audio recording process joined.")
    audio_process = None  # Reset audio process
    stop_event = None  # Reset stop event

    if config.use_desktop_notifications:
      await send_notification("Recording stopped.")  # Await the async function
    _nowait = play_sound("stop")  # Await the async function

    # --- Start of moved logic ---
    logger.info("Processing recorded audio...")
    await process_audio_file(config, dbus)
    transcribed_text = await transcribe_recorded_audio(config, dbus)
    if transcribed_text is not None:
      await paste_transcribed_text(transcribed_text, dbus)
    # --- End of moved logic ---

    # Loop back to wait for the next start trigger
    logger.info("Ready to start recording. Awaiting trigger...")

  elif cancel_task in done:
    await handle_cancel(stop_task, audio_process, stop_event, config, dbus)
    # Return from this function to go back to the main loop in record
    return


async def handle_stop(stop_task, cancel_task, audio_process, stop_event, config, dbus):
  """Handles the stop recording trigger."""
  logger.info("Stop trigger received.")
  # Cancel the other task
  cancel_task.cancel()
  try:
    await cancel_task
  except asyncio.CancelledError:
    pass  # Expected cancellation

  logger.info("Stopping recording process...")
  # Set the stop event to signal the audio process to stop
  if stop_event:
    stop_event.set()
  # Wait for the audio process to finish asynchronously
  if audio_process and audio_process.is_alive():
    await audio_process.join()
    logger.info("Audio recording process joined.")
  audio_process = None  # Reset audio process
  stop_event = None  # Reset stop event

  if config.use_desktop_notifications:
    await send_notification("Recording stopped.")  # Await the async function
  _nowait = play_sound("stop")  # Await the async function

  # --- Start of moved logic ---
  logger.info("Processing recorded audio...")
  await process_audio_file(config, dbus)
  transcribed_text = await transcribe_recorded_audio(config, dbus)
  if transcribed_text is not None:
    await paste_transcribed_text(transcribed_text, dbus)
  # --- End of moved logic ---


async def handle_cancel(stop_task, audio_process, stop_event, config, dbus):
  """Handles the cancel recording trigger."""
  logger.info("Cancel trigger received. Stopping recording and removing file.")
  # Cancel the other task
  stop_task.cancel()
  try:
    await stop_task
  except asyncio.CancelledError:
    pass  # Expected cancellation

  # Set the stop event to signal the audio process to stop
  if stop_event:
    stop_event.set()
  # Wait for the audio process to finish asynchronously
  if audio_process and audio_process.is_alive():
    await audio_process.join()
    logger.info("Audio recording process joined.")
  audio_process = None  # Reset audio process
  stop_event = None  # Reset stop event

  # Remove the recorded file
  if os.path.exists(config.filename):
    os.remove(config.filename)
    logger.info(f"Removed cancelled recording file: {config.filename}")

  if config.use_desktop_notifications:
    await send_notification("Recording cancelled.")  # Await the async function
  _nowait = play_sound("stop")  # Await the async function


async def process_audio_file(config: Config, dbus: DbusService):
  """Applies SoX silence removal to the recorded audio file."""
  if config.use_sox_silence:
    logger.info("Applying SoX silence removal to {filename}", filename=config.filename)
    start_time = time.time()
    try:
      loop = asyncio.get_event_loop()
      await loop.run_in_executor(None, cleanup_audio, config.filename)
      end_time = time.time()
      logger.debug("SoX silence removal completed in {elapsed:2f} seconds.", elapsed=(end_time - start_time))
    except Exception as e:
      logger.error(f"Error during audio cleanup: {e}")
      # Emit ErrorOccurred signal
      error_message = f"Error during audio cleanup: {e}"
      dbus.ErrorOccurred.emit(error_message)
      logger.error(f"Emitted D-Bus signal: ErrorOccurred - {error_message}")


async def transcribe_recorded_audio(config: Config, dbus: DbusService) -> str | None:
  """Transcribes the recorded audio file using the Wyoming server."""
  logger.debug(f"Starting transcription for {config.filename}")
  start_time = time.time()
  loop = asyncio.get_event_loop()
  transcribed_text = await loop.run_in_executor(
    None, transcribe_audio_with_wyoming, config.filename, config.wyoming_server_address
  )
  end_time = time.time()
  logger.debug("Transcription completed in {elapsed:2f} seconds.", elapsed=(end_time - start_time))
  return transcribed_text


async def paste_transcribed_text(transcribed_text: str, dbus: DbusService):
  """Pastes the transcribed text to the clipboard."""
  if transcribed_text:
    logger.bind(transcribed_text=transcribed_text).info(
      'Transcribed text available, "{text}"', text=transcribed_text
    )

    # Ensure wl-copy is only called when transcribed_text is not None
    # Define the lambda inside the check to help type checker
    def clipboard_paste_command():
      text = cast(str, transcribed_text)
      subprocess.run(["wl-copy", text], check=True)
      subprocess.run(["wl-paste"], check=True)

    try:
      logger.debug("Attempting to paste text using wl-paste...")
      start_time = time.time()
      loop = asyncio.get_event_loop()
      await loop.run_in_executor(None, clipboard_paste_command)
      end_time = time.time()
      logger.info(
        "Text inserted at cursor using wl-paste in {elapsed:2f} seconds.", elapsed=(end_time - start_time)
      )
    except FileNotFoundError:
      logger.error("Error: 'wl-paste' command not found. Please ensure it's installed and in your PATH.")
      # Emit ErrorOccurred signal
      error_message = "Error: 'wl-paste' command not found. Please ensure it's installed and in your PATH."
      dbus.ErrorOccurred.emit(error_message)
      logger.error(f"Emitted D-Bus signal: ErrorOccurred - {error_message}")
    except subprocess.CalledProcessError as e:
      logger.error(f"Error executing wl-paste: {e}")
      # Emit ErrorOccurred signal
      error_message = f"Error executing wl-paste: {e}"
      dbus.ErrorOccurred.emit(error_message)
      logger.error(f"Emitted D-Bus signal: ErrorOccurred - {error_message}")
  else:
    logger.warning("Transcription failed or produced no text.")
