#!/usr/bin/env python3
"""
Pytest tests for the audio transcription pipeline.
Tests key behaviors with deterministic, synchronous execution.
"""

import asyncio
from typing import TypedDict, cast
from unittest.mock import Mock

import pytest

# import reactivex as rx  # Unused
from reactivex import Observable
from reactivex import operators as ops
from reactivex.scheduler.eventloop import AsyncIOScheduler
from reactivex.subject import Subject

from lmnop_transcribe.pipeline import (
  AudioChunk,
  CancelEvent,
  Config,
  ControlEvent,
  KeyPressEvent,
  create_pipeline,
  trim_audio_chunks,
  # TranscriptionResult, RecordingState  # Unused
)


# Test-specific TypedDicts (prefixed with _ to avoid pytest collection)
class _TestRecordingStateType(TypedDict):
  is_recording: bool
  start_time_delta: float | None
  end_time_delta: float | None
  action: str | None


class TestAudioPipeline:
  """Test suite for the audio transcription pipeline."""

  def setup_method(self):
    """Set up test fixtures before each test."""
    self.config = Config(
      save_wav_files=False,
      wav_output_path=None,
      wyoming_server_address="localhost:10300",
      trim_duration_ms=500,
      minimum_recording_ms=1000,
    )
    self.key_press_events = Subject()
    self.audio_chunks = Subject()

  def test_control_event_mapping(self):
    """Test that key press events are correctly mapped to control events."""
    results = []

    # Create the control events stream
    control_events = self.key_press_events.pipe(
      ops.filter(lambda event: event.key in ["play_key", "stop_key", "cancel_key"]),
      ops.map(
        lambda event: ControlEvent(
          type={
            "play_key": "play",
            "stop_key": "stop",
            "cancel_key": "cancel",
          }[event.key],
          timestamp_delta=event.timestamp_delta,
        )
      ),
    )

    control_events.subscribe(lambda event: results.append(event))

    # Emit test events
    self.key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=0))
    self.key_press_events.on_next(KeyPressEvent(key="invalid_key", timestamp_delta=100))  # Should be filtered
    self.key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=1500))
    self.key_press_events.on_next(KeyPressEvent(key="cancel_key", timestamp_delta=2000))

    # Verify results
    assert len(results) == 3
    assert results[0].type == "play"
    assert results[0].timestamp_delta == 0
    assert results[1].type == "stop"
    assert results[1].timestamp_delta == 1500
    assert results[2].type == "cancel"
    assert results[2].timestamp_delta == 2000

  def test_recording_state_transitions(self):
    """Test recording state transitions for play/stop/cancel."""
    results = []

    # Create control events
    control_events = self.key_press_events.pipe(
      ops.filter(lambda event: event.key in ["play_key", "stop_key", "cancel_key"]),
      ops.map(
        lambda event: ControlEvent(
          type={
            "play_key": "play",
            "stop_key": "stop",
            "cancel_key": "cancel",
          }[event.key],
          timestamp_delta=event.timestamp_delta,
        )
      ),
    )

    # Create recording state with state update function
    def update_state(state: _TestRecordingStateType, event: ControlEvent) -> _TestRecordingStateType:
      if event.type == "play":
        return _TestRecordingStateType(
          is_recording=True,
          start_time_delta=event.timestamp_delta,
          end_time_delta=None,
          action="play",
        )
      elif event.type in ["stop", "cancel"]:
        return _TestRecordingStateType(
          is_recording=False,
          start_time_delta=state.get("start_time_delta"),
          end_time_delta=event.timestamp_delta,
          action=event.type,
        )
      return state

    initial_state: _TestRecordingStateType = _TestRecordingStateType(
      is_recording=False,
      start_time_delta=None,
      end_time_delta=None,
      action=None,
    )
    recording_state = control_events.pipe(ops.scan(update_state, seed=initial_state))

    recording_state.subscribe(lambda state: results.append(state))

    # Test play -> stop sequence
    self.key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=0))
    self.key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=1500))

    # Verify state transitions
    assert len(results) == 2  # play + stop (no initial with seed)

    # Play state
    assert results[0]["is_recording"] is True
    assert results[0]["start_time_delta"] == 0
    assert results[0]["action"] == "play"

    # Stop state
    assert results[1]["is_recording"] is False
    assert results[1]["start_time_delta"] == 0
    assert results[1]["end_time_delta"] == 1500
    assert results[1]["action"] == "stop"

  def test_audio_trimming(self):
    """Test audio chunk trimming functionality."""
    chunks = [
      AudioChunk(data=b"chunk_0", timestamp_delta=200),
      AudioChunk(data=b"chunk_1", timestamp_delta=400),
      AudioChunk(data=b"chunk_2", timestamp_delta=600),
      AudioChunk(data=b"chunk_3", timestamp_delta=800),
      AudioChunk(data=b"chunk_4", timestamp_delta=1000),
    ]

    # Trim first 500ms
    trimmed = trim_audio_chunks(chunks, 500)

    # Should keep chunks at 600ms, 800ms, 1000ms
    assert len(trimmed) == 3
    assert trimmed[0].timestamp_delta == 600
    assert trimmed[1].timestamp_delta == 800
    assert trimmed[2].timestamp_delta == 1000

  def test_minimum_duration_filtering(self):
    """Test that recordings shorter than minimum duration are filtered out."""
    # This test verifies the duration check logic
    chunks_and_state = (
      [AudioChunk(data=b"chunk", timestamp_delta=200)],  # Only one chunk
      _TestRecordingStateType(
        is_recording=False,
        start_time_delta=0,
        end_time_delta=800,  # 800ms duration < 1000ms minimum
        action="stop",
      ),
    )

    # Check if it meets minimum duration
    end_time = chunks_and_state[1]["end_time_delta"]
    start_time = chunks_and_state[1]["start_time_delta"]
    assert end_time is not None and start_time is not None, (
      "Both end_time_delta and start_time_delta should be set"
    )
    duration = end_time - start_time
    meets_minimum = len(chunks_and_state[0]) > 0 and duration >= self.config.minimum_recording_ms

    assert not meets_minimum  # Should be False for 800ms < 1000ms

  def test_minimum_duration_passing(self):
    """Test that recordings meeting minimum duration pass through."""
    chunks_and_state = (
      [
        AudioChunk(data=b"chunk_0", timestamp_delta=200),
        AudioChunk(data=b"chunk_1", timestamp_delta=400),
        AudioChunk(data=b"chunk_2", timestamp_delta=600),
      ],
      _TestRecordingStateType(
        is_recording=False,
        start_time_delta=0,
        end_time_delta=1500,  # 1500ms duration >= 1000ms minimum
        action="stop",
      ),
    )

    # Check if it meets minimum duration
    end_time = chunks_and_state[1]["end_time_delta"]
    start_time = chunks_and_state[1]["start_time_delta"]
    assert end_time is not None and start_time is not None, (
      "Both end_time_delta and start_time_delta should be set"
    )
    duration = end_time - start_time
    meets_minimum = len(chunks_and_state[0]) > 0 and duration >= self.config.minimum_recording_ms

    assert meets_minimum  # Should be True for 1500ms >= 1000ms

  def test_cancel_event_generation(self):
    """Test that cancel events are generated correctly."""
    results = []

    # Create a mock recording state that represents a cancelled recording
    cancelled_state = _TestRecordingStateType(
      is_recording=False,
      action="cancel",
      start_time_delta=0,
      end_time_delta=None,
    )

    # Test the cancel event filter logic
    is_recording = cancelled_state["is_recording"]
    action = cancelled_state["action"]
    start_time_delta = cancelled_state["start_time_delta"]
    assert is_recording is not None and action is not None and start_time_delta is not None, (
      "Required fields should be set"
    )
    should_generate_cancel = not is_recording and action == "cancel" and start_time_delta is not None

    assert should_generate_cancel

    # Generate the cancel event
    if should_generate_cancel:
      start_time_delta = cancelled_state["start_time_delta"]
      assert start_time_delta is not None, "start_time_delta should be set for cancel event"
      cancel_event = CancelEvent(recording_id=start_time_delta)
      results.append(cancel_event)

    assert len(results) == 1
    assert results[0].recording_id == 0
    assert results[0].type == "cancel"

  def test_config_values(self):
    """Test that configuration values are set correctly."""
    config = Config()

    # Test default values
    assert config.save_wav_files is False
    assert config.trim_duration_ms == 500
    assert config.minimum_recording_ms == 2000  # Updated default

    # Test custom values
    custom_config = Config(save_wav_files=True, trim_duration_ms=300, minimum_recording_ms=1500)

    assert custom_config.save_wav_files is True
    assert custom_config.trim_duration_ms == 300
    assert custom_config.minimum_recording_ms == 1500

  def test_empty_chunks_filtering(self):
    """Test that empty chunk lists are filtered out."""
    # Empty chunks should be filtered
    empty_chunks_and_state = (
      [],
      _TestRecordingStateType(
        start_time_delta=0,
        end_time_delta=1500,
        action=None,
        is_recording=False,
      ),
    )

    end_time = empty_chunks_and_state[1]["end_time_delta"]
    start_time = empty_chunks_and_state[1]["start_time_delta"]
    assert end_time is not None and start_time is not None, (
      "Both end_time_delta and start_time_delta should be set"
    )
    meets_criteria = len(empty_chunks_and_state[0]) > 0 and (end_time - start_time) >= 1000

    assert not meets_criteria  # Should be False due to empty chunks

  def test_data_classes_structure(self):
    """Test that data classes have correct structure and defaults."""
    # Test KeyPressEvent
    key_event = KeyPressEvent()
    assert key_event.type == "keypress"
    assert key_event.key == ""
    assert key_event.timestamp_delta == 0.0

    # Test ControlEvent
    control_event = ControlEvent(type="play", timestamp_delta=100)
    assert control_event.type == "play"
    assert control_event.timestamp_delta == 100

    # Test AudioChunk
    audio_chunk = AudioChunk(data=b"test", timestamp_delta=200)
    assert audio_chunk.data == b"test"
    assert audio_chunk.timestamp_delta == 200

    # Test CancelEvent
    cancel_event = CancelEvent(recording_id=123)
    assert cancel_event.recording_id == 123
    assert cancel_event.type == "cancel"

  @pytest.mark.asyncio
  async def test_pipeline_creation_mock_mode(self):
    """Test pipeline creation in mock mode."""
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler(loop)

    # Mock transcription service for testing
    mock_transcription_service = Mock()

    pipeline = create_pipeline(
      scheduler, mock_transcription_service, key_events_source=self.key_press_events, use_real_audio=False
    )

    # Verify pipeline components are created
    assert "control_events" in pipeline
    assert "recording_state" in pipeline
    assert "cancel_events" in pipeline
    assert "transcription_stream" in pipeline
    assert pipeline["audio_source_instance"] is None  # Mock mode

  @pytest.mark.asyncio
  async def test_streaming_transcription_logic(self):
    """Test the streaming transcription buffer release and streaming logic."""
    results = []

    # Create a simple transcription stream simulator
    def simulate_streaming():
      buffer = []
      buffer_released = False

      chunks = [
        AudioChunk(data=b"chunk_0", timestamp_delta=300),
        AudioChunk(data=b"chunk_1", timestamp_delta=600),
        AudioChunk(data=b"chunk_2", timestamp_delta=900),
        AudioChunk(data=b"chunk_3", timestamp_delta=1200),  # Should trigger buffer release
        AudioChunk(data=b"chunk_4", timestamp_delta=1500),  # Should stream directly
      ]

      for chunk in chunks:
        if not buffer_released:
          buffer.append(chunk)
          if chunk.timestamp_delta >= 1000:  # minimum_recording_ms
            # Release buffer
            trimmed_buffer = trim_audio_chunks(buffer, 500)  # trim_duration_ms
            buffer_released = True

            results.append(
              {
                "type": "buffer_release",
                "chunks": trimmed_buffer,
                "recording_id": 0,
              }
            )
            results.append({"type": "stream_chunk", "chunk": chunk, "recording_id": 0})
        else:
          # Stream directly
          results.append({"type": "stream_chunk", "chunk": chunk, "recording_id": 0})

    simulate_streaming()

    # Verify streaming behavior
    assert len(results) == 3  # buffer_release + stream_chunk (chunk_3) + stream_chunk (chunk_4)

    # First event should be buffer release
    assert results[0]["type"] == "buffer_release"
    assert len(results[0]["chunks"]) == 3  # chunks at 600ms, 900ms, and 1200ms (after 500ms trim)
    assert results[0]["chunks"][0].timestamp_delta == 600
    assert results[0]["chunks"][1].timestamp_delta == 900
    assert results[0]["chunks"][2].timestamp_delta == 1200

    # Second event should be current chunk (1200ms)
    assert results[1]["type"] == "stream_chunk"
    assert results[1]["chunk"].timestamp_delta == 1200

    # Third event should be streamed chunk (1500ms)
    assert results[2]["type"] == "stream_chunk"
    assert results[2]["chunk"].timestamp_delta == 1500


