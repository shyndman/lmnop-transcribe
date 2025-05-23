#!/usr/bin/env python3
"""
Direct tests for the transcription service module without mocking.
These tests verify the actual file I/O and core functionality.
"""

import os
import tempfile
import wave
from unittest.mock import Mock, patch

import pytest


class TestTranscriptionServiceDirect:
  """Test TranscriptionService class without mocking core functionality."""

  def test_transcription_service_initialization(self):
    """Test TranscriptionService can be initialized without errors."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.transcription_service import TranscriptionService

      # Test with minimal parameters
      service = TranscriptionService("localhost:10300")
      assert service.wyoming_server_address == "localhost:10300"
      assert service.save_wav_files is False
      assert service.wav_output_path is None

      # Test with all parameters
      service = TranscriptionService(
        wyoming_server_address="test-server:8080",
        save_wav_files=True,
        wav_output_path="/tmp/test",
        rate=44100,
        sample_width=1,
        channels=2,
      )
      assert service.wyoming_server_address == "test-server:8080"
      assert service.save_wav_files is True
      assert service.wav_output_path == "/tmp/test"
      assert service.rate == 44100
      assert service.sample_width == 1
      assert service.channels == 2

  def test_transcription_service_session_creation(self):
    """Test that TranscriptionService creates sessions correctly."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.transcription_service import TranscriptionService

      with tempfile.TemporaryDirectory() as temp_dir:
        service = TranscriptionService(
          wyoming_server_address="localhost:10300",
          save_wav_files=True,
          wav_output_path=temp_dir,
        )

        session = service.create_session("test123")

        assert session.session_id == "test123"
        assert session.wyoming_server_address == "localhost:10300"
        assert session.save_wav is True
        assert session.wav_filepath == f"{temp_dir}/recording_test123.wav"

  def test_transcription_service_without_wav_saving(self):
    """Test TranscriptionService session creation when WAV saving is disabled."""
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
        save_wav_files=False,  # WAV saving disabled
      )

      session = service.create_session("test456")

      assert session.session_id == "test456"
      assert session.save_wav is False
      assert session.wav_filepath is None

  def test_transcription_service_specific_wav_file(self):
    """Test TranscriptionService with specific WAV file path."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.transcription_service import TranscriptionService

      specific_wav_file = "/tmp/my_custom_recording.wav"
      service = TranscriptionService(
        wyoming_server_address="localhost:10300",
        save_wav_files=True,
        wav_output_path=specific_wav_file,
      )

      session = service.create_session("test789")

      assert session.session_id == "test789"
      assert session.save_wav is True
      assert session.wav_filepath == specific_wav_file

  def test_streaming_session_wav_integration(self):
    """Test that StreamingTranscriptionSession saves WAV files correctly."""
    mock_wyoming_modules = {
      "wyoming": Mock(),
      "wyoming.asr": Mock(),
      "wyoming.audio": Mock(),
      "wyoming.event": Mock(),
    }

    with patch.dict("sys.modules", mock_wyoming_modules):
      from lmnop_transcribe.common import AudioChunk
      from lmnop_transcribe.transcription_service import StreamingTranscriptionSession

      with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        filepath = tmp_file.name

      try:
        # Create session with WAV saving but mock Wyoming connection
        session = StreamingTranscriptionSession(
          session_id="wav_test",
          wyoming_server_address="localhost:10300",
          save_wav=True,
          wav_filepath=filepath,
        )

        # Mock socket operations to avoid actual network calls
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
            mock_transcript.text = "Integration test transcript"
            mock_transcript_class.from_event.return_value = mock_transcript

            # Test the streaming session flow
            session.begin_session()

            # Add realistic audio chunks
            chunk1 = AudioChunk(data=b"\x00\x01\x02\x03" * 2000, timestamp_delta=100.0)  # 8KB
            chunk2 = AudioChunk(data=b"\x04\x05\x06\x07" * 2000, timestamp_delta=200.0)  # 8KB
            session.add_chunk(chunk1)
            session.add_chunk(chunk2)

            result = session.end_session()

            assert result == "Integration test transcript"
            assert os.path.exists(filepath)

            # Verify the actual WAV file was created correctly
            with wave.open(filepath, "rb") as wav_file:
              assert wav_file.getnchannels() == 1
              assert wav_file.getsampwidth() == 2
              assert wav_file.getframerate() == 44100

              # Verify audio data was written
              frames = wav_file.readframes(wav_file.getnframes())
              expected_size = len(chunk1.data) + len(chunk2.data)
              assert len(frames) == expected_size

      finally:
        if os.path.exists(filepath):
          os.unlink(filepath)


if __name__ == "__main__":
  pytest.main([__file__, "-v"])
