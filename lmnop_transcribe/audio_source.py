#!/usr/bin/env python3
"""
Audio source module using sounddevice for reactive audio streaming.
Provides observables for audio chunks that integrate with the RxPY pipeline.
"""

import asyncio
import logging
import queue
import time
from typing import cast

import numpy as np
import reactivex as rx
import sounddevice as sd

# Set up logging
from loguru import logger
from reactivex.scheduler.eventloop import AsyncIOScheduler

from .common import AudioChunk, AudioConfig


def find_default_audio_device() -> int:
  """
  Find the default audio input device.
  Returns the device index or None if no default device is found.
  """
  devices = sd.query_devices()
  for i, d in enumerate(devices):
    device = cast(dict, d)
    if "ALC295" in device["name"]:
      return i

  raise EnvironmentError("No default audio input device found")


class AudioSource:
  """
  Reactive audio source using sounddevice.

  Provides observables for audio chunks with proper lifecycle management.
  Uses callback-based approach for better control over recording sessions.
  """

  def __init__(self, config: AudioConfig | None = None, scheduler: AsyncIOScheduler | None = None):
    self.config = config or AudioConfig()
    self.scheduler = scheduler
    self._audio_queue = queue.Queue()
    self._stream: sd.InputStream | None = None
    self._recording_start_time: float | None = None
    self._is_recording = False

    logger.info(f"AudioSource initialized with config: {self.config}")

  def _audio_callback(self, indata: np.ndarray, _frames: int, _time_info, status):
    """
    Audio callback called from separate thread by sounddevice.
    Puts audio data into queue with timestamp information.
    """
    if status:
      logger.warning(f"Audio callback status: {status}")

    logger.trace("audio packet received, {frames}", frames=_frames)

    if self._is_recording and self._recording_start_time is not None:
      # Calculate delta time from recording start
      current_time = time.time() * 1000  # Convert to milliseconds
      timestamp_delta = current_time - self._recording_start_time

      # Convert numpy array to bytes
      audio_bytes = indata.copy()

      chunk = AudioChunk(data=audio_bytes.tobytes(), timestamp_delta=timestamp_delta)

      try:
        self._audio_queue.put_nowait(chunk)
        logger.debug(f"Audio chunk queued: {len(audio_bytes)} bytes at {timestamp_delta:.1f}ms")
      except queue.Full:
        logger.warning("Audio queue full, dropping chunk")

  def _get_device_info(self) -> dict:
    """Get information about the audio device"""
    try:
      device_info = cast(dict, sd.query_devices(self.config.device, "input"))
      logger.info(f"Using audio device: {device_info['name']}")
      return device_info
    except Exception:
      logger.exception("Error querying audio device")
      raise

  def _create_stream(self) -> sd.InputStream:
    """Create and configure the audio input stream"""
    device_info = self._get_device_info()

    # Use device default samplerate if not specified
    samplerate = self.config.samplerate or device_info["default_samplerate"]

    logger.info(
      f"Creating audio stream: {self.config.channels} channels, "
      f"{samplerate}Hz, blocksize={self.config.blocksize}"
    )

    stream = sd.InputStream(
      device=self.config.device,
      channels=self.config.channels,
      samplerate=samplerate,
      blocksize=self.config.blocksize,
      dtype=self.config.dtype,
      callback=self._audio_callback,
    )

    return stream

  def start_recording(self):
    """Start audio recording session"""
    if self._is_recording:
      logger.warning("Recording already in progress")
      return

    logger.info("Starting audio recording session")

    try:
      # Create new stream if needed
      if self._stream is None:
        self._stream = self._create_stream()

      # Clear any leftover audio chunks from queue
      while not self._audio_queue.empty():
        try:
          self._audio_queue.get_nowait()
        except queue.Empty:
          break

      # Mark recording start time
      self._recording_start_time = time.time() * 1000  # milliseconds
      self._is_recording = True

      # Start the audio stream
      assert self._stream is not None, "Audio stream should be initialized"
      self._stream.start()
      logger.info(f"Audio recording started at {self._recording_start_time:.0f}ms")

    except Exception:
      logger.exception("Failed to start recording")
      self._is_recording = False
      self._recording_start_time = None
      raise

  def stop_recording(self):
    """Stop audio recording session and close the stream to release microphone access"""
    if not self._is_recording:
      logger.warning("No recording in progress")
      return

    logger.info("Stopping audio recording session")

    try:
      self._is_recording = False

      # Close the stream completely to release microphone access
      if self._stream:
        if self._stream.active:
          self._stream.stop()
          logger.info("Audio stream stopped")
        self._stream.close()
        logger.info("Audio stream closed and microphone released")
        self._stream = None

      # Log final statistics
      if self._recording_start_time:
        duration = (time.time() * 1000) - self._recording_start_time
        logger.info(
          f"Recording session ended. Duration: {duration:.0f}ms, Queue size: {self._audio_queue.qsize()}"
        )

    except Exception:
      logger.exception("Error stopping recording")

  def cleanup(self):
    """Clean up audio resources"""
    logger.info("Cleaning up audio source")

    self.stop_recording()

    if self._stream:
      try:
        self._stream.close()
        logger.info("Audio stream closed")
      except Exception:
        logger.exception("Error closing stream")
      finally:
        self._stream = None

    # Clear remaining queue items
    queue_size = self._audio_queue.qsize()
    if queue_size > 0:
      logger.info(f"Clearing {queue_size} remaining audio chunks from queue")
      while not self._audio_queue.empty():
        try:
          self._audio_queue.get_nowait()
        except queue.Empty:
          break

  def create_audio_observable(self) -> rx.Observable:
    """
    Create an observable that emits audio chunks from the queue.

    This observable polls the audio queue at regular intervals and emits
    AudioChunk objects when they're available.
    """

    def audio_generator(observer, scheduler):
      logger.info("Audio observable started")

      def poll_audio(*args):
        try:
          # Get all available chunks from queue
          chunks_emitted = 0
          while not self._audio_queue.empty():
            try:
              chunk = self._audio_queue.get_nowait()
              observer.on_next(chunk)
              chunks_emitted += 1
            except queue.Empty:
              break

          if chunks_emitted > 0:
            logger.debug(f"Emitted {chunks_emitted} audio chunks")

        except Exception as e:
          logger.exception("Error in audio polling")
          observer.on_error(e)
          return

        # Schedule next poll
        if scheduler:
          scheduler.schedule_relative(self.config.chunk_poll_interval_ms / 1000.0, poll_audio)

      # Start polling
      poll_audio()

      # Return cleanup function
      def cleanup():
        logger.info("Audio observable cleanup called")

      from reactivex.disposable import Disposable

      return Disposable(cleanup)

    return rx.create(audio_generator)


