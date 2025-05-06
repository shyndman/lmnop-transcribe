from __future__ import annotations

import asyncio
import multiprocessing
import os
import queue
import shlex
import subprocess
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
from .user_feedback import play_sound, send_notification


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
  # Wait for the start trigger
  await wait_for_start_trigger(keyboard_device, config)

  logger.info("Starting recording process using aiomultiprocess...")
  manager = aiomultiprocess.core.get_manager()
  stop_event = cast(Event, manager.Event())
  audio_queue: queue.Queue[bytes] = manager.Queue()

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

  if config.use_desktop_notifications:
    await send_notification("Recording started...")
  _ignore = play_sound("start")

  # Wait for either the stop or cancel trigger
  trigger_type = await wait_for_stop_or_cancel_trigger(keyboard_device, config)

  if trigger_type == "stop":
    await handle_stop(audio_process, stop_event, audio_queue, config, dbus)  # Pass audio_queue

    # Loop back to wait for the next start trigger
    logger.info("Ready to start recording. Awaiting trigger...")

  elif trigger_type == "cancel":
    await handle_cancel(audio_process, stop_event, audio_queue, config, dbus)  # Pass audio_queue
    # Return from this function to go back to the main loop in record
    return


async def handle_stop(
  audio_process: aiomultiprocess.Process | None,
  stop_event: Event | None,
  audio_queue: queue.Queue[bytes],
  config: Config,
  dbus: DbusService,
):
  """Handles the stop recording trigger."""
  logger.info("Stop trigger received.")

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

  audio_process = None
  stop_event = None

  if config.use_desktop_notifications:
    await send_notification("Recording stopped.")
  _nowait = play_sound("stop")

  # The minimum duration check is now handled by the audio recording process
  # or can be implemented based on the amount of data received from the queue
  # For now, we proceed directly to transcription.

  logger.info("Processing recorded audio...")
  # Assuming 16-bit audio, sample width is 2 bytes
  sample_width = 2
  transcribed_text = await transcribe_recorded_audio(
    audio_queue,
    config.wyoming_server_address,
    config.sample_rate,
    sample_width,
    config.channels,
    dbus,
  )
  if transcribed_text is not None:
    await paste_transcribed_text(transcribed_text, dbus)


async def handle_cancel(
  audio_process: aiomultiprocess.Process | None,
  stop_event: Event | None,
  audio_queue: queue.Queue[bytes],
  config: Config,
  dbus: DbusService,
):
  """Handles the cancel recording trigger."""
  logger.info("Cancel trigger received. Stopping recording.")

  if stop_event:
    stop_event.set()
  if audio_process and audio_process.is_alive():
    await audio_process.join()
    logger.info("Audio recording process joined.")

  # Signal the end of the audio stream to the transcriber
  if audio_queue:
    audio_queue.put(None)
    logger.debug("Sent None signal to audio queue.")

  audio_process = None
  stop_event = None

  if config.use_desktop_notifications:
    await send_notification("Recording cancelled.")
  _nowait = play_sound("stop")


async def transcribe_recorded_audio(
  audio_queue: multiprocessing.Queue,
  wyoming_server_address: str,
  rate: int,
  sample_width: int,
  channels: int,
  dbus: DbusService,
) -> str | None:
  """Transcribes audio chunks from a queue using the Wyoming server."""
  logger.debug("Starting transcription from audio queue.")
  start_time = time.time()
  loop = asyncio.get_event_loop()
  transcribed_text = await loop.run_in_executor(
    None,
    transcribe_audio_with_wyoming,
    audio_queue,
    wyoming_server_address,
    rate,
    sample_width,
    channels,
  )
  end_time = time.time()
  logger.debug("Transcription completed in {elapsed:2f} seconds.", elapsed=(end_time - start_time))
  return transcribed_text


async def paste_transcribed_text(transcribed_text: str, dbus: DbusService):
  """Types the transcribed text using ydotool."""
  if transcribed_text:
    logger.bind(transcribed_text=transcribed_text).info(
      'Transcribed text available, "{text}"', text=transcribed_text
    )

    escaped_text = shlex.quote(transcribed_text)

    try:
      logger.debug("Attempting to type text using ydotool...")
      start_time = time.time()
      subprocess.run(["ydotool", "type", "--key-delay", "3", "--key-hold", "3", escaped_text], check=True)
      elapsed = time.time() - start_time

      logger.info("Text typed at cursor using ydotool in {elapsed:2f} seconds.", elapsed=elapsed)
    except FileNotFoundError:
      error_message = "Error: 'ydotool' command not found. Please ensure it's installed and in your PATH."
      logger.exception(error_message)
      dbus.ErrorOccurred.emit(error_message)
    except subprocess.CalledProcessError:
      error_message = "Error executing ydotool"
      logger.exception(error_message)
      dbus.ErrorOccurred.emit(error_message)
  else:
    logger.warning("Transcription failed or produced no text.")
