import asyncio
import multiprocessing  # Import multiprocessing
import queue  # Import queue for Empty exception
from collections.abc import Callable

import sounddevice as sd
import soundfile as sf
from loguru import logger

from .config import Config


def create_audio_callback(q: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> Callable:
  def audio_callback(indata, frames, time, status):
    if status:
      logger.debug(f"Audio callback status: {status}")
    # Use call_soon_threadsafe to put data into the asyncio queue from the sounddevice thread
    loop.call_soon_threadsafe(q.put_nowait, indata.copy())

  return audio_callback


async def record_audio(
  q: asyncio.Queue, device_name: str, rate: int, recording_signal: asyncio.Event
):  # Accept recording_signal
  loop = asyncio.get_event_loop()
  stream = None  # Initialize stream to None
  file = None  # Initialize file to None

  try:
    # Initialize the sounddevice input stream
    stream = sd.InputStream(
      device=device_name,
      samplerate=rate,
      channels=Config().channels,
      blocksize=Config().block_size,
      callback=create_audio_callback(q, loop),
    )
    logger.info(
      f"Audio stream initialized with device={device_name}, "
      + f"samplerate={rate}, channels={Config().channels}, blocksize={Config().block_size}"
    )

    # Open the sound file for writing
    file = sf.SoundFile(Config().filename, mode="w", samplerate=rate, channels=Config().channels)

    # Start the sounddevice stream
    stream.start()
    logger.info("Audio stream started.")

    # This loop will now await data from the asyncio queue
    while True:
      try:
        data = await q.get()  # Await data from the queue
        # Perform file writing in a thread pool to avoid blocking the event loop
        await loop.run_in_executor(None, file.write, data)
        logger.debug(f"Wrote {len(data)} samples to file")
        q.task_done()  # Signal that the queue item is processed

        # Check if recording should stop
        if not recording_signal.is_set():
          logger.info("Recording signal cleared, stopping audio processing.")
          break  # Exit loop if recording_signal is cleared

      except asyncio.CancelledError:
        logger.info("Audio processing task cancelled.")
        break  # Exit loop if cancelled
      except Exception as e:
        logger.error(f"Error in audio processing loop: {e}")
        break  # Exit loop on other errors

  except Exception as e:
    logger.exception(f"Error initializing audio stream or file: {e}")

  finally:
    # Ensure stream and file are closed properly
    if stream is not None:  # Check if stream was successfully initialized
      if stream.active:  # Check if the stream is currently active
        stream.stop()
        logger.info("Audio stream stopped.")
      stream.close()  # Always close the stream if it was initialized
      logger.info("Audio stream closed.")
    if file is not None:
      file.close()
      logger.info("Audio file closed.")


# New function for multiprocessing
async def audio_recording_process(
  device_name: str, rate: int, filename: str, channels: int, blocksize: int, stop_event
):
  """
  Function to run audio recording in a separate process.
  """
  logger.info("Audio recording process started.")
  q_local = multiprocessing.Queue()  # Use multiprocessing.Queue for inter-process communication

  def callback_local(indata, frames, time, status):
    if status:
      logger.debug(f"Audio callback status: {status}")
    try:
      q_local.put_nowait(indata.copy())
    except queue.Full:
      logger.warning("Audio queue is full, dropping data.")
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

    # Loop to get data from the local queue and write to file
    while not stop_event.is_set():
      try:
        # Use get with a small timeout to allow checking the stop_event
        data = q_local.get(timeout=0.1)
        file.write(data)
        logger.debug(f"Wrote {len(data)} samples to file in process")
      except queue.Empty:
        pass  # No data in queue, check event again
      except Exception as e:
        logger.error(f"Error in audio processing loop in process: {e}")
        break  # Exit loop on other errors

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
