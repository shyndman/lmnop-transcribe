#!/usr/bin/env python3
"""
Audio transcription pipeline implemented in RxPY with AsyncIO scheduler.
This is a port of the TypeScript reference implementation with real audio source.
"""

import argparse
import asyncio
import logging
from typing import cast

import reactivex as rx
from reactivex import operators as ops
from reactivex.scheduler.eventloop import AsyncIOScheduler
from reactivex.subject import Subject

from .audio_source import AudioConfig, AudioSource
from .common import AudioChunk, CancelEvent, Config, ControlEvent, KeyPressEvent, RecordingState
from .transcription_service import TranscriptionService

# Active transcription sessions tracking
active_sessions = {}


class MockDBusService:
  def publish_transcription(self, text: str):
    """Simulate publishing transcription via D-Bus"""
    print(f"📢 D-Bus: {text}")

  def publish_cancel(self, recording_id: float):
    """Simulate publishing cancel message via D-Bus"""
    print(f"📢 D-Bus: Cancelled recording {recording_id}")


def mock_save_to_wav_file(chunks: list[AudioChunk], filename: str):
  """Simulate saving audio chunks to WAV file"""
  total_bytes = sum(len(chunk.data) for chunk in chunks)
  print(f"💾 Saved {len(chunks)} chunks ({total_bytes} bytes) to {filename}")


def mock_show_notification(message: str):
  """Simulate showing desktop notification"""
  print(f"🔔 {message}")


def trim_audio_chunks(chunks: list[AudioChunk], trim_duration_ms: int) -> list[AudioChunk]:
  """Trim first n milliseconds from audio chunks based on delta timestamps"""
  trimmed_chunks = [chunk for chunk in chunks if chunk.timestamp_delta >= trim_duration_ms]
  print(f"✂️ Trimmed {len(chunks) - len(trimmed_chunks)} chunks from start ({trim_duration_ms}ms)")
  return trimmed_chunks


# Set up logging
logger = logging.getLogger(__name__)

# Global instances
config = Config()
dbus_service = MockDBusService()

# Event subjects for testing
key_press_events = Subject()
audio_chunks = Subject()