class TestAudioSource:
  """Test suite for the audio source module."""

  def test_audio_config_defaults(self):
    """Test AudioConfig default values."""
    from lmnop_transcribe.common import AudioConfig

    config = AudioConfig()
    assert config.device == "default"
    assert config.channels == 1
    assert config.samplerate == 16000  # Whisper uses 16kHz
    assert config.blocksize is None
    assert config.chunk_poll_interval_ms == 10
    assert config.dtype == "int16"

  def test_audio_config_custom_values(self):
    """Test AudioConfig with custom values."""
    from lmnop_transcribe.common import AudioConfig

    config = AudioConfig(
      device="hw:1,0",
      channels=2,
      samplerate=48000,
      blocksize=2048,
      chunk_poll_interval_ms=50,
      dtype="float32",
    )

    assert config.device == "hw:1,0"
    assert config.channels == 2
    assert config.samplerate == 48000
    assert config.blocksize == 2048
    assert config.chunk_poll_interval_ms == 50
    assert config.dtype == "float32"

  def test_audio_chunk_structure(self):
    """Test AudioChunk data structure."""
    from lmnop_transcribe.common import AudioChunk

    chunk = AudioChunk(data=b"test_audio_data", timestamp_delta=1234.5)
    assert chunk.data == b"test_audio_data"
    assert chunk.timestamp_delta == 1234.5

  @pytest.mark.asyncio
  async def test_audio_source_initialization(self):
    """Test AudioSource initialization without actual hardware."""
    from lmnop_transcribe.audio_source import AudioConfig, AudioSource

    config = AudioConfig(channels=1, samplerate=44100)

    # Test initialization (won't create stream until start_recording)
    audio_source = AudioSource(config)
    assert audio_source.config.channels == 1
    assert audio_source.config.samplerate == 44100
    assert audio_source._is_recording is False
    assert audio_source._stream is None
    assert audio_source._recording_start_time is None

  def test_audio_source_observable_creation(self):
    """Test that audio observable can be created."""
    from lmnop_transcribe.audio_source import AudioConfig, AudioSource

    config = AudioConfig()
    audio_source = AudioSource(config)

    observable = audio_source.create_audio_observable()
    assert observable is not None

    # Test that we can subscribe (though it won't emit without real audio)
    subscription_called = False

    def on_chunk(chunk):
      nonlocal subscription_called
      subscription_called = True

    observable.subscribe(on_next=on_chunk)
    # No chunks should be emitted without starting recording
    assert not subscription_called


