import multiprocessing
import os
import queue
import time

import sounddevice as sd
import soundfile as sf
from loguru import logger

from lmnop_transcribe.logger import initialize_logging

from .config import Config


async def audio_recording_process(
  device_name: str, rate: int, filename: str, channels: int, blocksize: int, stop_event
):
  """
  Function to run audio recording in a separate process.
  """
  config = Config()
  initialize_logging(config)

  logger.info("Audio recording process started, pid={pid}", pid=os.getpid())
  q_local = multiprocessing.Queue()  # Use multiprocessing.Queue for inter-process communication

  def callback_local(indata, frames, time, status):
    if status:
      logger.debug(f"Audio callback status: {status}")
    try:
      q_local.put_nowait(indata.copy())
    except queue.Full:
      logger.warning("Audio queue is fuAudio callback statusll, dropping data.")
      pass  # Drop data if queue is full

  stream = None
  file = None

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

    # Open the sound file for writing
    file = sf.SoundFile(filename, mode="w", samplerate=rate, channels=channels)
    logger.info(f"Audio file {filename} opened for writing in process.")

    # Start the sounddevice stream
    stream.start()
    logger.info("Audio stream started in process.")
    start_time = time.time()

    # Loop to get data from the local queue and write to file
    while not stop_event.is_set():
      try:
        # Use get with a small timeout to allow checking the stop_event
        data = q_local.get(timeout=0.1)
        file.write(data)

        elapsed = time.time() - start_time
        logger.debug(
          "Wrote {length} samples to file in process, {elapsed:1f}s", length=len(data), elapsed=elapsed
        )
      except queue.Empty:
        pass  # No data in queue, check event again
      except Exception as e:
        logger.error(f"Error in audio processing loop in process: {e}")
        break  # Exit loop on other errors

    logger.info("Finished record {elapsed:2f} seconds of audio", elapsed=(time.time() - start_time))
  except Exception as e:
    logger.exception(f"Error initializing audio stream or file in process: {e}")

  finally:
    # Ensure stream and file are closed properly in the process
    if stream is not None:
      if stream.active:
        stream.stop()
        logger.info("Audio stream stopped in process.")
      stream.close()
      logger.info("Audio stream closed in process.")
    if file is not None:
      file.close()
      logger.info("Audio file closed in process.")
    logger.info("Audio recording process finished.")
