#!/usr/bin/env python3
"""
Tests for the transcription service module.
"""

import os
import tempfile
import wave
from unittest.mock import Mock, patch

import pytest


# Mock Wyoming modules before importing transcription_service
def setup_wyoming_mocks():
  """Set up mocks for Wyoming dependencies."""
  mock_modules = {
    "wyoming": Mock(),
    "wyoming.asr": Mock(),
    "wyoming.audio": Mock(),
    "wyoming.event": Mock(),
  }

  # Create mock classes
  mock_transcribe = Mock()
  mock_transcript = Mock()
  mock_audio_chunk = Mock()
  mock_audio_start = Mock()
  mock_audio_stop = Mock()

  mock_modules["wyoming.asr"].Transcribe = mock_transcribe
  mock_modules["wyoming.asr"].Transcript = mock_transcript
  mock_modules["wyoming.audio"].AudioChunk = mock_audio_chunk
  mock_modules["wyoming.audio"].AudioStart = mock_audio_start
  mock_modules["wyoming.audio"].AudioStop = mock_audio_stop
  mock_modules["wyoming.event"].read_event = Mock()
  mock_modules["wyoming.event"].write_event = Mock()

  return mock_modules


class TestStreamingTranscriptionSession:
  """Test StreamingTranscriptionSession functionality."""

  @patch("lmnop_transcribe.transcription_service.socket.create_connection")
  def test_successful_session_flow(self, mock_create_connection):
    """Test successful transcription session with Wyoming server."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.common import AudioChunk
      from lmnop_transcribe.transcription_service import StreamingTranscriptionSession

      # Mock socket and file objects
      mock_socket = Mock()
      mock_file_wb = Mock()
      mock_file_rb = Mock()
      mock_socket.makefile.side_effect = [mock_file_wb, mock_file_rb]
      mock_create_connection.return_value = mock_socket

      # Mock successful transcript response
      mock_transcript_event = Mock()
      mock_transcript_event.type = "transcript"

      with (
        patch("lmnop_transcribe.transcription_service.read_event") as mock_read_event,
        patch("lmnop_transcribe.transcription_service.write_event") as mock_write_event,
      ):
        mock_read_event.return_value = mock_transcript_event

        # Mock Transcript class
        mock_transcript_class = Mock()
        mock_transcript_class.is_type.return_value = True
        mock_transcript = Mock()
        mock_transcript.text = "  Hello world  "
        mock_transcript_class.from_event.return_value = mock_transcript

        with patch("lmnop_transcribe.transcription_service.Transcript", mock_transcript_class):
          # Create session
          session = StreamingTranscriptionSession(
            session_id="test123",
            wyoming_server_address="localhost:10300",
            rate=44100,
            sample_width=2,
            channels=1,
          )

          # Test session flow
          session.begin_session()

          # Add some chunks
          chunk1 = AudioChunk(data=b"audio_data_1", timestamp_delta=100.0)
          chunk2 = AudioChunk(data=b"audio_data_2", timestamp_delta=200.0)
          session.add_chunk(chunk1)
          session.add_chunk(chunk2)

          # End session and get transcript
          result = session.end_session()

          assert result == "Hello world"
          mock_create_connection.assert_called_once_with(("localhost", 10300))
          # Should have: Transcribe, AudioStart, 2 AudioChunks, AudioStop
          assert mock_write_event.call_count == 5

  @patch("lmnop_transcribe.transcription_service.socket.create_connection")
  def test_session_connection_error(self, mock_create_connection):
    """Test handling of connection error during session begin."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import StreamingTranscriptionSession

      mock_create_connection.side_effect = ConnectionRefusedError("Connection refused")

      session = StreamingTranscriptionSession(session_id="test123", wyoming_server_address="localhost:10300")

      with pytest.raises(ConnectionRefusedError):
        session.begin_session()

  def test_session_wav_file_saving(self):
    """Test that session saves WAV file when requested."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.common import AudioChunk
      from lmnop_transcribe.transcription_service import StreamingTranscriptionSession

      with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        filepath = tmp_file.name

      try:
        # Mock socket operations
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
            mock_transcript.text = "Test transcript"
            mock_transcript_class.from_event.return_value = mock_transcript

            # Create session with WAV saving
            session = StreamingTranscriptionSession(
              session_id="test123",
              wyoming_server_address="localhost:10300",
              save_wav=True,
              wav_filepath=filepath,
            )

            session.begin_session()

            # Add audio chunks
            chunk1 = AudioChunk(data=b"\x00\x01\x02\x03" * 100, timestamp_delta=100.0)
            chunk2 = AudioChunk(data=b"\x04\x05\x06\x07" * 100, timestamp_delta=200.0)
            session.add_chunk(chunk1)
            session.add_chunk(chunk2)

            result = session.end_session()

            assert result == "Test transcript"
            assert os.path.exists(filepath)

            # Verify WAV file
            with wave.open(filepath, "rb") as wav_file:
              assert wav_file.getnchannels() == 1
              assert wav_file.getsampwidth() == 2
              assert wav_file.getframerate() == 16000  # Updated to match Whisper's sample rate

      finally:
        if os.path.exists(filepath):
          os.unlink(filepath)

  def test_session_cancel(self):
    """Test session cancellation."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import StreamingTranscriptionSession

      with patch("lmnop_transcribe.transcription_service.socket.create_connection") as mock_conn:
        mock_socket = Mock()
        mock_file_wb = Mock()
        mock_file_rb = Mock()
        mock_socket.makefile.side_effect = [mock_file_wb, mock_file_rb]
        mock_conn.return_value = mock_socket

        session = StreamingTranscriptionSession(
          session_id="test123", wyoming_server_address="localhost:10300"
        )

        with patch("lmnop_transcribe.transcription_service.write_event"):
          session.begin_session()
          session.cancel_session()

          # Verify cleanup was called
          mock_file_wb.close.assert_called_once()
          mock_file_rb.close.assert_called_once()
          mock_socket.close.assert_called_once()