def list_audio_devices():
  """Utility function to list available audio devices"""
  print("Available audio devices:")
  devices = sd.query_devices()
  for i, d in enumerate(devices):
    device = cast(dict, d)
    if device["max_input_channels"] > 0:
      print(f"  {i}: {device['name']} (max {device['max_input_channels']} input channels)")


# Example usage and testing
async def test_audio_source():
  """Test function to verify audio source functionality"""
  import os

  import soundfile as sf

  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

  print("🔊 Testing audio source...")

  # List available devices
  list_audio_devices()

  # Create audio source
  config = AudioConfig(
    device="default",
    channels=1,
    samplerate=44100,
    chunk_poll_interval_ms=50,  # Poll every 50ms
  )

  loop = asyncio.get_event_loop()
  scheduler = AsyncIOScheduler(loop)

  audio_source = AudioSource(config, scheduler)

  # Prepare WAV file output
  wav_output_path = os.path.expanduser("~/tmp/test.wav")
  os.makedirs(os.path.dirname(wav_output_path), exist_ok=True)

  # Buffer to collect audio chunks for WAV file
  audio_chunks_buffer = []

  try:
    # Create observable
    audio_obs = audio_source.create_audio_observable()

    # Subscribe to audio chunks
    chunk_count = 0

    def on_chunk(chunk: AudioChunk):
      nonlocal chunk_count
      chunk_count += 1
      audio_chunks_buffer.append(chunk.data)
      print(f"📡 Received chunk {chunk_count}: {len(chunk.data)} bytes at {chunk.timestamp_delta:.1f}ms")

    audio_obs.subscribe(on_next=on_chunk, on_error=lambda e: print(f"❌ Error: {e}"), scheduler=scheduler)

    # Test recording session
    print("🎙️ Starting 3-second recording test...")
    audio_source.start_recording()

    await asyncio.sleep(3.0)

    audio_source.stop_recording()
    print(f"🏁 Recording test completed. Total chunks received: {chunk_count}")

    # Wait a bit to process remaining chunks
    await asyncio.sleep(0.5)

    # Write collected audio to WAV file
    if audio_chunks_buffer:
      print(f"💾 Writing {len(audio_chunks_buffer)} chunks to {wav_output_path}")

      total_bytes = 0
      with sf.SoundFile(
        wav_output_path,
        mode="w",
        samplerate=config.samplerate,
        channels=config.channels,
        format="WAV",
        subtype="PCM_16",
      ) as wav_file:
        for chunk_data in audio_chunks_buffer:
          wav_file.write(chunk_data)
          total_bytes += len(chunk_data)
      print(f"✅ WAV file saved: {wav_output_path} ({total_bytes} bytes)")
    else:
      print("⚠️ No audio chunks to save")

  finally:
    audio_source.cleanup()


def main():
  asyncio.run(test_audio_source())
