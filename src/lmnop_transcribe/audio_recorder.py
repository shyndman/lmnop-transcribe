import queue
from collections.abc import Callable

import sounddevice as sd
import soundfile as sf

from .config import Config


def create_audio_callback(q: queue.Queue) -> Callable:
  def audio_callback(indata, frames, time, status):
    if status:
      print(status)
    q.put(indata.copy())

  return audio_callback


def record_audio(q: queue.Queue, device_name: str, rate: int):
  try:
    stream = sd.InputStream(
      device=device_name,
      samplerate=rate,
      channels=Config().channels,
      blocksize=Config().block_size,
      callback=create_audio_callback(q),
    )
    print(
      f"Audio stream initialized with device={device_name}, "
      + f"samplerate={rate}, channels={Config().channels}, blocksize={Config().block_size}"
    )

    with stream:
      with sf.SoundFile(Config().filename, mode="w", samplerate=rate, channels=Config().channels) as file:
        while True:
          try:
            data = q.get(timeout=0.1)
            file.write(data)
            print(f"Wrote {len(data)} samples to file")
            yield True
          except queue.Empty:
            yield False
  except Exception as e:
    print(f"Error: {e}")
    yield False