def create_pipeline(
  scheduler: AsyncIOScheduler,
  transcription_service: TranscriptionService,
  key_events_source=None,
  audio_source_instance: AudioSource | None = None,
  use_real_audio: bool = True,
):
  """
  Create the reactive audio transcription pipeline

  Args:
      scheduler: AsyncIO scheduler for reactive operations
      transcription_service: TranscriptionService instance for handling transcription sessions
      key_events_source: Observable of KeyPressEvent (defaults to global subject for testing)
      audio_source_instance: AudioSource instance for real audio (created if None and use_real_audio=True)
      use_real_audio: Whether to use real audio source or mock subjects for testing
  """

  # Use provided sources or fall back to global subjects for testing
  key_source = key_events_source if key_events_source is not None else key_press_events

  # Audio source setup
  if use_real_audio:
    if audio_source_instance is None:
      logger.info("Creating default AudioSource instance")

      audio_config = AudioConfig(
        # device = find_default_audio_device(),
        channels=1,
        samplerate=16000,
        blocksize=16000,  # 1 second of audio at 16kHz
        chunk_poll_interval_ms=20,  # Poll every 20ms for responsive audio
      )
      audio_source_instance = AudioSource(audio_config, scheduler)

    audio_source = audio_source_instance.create_audio_observable().pipe(ops.share())
    logger.info("Using real audio source")
  else:
    audio_source = audio_chunks
    logger.info("Using mock audio source for testing")

  # 1. Map key press events to control events
  control_events = key_source.pipe(
    ops.filter(lambda event: cast(KeyPressEvent, event).key in ["play_key", "stop_key", "cancel_key"]),
    ops.map(
      lambda event: ControlEvent(
        type={
          "play_key": "play",
          "stop_key": "stop",
          "cancel_key": "cancel",
        }[cast(KeyPressEvent, event).key],
        timestamp_delta=cast(KeyPressEvent, event).timestamp_delta,
      )
    ),
    ops.share(),
  )

  # 2. Track recording state
  def update_state(state: RecordingState, event: ControlEvent) -> RecordingState:
    if event.type == "play":
      return RecordingState(
        is_recording=True,
        start_time_delta=event.timestamp_delta,
        end_time_delta=None,
        action="play",
      )
    elif event.type in ["stop", "cancel"]:
      return RecordingState(
        is_recording=False,
        start_time_delta=state.get("start_time_delta"),
        end_time_delta=event.timestamp_delta,
        action=event.type,
      )
    return state

  initial_state: RecordingState = RecordingState(
    is_recording=False,
    start_time_delta=None,
    end_time_delta=None,
    action=None,
  )
  recording_state = control_events.pipe(
    ops.scan(update_state, seed=initial_state), ops.replay(1), ops.ref_count()
  )

  # 3. Create cancel events stream for cleanup
  cancel_events = recording_state.pipe(
    ops.filter(
      lambda state: (
        not cast(RecordingState, state)["is_recording"]
        and cast(RecordingState, state)["action"] == "cancel"
        and cast(RecordingState, state).get("start_time_delta") is not None
      )
    ),
    ops.map(
      lambda state: CancelEvent(recording_id=cast(float, cast(RecordingState, state)["start_time_delta"]))
    ),
  )

  # 4. Stream audio chunks to transcription with initial buffering for minimum duration
  def create_transcription_stream(recording_start_time):
    buffer = []
    buffer_released = False

    def process_chunk(chunk):
      nonlocal buffer, buffer_released

      if not buffer_released:
        buffer.append(chunk)
        if chunk.timestamp_delta >= cast(Config, config).minimum_recording_ms:
          # Release buffer
          logger.info(f"📤 Releasing buffer: {len(buffer)} chunks for transcription")
          trimmed_buffer = trim_audio_chunks(buffer, cast(Config, config).trim_duration_ms)
          buffer_released = True

          # Emit buffer release event
          return rx.from_(
            [
              {
                "type": "buffer_release",
                "chunks": trimmed_buffer,
                "recording_id": recording_start_time,
              },
              {
                "type": "stream_chunk",
                "chunk": chunk,
                "recording_id": recording_start_time,
              },
            ]
          )
        else:
          # Still buffering
          return rx.empty()
      else:
        # Stream directly
        logger.debug(f"📡 Streaming chunk: {chunk.timestamp_delta:.0f}ms")
        return rx.just(
          {
            "type": "stream_chunk",
            "chunk": chunk,
            "recording_id": recording_start_time,
          }
        )

    return audio_source.pipe(
      ops.do_action(
        lambda chunk: logger.info(f"🎵 Audio chunk: {chunk.timestamp_delta:.0f}ms, {len(chunk.data)} bytes")
      ),
      ops.flat_map(process_chunk),
      ops.take_until(
        recording_state.pipe(
          ops.filter(
            lambda s: not cast(RecordingState, s)["is_recording"]
            and cast(RecordingState, s).get("start_time_delta") == recording_start_time
          )
        )
      ),
    )

  transcription_stream = recording_state.pipe(
    ops.filter(lambda state: cast(RecordingState, state)["is_recording"]),
    ops.flat_map(lambda state: create_transcription_stream(cast(RecordingState, state)["start_time_delta"])),
    ops.share(),
  )

  return {
    "control_events": control_events,
    "recording_state": recording_state,
    "cancel_events": cancel_events,
    "transcription_stream": transcription_stream,
    "audio_source_instance": audio_source_instance if use_real_audio else None,
  }