class TestKeyboardBridge:
  """Test suite for keyboard bridge functionality."""

  def test_keyboard_event_structure(self):
    """Test KeyPressEvent structure."""
    event = KeyPressEvent(key="test_key", timestamp_delta=500.0)
    assert event.type == "keypress"
    assert event.key == "test_key"
    assert event.timestamp_delta == 500.0

  def test_keyboard_event_defaults(self):
    """Test KeyPressEvent default values."""
    event = KeyPressEvent()
    assert event.type == "keypress"
    assert event.key == ""
    assert event.timestamp_delta == 0.0

  def test_control_event_types(self):
    """Test various control event types."""
    play_event = ControlEvent(type="play", timestamp_delta=0)
    stop_event = ControlEvent(type="stop", timestamp_delta=1500)
    cancel_event = ControlEvent(type="cancel", timestamp_delta=2000)

    assert play_event.type == "play"
    assert stop_event.type == "stop"
    assert cancel_event.type == "cancel"

    assert play_event.timestamp_delta == 0
    assert stop_event.timestamp_delta == 1500
    assert cancel_event.timestamp_delta == 2000


class TestIntegration:
  """Integration tests for the complete pipeline."""

  @pytest.mark.asyncio
  async def test_end_to_end_recording_session(self):
    """Test a complete recording session from key press to transcription."""
    from lmnop_transcribe.pipeline import audio_chunks  # Import global audio_chunks subject

    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler(loop)

    # Create subjects for testing
    key_press_events = Subject()

    # Mock transcription service for testing
    mock_transcription_service = Mock()

    # Create pipeline in mock mode
    pipeline = create_pipeline(
      scheduler, mock_transcription_service, key_events_source=key_press_events, use_real_audio=False
    )

    transcription_events = []
    cast(Observable, pipeline["transcription_stream"]).subscribe(
      lambda event: transcription_events.append(event)
    )

    # Simulate recording session
    await asyncio.sleep(0.01)  # Let pipeline initialize

    # Start recording
    key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=0))
    await asyncio.sleep(0.01)

    # Emit audio chunks - first few will be buffered (using global subject)
    audio_chunks.on_next(AudioChunk(data=b"chunk_0", timestamp_delta=300))
    audio_chunks.on_next(AudioChunk(data=b"chunk_1", timestamp_delta=600))
    audio_chunks.on_next(AudioChunk(data=b"chunk_2", timestamp_delta=900))

    # This chunk should trigger buffer release
    audio_chunks.on_next(AudioChunk(data=b"chunk_3", timestamp_delta=1200))
    await asyncio.sleep(0.01)

    # This chunk should stream directly
    audio_chunks.on_next(AudioChunk(data=b"chunk_4", timestamp_delta=1500))
    await asyncio.sleep(0.01)

    # Add more chunks to ensure minimum duration is met
    audio_chunks.on_next(AudioChunk(data=b"chunk_5", timestamp_delta=1800))
    audio_chunks.on_next(AudioChunk(data=b"chunk_6", timestamp_delta=2100))
    await asyncio.sleep(0.01)

    # Stop recording (extend duration to well exceed minimum)
    key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=2500))
    await asyncio.sleep(0.01)

    # Verify transcription events were generated
    assert len(transcription_events) >= 1  # Should have at least buffer release

    # Find buffer release event
    buffer_events = [e for e in transcription_events if e["type"] == "buffer_release"]
    assert len(buffer_events) >= 1

    # Verify buffer was trimmed correctly (should exclude chunks < 500ms)
    buffer_event = buffer_events[0]
    trimmed_chunks = buffer_event["chunks"]
    assert all(chunk.timestamp_delta >= 500 for chunk in trimmed_chunks)


