#!/usr/bin/env python3
"""
Test script to verify that multiple play events create separate transcription sessions.
"""

import asyncio
import logging
from unittest.mock import Mock, patch

# Mock Wyoming modules before importing
mock_wyoming_modules = {
  "wyoming": Mock(),
  "wyoming.asr": Mock(),
  "wyoming.audio": Mock(),
  "wyoming.event": Mock(),
}

with patch.dict("sys.modules", mock_wyoming_modules):
  from reactivex.scheduler.eventloop import AsyncIOScheduler
  from reactivex.subject import Subject

  from lmnop_transcribe.common import KeyPressEvent
  from lmnop_transcribe.pipeline import active_sessions, create_pipeline
  from lmnop_transcribe.transcription_service import TranscriptionService


async def test_multiple_sessions():
  """Test that multiple play events create separate transcription sessions."""
  # Set up logging
  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

  print("🧪 Testing multiple transcription sessions...")

  # Clear any existing sessions
  active_sessions.clear()

  # Create mocks for Wyoming
  with (
    patch("lmnop_transcribe.transcription_service.socket.create_connection") as mock_conn,
    patch("lmnop_transcribe.transcription_service.write_event"),
    patch("lmnop_transcribe.transcription_service.read_event") as mock_read,
  ):
    # Setup mocks
    mock_socket = Mock()
    mock_file_wb = Mock()
    mock_file_rb = Mock()
    mock_socket.makefile.side_effect = lambda mode: mock_file_wb if "w" in mode else mock_file_rb
    mock_conn.return_value = mock_socket

    mock_transcript_event = Mock()
    mock_read.return_value = mock_transcript_event

    with patch("lmnop_transcribe.transcription_service.Transcript") as mock_transcript_class:
      mock_transcript_class.is_type.return_value = True
      mock_transcript = Mock()
      mock_transcript.text = "Test transcription"
      mock_transcript_class.from_event.return_value = mock_transcript

      # Create transcription service
      transcription_service = TranscriptionService("localhost:10300")

      # Create scheduler and subjects for testing
      loop = asyncio.get_event_loop()
      scheduler = AsyncIOScheduler(loop)
      key_press_events = Subject()
      _audio_chunks = Subject()

      # Create pipeline with mock audio
      pipeline = create_pipeline(
        scheduler, transcription_service, key_events_source=key_press_events, use_real_audio=False
      )

      # Subscribe to events for debugging
      pipeline["recording_state"].subscribe(lambda state: print(f"📊 State: {state}"), scheduler=scheduler)

      print("🎮 Starting first recording session...")

      # First recording session
      key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=0))

      # Wait for all scheduled tasks to complete
      await asyncio.sleep(0.1)
      pending_tasks = [task for task in asyncio.all_tasks() if not task.done()]
      if pending_tasks:
        print(f"⏳ Waiting for {len(pending_tasks)} pending tasks...")
        await asyncio.gather(*pending_tasks, return_exceptions=True)
      await asyncio.sleep(0.1)  # Additional wait

      print(f"🔢 Active sessions after first play: {len(active_sessions)}")
      assert len(active_sessions) == 1, f"Expected 1 session, got {len(active_sessions)}"
      first_session_id = list(active_sessions.keys())[0]
      print(f"✅ First session created: {first_session_id}")

      # Stop first session
      key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=1000))
      await asyncio.sleep(0.1)  # Let session end

      print(f"🔢 Active sessions after first stop: {len(active_sessions)}")

      print("🎮 Starting second recording session...")

      # Second recording session
      key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=2000))
      await asyncio.sleep(0.1)  # Let session start

      print(f"🔢 Active sessions after second play: {len(active_sessions)}")
      assert len(active_sessions) == 1, f"Expected 1 session, got {len(active_sessions)}"
      second_session_id = list(active_sessions.keys())[0]
      print(f"✅ Second session created: {second_session_id}")

      # Verify sessions have different IDs
      assert first_session_id != second_session_id, "Sessions should have different IDs"
      print(f"✅ Sessions have different IDs: {first_session_id} vs {second_session_id}")

      # Stop second session
      key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=3000))
      await asyncio.sleep(0.1)  # Let session end

      print(f"🔢 Active sessions after second stop: {len(active_sessions)}")

      print("🎮 Testing overlapping sessions...")

      # Test overlapping sessions (start new before stopping old)
      key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=4000))
      await asyncio.sleep(0.1)

      key_press_events.on_next(KeyPressEvent(key="play_key", timestamp_delta=5000))
      await asyncio.sleep(0.1)

      print(f"🔢 Active sessions with overlap: {len(active_sessions)}")
      assert len(active_sessions) == 2, f"Expected 2 overlapping sessions, got {len(active_sessions)}"

      session_ids = list(active_sessions.keys())
      print(f"✅ Overlapping sessions: {session_ids}")

      # Clean up
      key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=6000))
      key_press_events.on_next(KeyPressEvent(key="stop_key", timestamp_delta=7000))
      await asyncio.sleep(0.2)

      print("✅ All tests passed! Multiple sessions work correctly.")


if __name__ == "__main__":
  asyncio.run(test_multiple_sessions())
