import multiprocessing
import os
import queue
import time

import numpy as np
import sounddevice as sd
from loguru import logger

from lmnop_transcribe.logger import initialize_logging

from .config import Config


def _process_incoming_audio(
  q_local: multiprocessing.Queue,
  q_main: multiprocessing.Queue,
  buffer: bytearray,
  trim_done: list,
  trim_duration_bytes: int,
  sample_width: int,
  channels: int,
  rate: int,
):
  """Gets data from the local queue, buffers, trims, and sends to the main queue."""
  try:
    data: np.ndarray = q_local.get(timeout=0.1)
    data_bytes = data.tobytes()

    if not trim_done[0]:
      buffer.extend(data_bytes)
      logger.debug(f"Buffered {len(data_bytes)} bytes, total buffer size: {len(buffer)}")

      if len(buffer) >= trim_duration_bytes:
        logger.info(
          f"Buffer size {len(buffer)} >= trim duration bytes {trim_duration_bytes}. Performing trim."
        )
        trimmed_audio = buffer[trim_duration_bytes:]
        q_main.put(bytes(trimmed_audio))
        logger.info(f"Sent {len(trimmed_audio)} bytes of trimmed audio to main queue.")
        buffer.clear()
        trim_done[0] = True
        logger.debug("Trim complete and flag set.")
      else:
        logger.debug("Buffering audio for trimming.")
    else:
      q_main.put(data_bytes)
      logger.debug(f"Sent {len(data_bytes)} bytes of subsequent audio to main queue.")

  except queue.Empty:
    pass
  except Exception as e:
    logger.error(f"Error in _process_incoming_audio: {e}")


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
    f"Calculated trim duration: {config.trim_duration_seconds:.2f} seconds = {trim_duration_bytes} bytes"
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
  start_time = None

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
      f"Audio stream initialized in process with device={device_name}, "
      + f"samplerate={rate}, channels={channels}, blocksize={blocksize}"
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
          sample_width,
          channels,
          rate,
        )
      except Exception as e:
        logger.error(f"Error in audio processing loop in process: {e}")
        break  # Exit loop on other errors

    if start_time is not None:
      elapsed = time.time() - start_time
      logger.info("Finished record {elapsed:2f} seconds of audio", elapsed=elapsed)

  except Exception as e:
    logger.exception(f"Error initializing audio stream in process: {e}")

  finally:
    if stream is not None:
      if stream.active:
        stream.stop()
        logger.info("Audio stream stopped in process.")
      stream.close()
      logger.info("Audio stream closed in process.")

    logger.info("Audio recording process finished.")