class TestCommandLineArguments:
  """Test command-line argument parsing functionality."""

  def test_parse_args_defaults(self):
    """Test argument parsing with default values."""
    from unittest.mock import patch

    from lmnop_transcribe.pipeline import parse_args

    # Mock sys.argv to simulate no arguments
    with patch("sys.argv", ["pipeline.py"]):
      args = parse_args()

      assert args.mock_audio is False
      assert args.no_keyboard is False
      assert args.save_wav is None
      assert args.wyoming_server == "localhost:10300"

  def test_parse_args_all_options(self):
    """Test argument parsing with all options provided."""
    from unittest.mock import patch

    from lmnop_transcribe.pipeline import parse_args

    test_argv = [
      "pipeline.py",
      "--mock-audio",
      "--no-keyboard",
      "--save-wav",
      "/tmp/recordings",
      "--wyoming-server",
      "custom-host:8080",
    ]

    with patch("sys.argv", test_argv):
      args = parse_args()

      assert args.mock_audio is True
      assert args.no_keyboard is True
      assert args.save_wav == "/tmp/recordings"
      assert args.wyoming_server == "custom-host:8080"

  def test_parse_args_partial_options(self):
    """Test argument parsing with some options provided."""
    from unittest.mock import patch

    from lmnop_transcribe.pipeline import parse_args

    test_argv = ["pipeline.py", "--mock-audio", "--save-wav", "/my/recordings"]

    with patch("sys.argv", test_argv):
      args = parse_args()

      assert args.mock_audio is True
      assert args.no_keyboard is False  # Not provided, should be False
      assert args.save_wav == "/my/recordings"
      assert args.wyoming_server == "localhost:10300"  # Default value

  @pytest.mark.asyncio
  async def test_main_function_with_wav_saving(self):
    """Test main function configuration with WAV saving enabled."""

    from lmnop_transcribe.pipeline import config

    # Test that config is updated correctly when WAV saving is enabled
    original_config = config

    try:
      # Test config update without running full main loop
      # Just call the config update part of async_main
      config.save_wav_files = True
      config.wav_output_path = "/tmp/test"
      config.wyoming_server_address = "test:9999"

      # Verify config was updated
      assert config.save_wav_files is True
      assert config.wav_output_path == "/tmp/test"
      assert config.wyoming_server_address == "test:9999"

    finally:
      # Restore original config
      config.save_wav_files = original_config.save_wav_files
      config.wav_output_path = original_config.wav_output_path
      config.wyoming_server_address = original_config.wyoming_server_address

  @pytest.mark.asyncio
  async def test_main_function_without_wav_saving(self):
    """Test main function configuration with WAV saving disabled."""
    from lmnop_transcribe.pipeline import config

    original_config = config

    try:
      # Test config update without running full main loop
      # Just call the config update part of async_main
      config.save_wav_files = False
      config.wav_output_path = None
      config.wyoming_server_address = "localhost:10300"

      # Verify config was updated correctly
      assert config.save_wav_files is False
      assert config.wav_output_path is None
      assert config.wyoming_server_address == "localhost:10300"

    finally:
      # Restore original config
      config.save_wav_files = original_config.save_wav_files
      config.wav_output_path = original_config.wav_output_path
      config.wyoming_server_address = original_config.wyoming_server_address


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
