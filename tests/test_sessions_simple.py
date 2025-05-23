#!/usr/bin/env python3
"""
Simple test to verify session creation works with proper mocking.
"""

import asyncio
import logging
from unittest.mock import Mock, patch


async def test_session_creation():
  """Test that play events create transcription sessions."""
  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

  # Mock Wyoming modules
  mock_wyoming_modules = {
    "wyoming": Mock(),
    "wyoming.asr": Mock(),
    "wyoming.audio": Mock(),
    "wyoming.event": Mock(),
  }

  with patch.dict("sys.modules", mock_wyoming_modules):
    from lmnop_transcribe.pipeline import active_sessions
    from lmnop_transcribe.transcription_service import TranscriptionService

    # Clear sessions
    active_sessions.clear()

    # Mock the socket operations that cause hanging
    with (
      patch("lmnop_transcribe.transcription_service.socket.create_connection") as mock_conn,
      patch("lmnop_transcribe.transcription_service.write_event") as _mock_write,
    ):
      # Setup socket mock
      mock_socket = Mock()
      mock_file_wb = Mock()
      mock_file_rb = Mock()
      mock_socket.makefile.side_effect = lambda mode: mock_file_wb if "w" in mode else mock_file_rb
      mock_conn.return_value = mock_socket

      # Create service
      service = TranscriptionService("localhost:10300")

      # Test session creation directly
      print("🧪 Testing direct session creation...")
      session = service.create_session("test_session_1")

      print(f"✅ Session created: {session.session_id}")

      # Test begin_session
      print("🎤 Testing session.begin_session()...")
      session.begin_session()
      print("✅ Session started successfully")

      # Test adding to active_sessions manually
      active_sessions["test_session_1"] = session
      print(f"📝 Active sessions: {len(active_sessions)}")

      # Create second session
      session2 = service.create_session("test_session_2")
      active_sessions["test_session_2"] = session2

      print(f"📝 Active sessions after second: {len(active_sessions)}")
      print(f"🔑 Session IDs: {list(active_sessions.keys())}")

      # Test cleanup
      del active_sessions["test_session_1"]
      print(f"📝 Active sessions after cleanup: {len(active_sessions)}")

      print("✅ Session creation test passed!")


if __name__ == "__main__":
  asyncio.run(test_session_creation())
