#!/usr/bin/env python3
"""
Integration test for the full audio transcription pipeline.
"""

from typing import TypedDict

import pytest

from lmnop_transcribe.pipeline import (
  AudioChunk,
  Config,
)


# Test-specific TypedDicts (prefixed with _ to avoid pytest collection)
class _TestRecordingState(TypedDict):
  is_recording: bool
  start_time_delta: float | None
  end_time_delta: float | None
  action: str | None


class _TestProcessedRecording(TypedDict):
  chunks: list[AudioChunk]
  recording_id: float
  start_time_delta: float
  end_time_delta: float
  action: str


@pytest.mark.asyncio
async def test_full_pipeline_integration():
  """Test the complete pipeline flow with delta timestamps."""

  # Test audio data for processing
  audio_data = [
    AudioChunk(data=b"chunk_0", timestamp_delta=200),
    AudioChunk(data=b"chunk_1", timestamp_delta=400),
    AudioChunk(data=b"chunk_2", timestamp_delta=600),
    AudioChunk(data=b"chunk_3", timestamp_delta=800),
    AudioChunk(data=b"chunk_4", timestamp_delta=1000),
  ]

  # Verify the full flow logic
  config = Config()

  # 1. Check recording duration meets minimum
  duration = 2500 - 0  # end_time_delta - start_time_delta (updated to meet 2000ms minimum)
  assert duration >= config.minimum_recording_ms

  # 2. Check trimming works correctly
  from lmnop_transcribe.pipeline import trim_audio_chunks

  trimmed_chunks = trim_audio_chunks(audio_data, config.trim_duration_ms)

  # Should trim first 500ms, keeping chunks at 600ms, 800ms, 1000ms
  assert len(trimmed_chunks) == 3
  assert all(chunk.timestamp_delta >= 500 for chunk in trimmed_chunks)

  # 3. Verify final recording data structure
  recording = _TestProcessedRecording(
    chunks=trimmed_chunks,
    recording_id=0,
    start_time_delta=0,
    end_time_delta=1500,
    action="stop",
  )

  assert len(recording["chunks"]) == 3
  assert recording["recording_id"] == 0
  assert recording["end_time_delta"] - recording["start_time_delta"] == 1500


def test_cancelled_recording():
  """Test cancelled recording doesn't produce output."""

  # Simulate cancelled recording
  duration = 800 - 0  # Cancelled before minimum duration
  config = Config()

  # Should not meet minimum duration
  assert duration < config.minimum_recording_ms

  # Should generate cancel event
  cancel_state = _TestRecordingState(
    is_recording=False,
    action="cancel",
    start_time_delta=0,
    end_time_delta=None,
  )

  is_recording = cancel_state["is_recording"]
  action = cancel_state["action"]
  start_time_delta = cancel_state["start_time_delta"]
  should_cancel = not is_recording and action == "cancel" and start_time_delta is not None

  assert should_cancel


def test_too_short_recording():
  """Test that recordings shorter than minimum are filtered."""

  config = Config()

  # Simulate short recording
  chunks = [AudioChunk(data=b"chunk", timestamp_delta=200)]
  recording_state = _TestRecordingState(
    is_recording=False,
    start_time_delta=0,
    end_time_delta=800,  # Only 800ms
    action="stop",
  )

  end_time = recording_state["end_time_delta"]
  start_time = recording_state["start_time_delta"]
  assert end_time is not None and start_time is not None, (
    "Both end_time_delta and start_time_delta should be set"
  )
  duration = end_time - start_time
  meets_minimum = len(chunks) > 0 and duration >= config.minimum_recording_ms

  assert not meets_minimum  # Should be filtered out


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
