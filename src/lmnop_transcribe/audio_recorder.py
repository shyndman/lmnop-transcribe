import asyncio
from collections.abc import Callable

import sounddevice as sd
import soundfile as sf

from .config import Config


def create_audio_callback(q: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> Callable:
  def audio_callback(indata, frames, time, status):
    if status:
      print(status)
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
    print(
      f"Audio stream initialized with device={device_name}, "
      + f"samplerate={rate}, channels={Config().channels}, blocksize={Config().block_size}"
    )

    # Open the sound file for writing
    file = sf.SoundFile(Config().filename, mode="w", samplerate=rate, channels=Config().channels)

    # Start the sounddevice stream
    stream.start()
    print("Audio stream started.")

    # This loop will now await data from the asyncio queue
    while True:
      try:
        data = await q.get()  # Await data from the queue
        file.write(data)
        print(f"Wrote {len(data)} samples to file")
        q.task_done()  # Signal that the queue item is processed
      except asyncio.CancelledError:
        print("Audio processing task cancelled.")
        break  # Exit loop if cancelled
      except Exception as e:
        print(f"Error in audio processing loop: {e}")
        break  # Exit loop on other errors

  except Exception as e:
    print(f"Error initializing audio stream or file: {e}")

  finally:
    # Ensure stream and file are closed properly
    if stream is not None:  # Check if stream was successfully initialized
      if stream.active:  # Check if the stream is currently active
        stream.stop()
        print("Audio stream stopped.")
      stream.close()  # Always close the stream if it was initialized
      print("Audio stream closed.")
    if file is not None:
      file.close()
      print("Audio file closed.")