class TestTranscriptionService:
  """Test the TranscriptionService class."""

  def test_init_with_defaults(self):
    """Test TranscriptionService initialization with default values."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import TranscriptionService

      service = TranscriptionService("localhost:10300")

      assert service.wyoming_server_address == "localhost:10300"
      assert service.save_wav_files is False
      assert service.wav_output_path is None
      assert service.rate == 44100
      assert service.sample_width == 2
      assert service.channels == 1

  def test_init_with_custom_values(self):
    """Test TranscriptionService initialization with custom values."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import TranscriptionService

      service = TranscriptionService(
        wyoming_server_address="custom:8080",
        save_wav_files=True,
        wav_output_path="/tmp/recordings",
        rate=44100,
        sample_width=1,
        channels=2,
      )

      assert service.wyoming_server_address == "custom:8080"
      assert service.save_wav_files is True
      assert service.wav_output_path == "/tmp/recordings"
      assert service.rate == 44100
      assert service.sample_width == 1
      assert service.channels == 2

  def test_create_session_without_wav_saving(self):
    """Test creating transcription session without WAV file saving."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import TranscriptionService

      service = TranscriptionService("localhost:10300", save_wav_files=False)
      session = service.create_session("test123")

      assert session.session_id == "test123"
      assert session.wyoming_server_address == "localhost:10300"
      assert session.rate == 44100
      assert session.sample_width == 2
      assert session.channels == 1
      assert session.save_wav is False
      assert session.wav_filepath is None

  def test_create_session_with_wav_saving(self):
    """Test creating transcription session with WAV file saving."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import TranscriptionService

      with tempfile.TemporaryDirectory() as temp_dir:
        service = TranscriptionService("localhost:10300", save_wav_files=True, wav_output_path=temp_dir)
        session = service.create_session("test123")

        assert session.session_id == "test123"
        assert session.save_wav is True
        assert session.wav_filepath == f"{temp_dir}/recording_test123.wav"

  def test_create_session_with_specific_wav_file(self):
    """Test creating session with specific WAV file path."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import TranscriptionService

      specific_file = "/tmp/custom_recording.wav"
      service = TranscriptionService("localhost:10300", save_wav_files=True, wav_output_path=specific_file)
      session = service.create_session("test123")

      assert session.wav_filepath == specific_file

  def test_create_multiple_sessions(self):
    """Test creating multiple transcription sessions."""
    with patch.dict("sys.modules", setup_wyoming_mocks()):
      from lmnop_transcribe.transcription_service import TranscriptionService

      service = TranscriptionService("localhost:10300")

      session1 = service.create_session("session1")
      session2 = service.create_session("session2")

      assert session1.session_id == "session1"
      assert session2.session_id == "session2"
      assert session1 is not session2  # Different instances


if __name__ == "__main__":
  pytest.main([__file__])
