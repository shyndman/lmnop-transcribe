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
from .transcriber import transcribe_audio_with_wyoming
from .trigger_handler import wait_for_start_trigger, wait_for_stop_trigger  # Import async trigger functions
from .user_feedback import play_sound, send_notification  # These are now async functions


async def record(keyboard_device, config: Config):
  """
  Monitors for start and stop triggers and manages audio recording process using aiomultiprocess.
  """
  logger.info("Ready to start recording. Awaiting trigger, pid={pid}", pid=os.getpid())

  audio_process = None  # Initialize audio process to None
  stop_event = None  # Initialize stop event to None

  while True:  # Main loop to wait for triggers
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

    # Wait for the stop trigger
    await wait_for_stop_trigger(keyboard_device, config)

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
    loop = asyncio.get_event_loop()

    if config.use_sox_silence:
      logger.info("Applying SoX silence removal to {filename}", filename=config.filename)
      start_time = time.time()
      try:
        # Run cleanup_audio in executor as it might be blocking
        await loop.run_in_executor(None, cleanup_audio, config.filename)
        end_time = time.time()
        logger.debug("SoX silence removal completed in %.2f seconds.", end_time - start_time)
      except Exception as e:
        logger.error(f"Error during audio cleanup: {e}")

    # Run transcription in a thread pool executor
    logger.debug(f"Starting transcription for {config.filename}")
    start_time = time.time()
    transcribed_text = await loop.run_in_executor(
      None, transcribe_audio_with_wyoming, config.filename, config.wyoming_server_address
    )
    end_time = time.time()
    logger.debug("Transcription completed in %.2f seconds.", end_time - start_time)

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
        logger.debug("Attempting to paste text using wl-copy...")
        start_time = time.time()
        await loop.run_in_executor(None, clipboard_paste_command)
        end_time = time.time()
        logger.info("Text inserted at cursor using wl-copy in %.2f seconds.", end_time - start_time)
      except FileNotFoundError:
        logger.error("Error: 'wl-copy' command not found. Please ensure it's installed and in your PATH.")
      except subprocess.CalledProcessError as e:
        logger.error(f"Error executing wl-copy: {e}")
    else:
      logger.warning("Transcription failed or produced no text.")
    # --- End of moved logic ---

    # Loop back to wait for the next start trigger
    logger.info("Ready to start recording. Awaiting trigger...")