async def async_main(
  use_real_audio: bool = False,
  use_keyboard_bridge: bool = False,
  wav_output_path: str | None = None,
  wyoming_server: str = "localhost:10300",
):
  """Main function to run the pipeline"""
  # Set up logging
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
  )
  logger = logging.getLogger(__name__)

  # Update global config
  global config
  config.save_wav_files = wav_output_path is not None
  config.wav_output_path = wav_output_path
  config.wyoming_server_address = wyoming_server

  # Initialize transcription service
  transcription_service = TranscriptionService(
    # TODO(shyndman): These should be config supplied
    channels=1,
    sample_width=2,
    rate=16000,
    wyoming_server_address=wyoming_server,
    save_wav_files=config.save_wav_files,
    wav_output_path=wav_output_path,
  )

  loop = asyncio.get_event_loop()
  scheduler = AsyncIOScheduler(loop)

  # Set up keyboard bridge if requested
  keyboard_bridge = None
  key_events_source = None

  if use_keyboard_bridge:
    try:
      from .keyboard_bridge import create_keyboard_bridge

      # Use the known keyboard device
      device_path = "/dev/input/event2"
      try:
        keyboard_bridge = create_keyboard_bridge(device_path, config)
        key_events_source = keyboard_bridge.observable
        logger.info(f"✅ Keyboard bridge initialized with device: {device_path}")
      except (PermissionError, FileNotFoundError, OSError):
        logger.exception(f"Failed to open keyboard device {device_path}")
        keyboard_bridge = None

      if keyboard_bridge is None:
        logger.warning("❌ Could not initialize keyboard bridge. Run as root or add user to input group.")
        logger.info("💡 Falling back to simulated keyboard events")
      else:
        await keyboard_bridge.start_monitoring()

    except ImportError as e:
      logger.warning(f"❌ Keyboard bridge not available: {e}")
      logger.info("💡 Falling back to simulated keyboard events")

  # Create pipeline
  pipeline = create_pipeline(
    scheduler, transcription_service, key_events_source=key_events_source, use_real_audio=use_real_audio
  )
  audio_source_instance = cast(AudioSource, pipeline["audio_source_instance"])

  # Subscribe to control events to control audio recording
  def on_control_event(event: ControlEvent):
    logger.info(f"🎛️ Control event: {event.type} at {event.timestamp_delta:.0f}ms")
    mock_show_notification(f"Recording {event.type}")

    if audio_source_instance:
      if event.type == "play":
        audio_source_instance.start_recording()
      elif event.type in ["stop", "cancel"]:
        audio_source_instance.stop_recording()

  pipeline["control_events"].subscribe(on_control_event, scheduler=scheduler)

  # Subscribe to recording state changes for debugging and session management
  def on_recording_state_change(state: RecordingState):
    logger.info(f"📊 State: {state}")

    # Start transcription session immediately when recording begins
    if state["is_recording"] and state["action"] == "play":
      session_id = str(state.get("start_time_delta"))

      # Create and start new transcription session
      async def start_new_session():
        try:
          logger.info(f"🎤 Creating new transcription session {session_id}")
          session = transcription_service.create_session(session_id)
          active_sessions[session_id] = session
          logger.info(f"📝 Session {session_id} added to active_sessions. Total: {len(active_sessions)}")
          session.begin_session()
          logger.info(f"✅ Transcription session {session_id} started")
        except Exception:
          logger.exception(f"❌ Error starting transcription session {session_id}")

      # Schedule the session start
      asyncio.create_task(start_new_session())

    # End transcription session when recording stops
    elif not state["is_recording"] and state["action"] in ["stop", "cancel"]:
      session_id = str(state.get("start_time_delta"))
      if session_id in active_sessions:
        session = active_sessions[session_id]

        async def end_streaming_session():
          try:
            if state["action"] == "stop":
              logger.info(f"⏹️ Ending transcription session {session_id}")
              result = session.end_session()
              if result:
                logger.info(f"📝 Transcription result: {result}")
                dbus_service.publish_transcription(result)
              else:
                logger.warning("❌ No transcription result")
            else:  # cancel
              logger.info(f"❌ Cancelling transcription session {session_id}")
              session.cancel_session()
              dbus_service.publish_cancel(float(session_id))
          except Exception:
            logger.exception(f"❌ Error ending transcription session {session_id}")
          finally:
            # Clean up session
            if session_id in active_sessions:
              del active_sessions[session_id]

        # Schedule the session end
        asyncio.create_task(end_streaming_session())

  pipeline["recording_state"].subscribe(on_recording_state_change, scheduler=scheduler)

  # Subscribe to transcription stream
  def on_transcription_event(event):
    if event["type"] == "buffer_release":
      logger.info(
        f"📤 Buffer released to transcription: {len(event['chunks'])} chunks "
        f"(recording {event['recording_id']})"
      )

      # Send buffered chunks to existing session
      session_id = str(event["recording_id"])
      if session_id in active_sessions:
        session = active_sessions[session_id]

        # Send all buffered chunks to the existing session
        async def send_buffered_chunks():
          try:
            for chunk in event["chunks"]:
              session.add_chunk(chunk)
            logger.info(f"📤 Sent {len(event['chunks'])} buffered chunks to session {session_id}")
          except Exception:
            logger.exception(f"❌ Error sending buffered chunks to session {session_id}")

        # Schedule the chunk sending
        asyncio.create_task(send_buffered_chunks())
      else:
        logger.warning(f"⚠️ No active session found for recording {session_id}")

    elif event["type"] == "stream_chunk":
      logger.debug(
        f"📡 Streaming chunk to transcription: {event['chunk'].timestamp_delta:.0f}ms "
        f"(recording {event['recording_id']})"
      )

      # Add chunk to active session if exists
      session_id = str(event["recording_id"])
      if session_id in active_sessions:
        try:
          active_sessions[session_id].add_chunk(event["chunk"])
          logger.info(
            f"📡 Sent streaming chunk to session {session_id}: {event['chunk'].timestamp_delta:.0f}ms"
          )
        except Exception:
          logger.exception(f"❌ Error adding chunk to session {session_id}")
      else:
        logger.warning(f"⚠️ No active session found for streaming chunk (recording {session_id})")

  pipeline["transcription_stream"].subscribe(
    on_transcription_event,
    on_error=lambda e: logger.exception("❌ Error in transcription stream"),
    scheduler=scheduler,
  )

  print(f"🚀 Pipeline started with {'real' if use_real_audio else 'mock'} audio source")

  try:
    if use_real_audio or use_keyboard_bridge:
      if use_keyboard_bridge:
        print("🎙️ Real mode: Press Caps Lock to record, Shift to cancel, Ctrl+C to stop")
      else:
        print("🎙️ Real audio mode: Press Ctrl+C to stop")
      # In real mode, wait for keyboard interrupt
      while True:
        await asyncio.sleep(1)
    else:
      # Simulate some events for testing
      await asyncio.sleep(0.1)

      # Simulate a recording session with delta timestamps
      print("⏰ Starting recording at 0ms")
      key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=0))

      await asyncio.sleep(0.2)  # Let recording start

      # Simulate audio chunks DURING recording
      print("🎤 Emitting audio chunks...")
      for i in range(5):
        chunk_time_delta = (i + 1) * 200
        print(f"🎵 Chunk {i} at {chunk_time_delta}ms")
        audio_chunks.on_next(AudioChunk(data=f"chunk_{i}".encode(), timestamp_delta=chunk_time_delta))
        await asyncio.sleep(0.1)

      await asyncio.sleep(0.2)

      # Stop recording after sufficient time
      print("⏹️ Stopping recording at 1500ms")
      key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=1500))

      await asyncio.sleep(1)
      print("✅ Pipeline test completed")

  except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
    return
  finally:
    if keyboard_bridge:
      keyboard_bridge.stop_monitoring()
    if audio_source_instance:
      audio_source_instance.cleanup()


def parse_args():
  """Parse command-line arguments"""
  parser = argparse.ArgumentParser(description="Audio transcription pipeline")
  parser.add_argument(
    "--mock-audio",
    action="store_true",
    help="Use mock audio source instead of real audio",
  )
  parser.add_argument("--no-keyboard", action="store_true", help="Disable keyboard bridge input events")
  parser.add_argument(
    "--save-wav",
    type=str,
    metavar="PATH",
    help="Path to save recorded audio as WAV files",
  )
  parser.add_argument(
    "--wyoming-server",
    type=str,
    default="localhost:10300",
    help="Wyoming ASR server address (default: localhost:10300)",
  )
  return parser.parse_args()


def main():
  args = parse_args()
  try:
    asyncio.run(
      async_main(
        use_real_audio=not args.mock_audio,
        use_keyboard_bridge=not args.no_keyboard,
        wav_output_path=args.save_wav,
        wyoming_server=args.wyoming_server,
      )
    )
  except KeyboardInterrupt:
    pass
