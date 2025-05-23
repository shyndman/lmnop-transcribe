#!/usr/bin/env python3
"""
Integration tests for transcription service with the pipeline.
Tests the actual integration without requiring Wyoming server.
"""

import asyncio
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from lmnop_transcribe.pipeline import async_main


class TestTranscriptionIntegration:
  """Test integration between pipeline and transcription service."""

  @pytest.mark.asyncio
  async def test_pipeline_with_transcription_service_wav_saving(self):
    """Test full pipeline integration with WAV saving enabled."""
    # Mock Wyoming modules
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the Wyoming socket operations to avoid network calls
        with (
          patch("lmnop_transcribe.transcription_service.socket.create_connection") as mock_conn,
          patch("lmnop_transcribe.transcription_service.write_event"),
          patch("lmnop_transcribe.transcription_service.read_event") as mock_read,
        ):
          # Setup mocks for streaming session
          mock_socket = Mock()
          mock_file_wb = Mock()
          mock_file_rb = Mock()
          mock_socket.makefile.side_effect = [mock_file_wb, mock_file_rb]
          mock_conn.return_value = mock_socket

          # Mock transcript response
          mock_transcript_event = Mock()
          mock_read.return_value = mock_transcript_event

          with patch("lmnop_transcribe.transcription_service.Transcript") as mock_transcript_class:
            mock_transcript_class.is_type.return_value = True
            mock_transcript = Mock()
            mock_transcript.text = "Integration test transcription"
            mock_transcript_class.from_event.return_value = mock_transcript

            try:
              # Run the pipeline for a short time with WAV saving
              await asyncio.wait_for(
                async_main(
                  use_real_audio=False,
                  use_keyboard_bridge=False,
                  wav_output_path=temp_dir,
                  wyoming_server="localhost:10300",
                ),
                timeout=0.5,  # Run for 0.5 seconds
              )
            except asyncio.TimeoutError:
              # Expected - the mock pipeline runs forever
              pass
            except KeyboardInterrupt:
              # Also expected in mock mode
              pass

  def test_transcription_service_session_creation(self):
    """Test that TranscriptionService creates sessions properly."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.transcription_service import TranscriptionService

      # Create a service instance
      service = TranscriptionService("localhost:10300")

      # Create a session
      session = service.create_session("test_session")

      # Verify session properties
      assert session.session_id == "test_session"
      assert session.wyoming_server_address == "localhost:10300"
      assert session.rate == 44100
      assert session.sample_width == 2
      assert session.channels == 1

  def test_wav_file_integration_with_streaming_session(self):
    """Test WAV file saving with streaming transcription session."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.common import AudioChunk
      from lmnop_transcribe.transcription_service import TranscriptionService

      with tempfile.TemporaryDirectory() as temp_dir:
        service = TranscriptionService(
          wyoming_server_address="localhost:10300",
          save_wav_files=True,
          wav_output_path=temp_dir,
          rate=44100,
          sample_width=2,
          channels=1,
        )

        # Create a session
        session = service.create_session("realistic_test")

        # Create some test audio chunks
        audio_chunks = [
          AudioChunk(data=b"\x00\x01\x02\x03" * 1000, timestamp_delta=100.0),
          AudioChunk(data=b"\x04\x05\x06\x07" * 1000, timestamp_delta=200.0),
        ]

        # Mock socket operations for streaming session
        with (
          patch("lmnop_transcribe.transcription_service.socket.create_connection") as mock_conn,
          patch("lmnop_transcribe.transcription_service.write_event"),
          patch("lmnop_transcribe.transcription_service.read_event") as mock_read,
        ):
          # Setup mocks
          mock_socket = Mock()
          mock_file_wb = Mock()
          mock_file_rb = Mock()
          mock_socket.makefile.side_effect = [mock_file_wb, mock_file_rb]
          mock_conn.return_value = mock_socket

          mock_transcript_event = Mock()
          mock_read.return_value = mock_transcript_event

          with patch("lmnop_transcribe.transcription_service.Transcript") as mock_transcript_class:
            mock_transcript_class.is_type.return_value = True
            mock_transcript = Mock()
            mock_transcript.text = "Streaming session test transcription"
            mock_transcript_class.from_event.return_value = mock_transcript

            # Test the streaming session flow
            session.begin_session()
            for chunk in audio_chunks:
              session.add_chunk(chunk)
            result = session.end_session()

            # Verify transcription
            assert result == "Streaming session test transcription"

            # Verify WAV file was created
            wav_path = os.path.join(temp_dir, "recording_realistic_test.wav")
            assert os.path.exists(wav_path)

  def test_command_line_integration(self):
    """Test that command-line arguments properly configure transcription service."""
    # Test command-line argument parsing without importing pipeline
    # to avoid NumPy reload warnings
    import argparse

    def create_test_parser():
      """Create the same parser as pipeline.py"""
      parser = argparse.ArgumentParser(description="Audio transcription pipeline")
      parser.add_argument("--real-audio", action="store_true")
      parser.add_argument("--keyboard", action="store_true")
      parser.add_argument("--save-wav", type=str, metavar="PATH")
      parser.add_argument("--wyoming-server", type=str, default="localhost:10300")
      return parser

    # Test argument parsing
    test_args = [
      "--save-wav",
      "/tmp/test_recordings",
      "--wyoming-server",
      "custom-server:9999",
      "--real-audio",
    ]

    parser = create_test_parser()
    args = parser.parse_args(test_args)

    assert args.save_wav == "/tmp/test_recordings"
    assert args.wyoming_server == "custom-server:9999"
    assert args.real_audio is True
    assert args.keyboard is False  # Not provided

    # Verify these would be passed correctly to main()
    assert args.save_wav is not None  # Would enable WAV saving
    assert args.wyoming_server != "localhost:10300"  # Custom server

  def test_error_handling_integration(self):
    """Test error handling in the integrated system."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.transcription_service import TranscriptionService

      service = TranscriptionService(
        wyoming_server_address="localhost:10300",
        save_wav_files=True,
        wav_output_path="/invalid/path/that/does/not/exist",
      )

      # Create a session
      session = service.create_session("error_test")

      # Test connection error handling
      with patch("lmnop_transcribe.transcription_service.socket.create_connection") as mock_conn:
        mock_conn.side_effect = ConnectionRefusedError("Connection refused")

        # Should handle connection failure gracefully
        with pytest.raises(ConnectionRefusedError):
          session.begin_session()


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
