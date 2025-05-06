import multiprocessing
import os
import queue
import time

import numpy as np
import sounddevice as sd
from loguru import logger

from .config import Config
from .logger import initialize_logging


async def audio_recording_process(
  device_name: str, rate: int, channels: int, blocksize: int, stop_event, q_main: multiprocessing.Queue
):
  """
  Function to run audio recording in a separate process.
  """
  config = Config()
  initialize_logging(config)

  logger.info("Audio recording process started, pid={pid}", pid=os.getpid())
  q_local = multiprocessing.Queue()

  # Buffer for initial audio data before trimming
  audio_buffer = bytearray()
  # Flag to indicate if trimming has been done
  trim_done = [False]

  # Calculate trim duration in bytes
  # Assuming 16-bit audio (2 bytes per sample)
  sample_width = 2
  trim_duration_bytes = int(config.trim_duration_seconds * rate * channels * sample_width)
  logger.info(
    "Calculated trim duration: {trim_seconds:.2f} seconds = {trim_bytes} bytes",
    trim_seconds=config.trim_duration_seconds,
    trim_bytes=trim_duration_bytes,
  )

  def callback_local(indata, frames, time, status):
    if status:
      logger.debug(f"Audio callback status: {status}")
    try:
      q_local.put_nowait(indata.copy())
    except queue.Full:
      logger.warning("Audio queue is fuAudio callback statusll, dropping data.")
      pass

  stream = None

  try:
    # Initialize the sounddevice input stream
    stream = sd.InputStream(
      device=device_name,
      samplerate=rate,
      channels=channels,
      blocksize=blocksize,
      callback=callback_local,
    )
    logger.info(
      (
        "Audio stream initialized in process with device={device_name}, "
        "samplerate={rate}, channels={channels}, blocksize={blocksize}"
      ),
      device_name=device_name,
      rate=rate,
      channels=channels,
      blocksize=blocksize,
    )

    # Start the sounddevice stream
    stream.start()
    logger.info("Audio stream started in process.")
    start_time = time.time()

    # Loop to get data from the local queue and process it
    while not stop_event.is_set():
      try:
        _process_incoming_audio(
          q_local,
          q_main,
          audio_buffer,
          trim_done,
          trim_duration_bytes,
        )
      except Exception:
        logger.exception("Error in audio processing loop in process")
        break  # Exit loop on other errors

    elapsed = time.time() - start_time
    logger.info("Finished record {elapsed:2f} seconds of audio", elapsed=elapsed)

  except Exception:
    logger.exception("Error initializing audio stream in process")

  finally:
    if stream is not None:
      if stream.active:
        stream.stop()
        logger.info("Audio stream stopped in process.")
      stream.close()
      logger.info("Audio stream closed in process.")

    logger.info("Audio recording process finished.")


def _process_incoming_audio(
  q_local: multiprocessing.Queue,
  q_main: multiprocessing.Queue,
  buffer: bytearray,
  trim_done: list,
  trim_duration_bytes: int,
):
  """Gets data from the local queue, buffers, trims, and sends to the main queue."""
  try:
    data: np.ndarray = q_local.get(timeout=0.1)
    data_bytes = data.tobytes()

    if trim_done[0]:
      q_main.put(data_bytes)
      logger.debug(f"Sent {len(data_bytes)} bytes of subsequent audio to main queue.")
      return

    buffer.extend(data_bytes)
    logger.debug(f"Buffered {len(data_bytes)} bytes, total buffer size: {len(buffer)}")

    if len(buffer) >= trim_duration_bytes:
      logger.info(f"Buffer size {len(buffer)} >= trim duration bytes {trim_duration_bytes}. Performing trim.")
      trimmed_audio = buffer[trim_duration_bytes:]
      buffer.clear()

      logger.info(
        "Sending {trim_byte_len} bytes of trimmed audio to main queue.", trim_byte_len=len(trimmed_audio)
      )
      q_main.put(bytes(trimmed_audio))
      trim_done[0] = True
      logger.debug("Trim complete and flag set.")
    else:
      logger.debug("Buffering audio for trimming.")

  except queue.Empty:
    pass
  except Exception as e:
    logger.error(f"Error in _process_incoming_audio: {e}")
