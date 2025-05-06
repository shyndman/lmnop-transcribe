import asyncio
import os
import queue
import shlex
import time
from multiprocessing.synchronize import Event
from typing import cast

import aiomultiprocess
from loguru import logger

from .audio_recorder import audio_recording_process
from .config import Config
from .dbus_service import DbusService
from .transcriber import transcribe_audio_with_wyoming
from .trigger_handler import (
  wait_for_start_trigger,
  wait_for_stop_or_cancel_trigger,
)
from .user_feedback import send_notification


async def record(keyboard_device, config: Config, dbus: DbusService):
  """
  Monitors for start and stop triggers and manages audio recording process using aiomultiprocess.
  """
  logger.info("Ready to start recording. Awaiting trigger, pid={pid}", pid=os.getpid())

  while True:
    await run_recording_cycle(keyboard_device, config, dbus)


async def run_recording_cycle(keyboard_device, config: Config, dbus: DbusService):
  """
  Runs a single audio recording and processing cycle.
  """
  await wait_for_start_trigger(keyboard_device, config)

  logger.info("Starting recording process using aiomultiprocess...")
  manager = aiomultiprocess.core.get_manager()
  stop_event = cast(Event, manager.Event())
  audio_queue: queue.Queue[bytes | None] = manager.Queue()

  audio_process = aiomultiprocess.Process(
    target=audio_recording_process,
    args=(
      config.audio_device_name,
      config.sample_rate,
      config.channels,
      config.block_size,
      stop_event,
      audio_queue,
    ),
  )
  audio_process.start()
  logger.info("Audio recording process started.")

  # Start the transcription task concurrently
  loop = asyncio.get_event_loop()
  # Assuming 16-bit audio, sample width is 2 bytes
  sample_width = 2
  transcription_task = loop.run_in_executor(
    None,
    transcribe_audio_with_wyoming,
    audio_queue,
    config.wyoming_server_address,
    config.sample_rate,
    sample_width,
    config.channels,
  )
  logger.info("Transcription task started.")

  if config.use_desktop_notifications:
    await send_notification("Recording started...")

  # Wait for either the stop or cancel trigger
  trigger_type = await wait_for_stop_or_cancel_trigger(keyboard_device, config)

  if trigger_type == "stop":
    # Pass audio_process and transcription_task to handle_stop
    await handle_stop(audio_process, stop_event, audio_queue, config)

    # Loop back to wait for the next start trigger
    logger.info("Ready to start recording. Awaiting trigger...")

  elif trigger_type == "cancel":
    # Pass audio_process and transcription_task to handle_cancel
    await handle_cancel(audio_process, stop_event, audio_queue, config)
    # Return from this function to go back to the main loop in record
    return

  # Wait for the transcription task to complete and get the result
  transcribed_text = None
  try:
    transcribed_text = await transcription_task
  except Exception as e:
    logger.error(f"Transcription task failed with exception: {e}")
    # Handle transcription task failure, maybe emit a DBus error
    transcribed_text = None  # Ensure transcribed_text is None if task failed

  # Now handle pasting if trigger was stop and transcription was successful
  if trigger_type == "stop" and isinstance(transcribed_text, str):
    await paste_transcribed_text(transcribed_text, dbus)


async def handle_stop(
  audio_process: aiomultiprocess.Process | None,
  stop_event: Event | None,
  audio_queue: queue.Queue[bytes | None],
  config: Config,
):
  """Handles the stop recording trigger."""
  logger.info("Stop trigger received.")

  await _stop_recording_process(audio_process, stop_event, audio_queue)

  if config.use_desktop_notifications:
    await send_notification("Recording stopped.")


async def handle_cancel(
  audio_process: aiomultiprocess.Process | None,
  stop_event: Event | None,
  audio_queue: queue.Queue[bytes | None],
  config: Config,
):
  """Handles the cancel recording trigger."""
  logger.info("Cancel trigger received. Stopping recording.")

  await _stop_recording_process(audio_process, stop_event, audio_queue)

  if config.use_desktop_notifications:
    await send_notification("Recording cancelled.")


async def _stop_recording_process(
  audio_process: aiomultiprocess.Process | None,
  stop_event: Event | None,
  audio_queue: queue.Queue[bytes | None],
):
  """Helper function to stop the audio recording process and signal the queue."""
  logger.info("Stopping recording process...")
  if stop_event:
    stop_event.set()
  if audio_process and audio_process.is_alive():
    await audio_process.join()
    logger.info("Audio recording process joined.")

  # Signal the end of the audio stream to the transcriber
  if audio_queue:
    audio_queue.put(None)
    logger.debug("Sent None signal to audio queue.")


async def paste_transcribed_text(transcribed_text: str | None, dbus: DbusService):
  """Types the transcribed text using ydotool."""
  if transcribed_text:
    logger.bind(transcribed_text=transcribed_text).info(
      'Transcribed text available, "{text}"', text=transcribed_text
    )

    escaped_text = shlex.quote(transcribed_text)

    try:
      logger.debug("Attempting to type text using ydotool asynchronously...")
      start_time = time.time()
      process = await asyncio.create_subprocess_exec(
        "ydotool",
        "type",
        "--key-delay",
        "3",
        "--key-hold",
        "3",
        escaped_text,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
      )
      stdout, stderr = await process.communicate()
      elapsed = time.time() - start_time

      if process.returncode != 0:
        error_message = f"Error executing ydotool: {stderr.decode().strip()}"
        logger.error(error_message)
        dbus.ErrorOccurred.emit(error_message)
      else:
        logger.info(
          "Text typed at cursor using ydotool asynchronously in {elapsed:2f} seconds.", elapsed=elapsed
        )

    except FileNotFoundError:
      error_message = "Error: 'ydotool' command not found. Please ensure it's installed and in your PATH."
      logger.exception(error_message)
      dbus.ErrorOccurred.emit(error_message)
    except Exception as e:  # Catch other potential exceptions during subprocess creation/communication
      error_message = f"An unexpected error occurred while running ydotool: {e}"
      logger.exception(error_message)
      dbus.ErrorOccurred.emit(error_message)
  else:
    logger.warning("Transcription failed or produced no text.")
