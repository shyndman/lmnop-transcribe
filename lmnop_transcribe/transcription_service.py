#!/usr/bin/env python3
"""
Transcription service using Wyoming ASR protocol.
Handles streaming audio transcription via TCP socket connection to Wyoming server.
"""

import io
import logging
import socket
import wave

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk as WyomingAudioChunk
from wyoming.audio import AudioStart, AudioStop
from wyoming.event import read_event, write_event

from .common import AudioChunk

logger = logging.getLogger(__name__)


class StreamingTranscriptionSession:
  """
  Manages a single streaming transcription session with Wyoming server.
  Handles the full Wyoming protocol flow: Transcribe -> AudioStart -> AudioChunks -> AudioStop -> Transcript
  """

  def __init__(
    self,
    session_id: str,
    wyoming_server_address: str,
    rate: int = 16000,
    sample_width: int = 2,
    channels: int = 1,
    save_wav: bool = False,
    wav_filepath: str | None = None,
  ):
    self.session_id = session_id
    self.wyoming_server_address = wyoming_server_address
    self.rate = rate
    self.sample_width = sample_width
    self.channels = channels
    self.save_wav = save_wav
    self.wav_filepath = wav_filepath

    self._socket: socket.socket | None = None
    self._write_io: io.BufferedWriter | None = None
    self._read_io: io.BufferedReader | None = None
    self._wav_buffer: list[bytes] = []
    self._session_started = False

    logger.info(f"Created transcription session {session_id}")

  def begin_session(self) -> None:
    """Begin the transcription session - connect to Wyoming and send initial events"""
    if self._session_started:
      logger.warning(f"Session {self.session_id} already started")
      return

    try:
      host, port = self.wyoming_server_address.split(":")
      port = int(port)

      logger.info(f"Connecting to Wyoming server at {host}:{port} for session {self.session_id}")
      self._socket = socket.create_connection((host, port))
      self._write_io = self._socket.makefile("wb")
      self._read_io = self._socket.makefile("rb")

      # Send Transcribe event
      write_event(Transcribe().event(), self._write_io)
      logger.debug(f"Session {self.session_id}: Sent Transcribe event")

      # Send AudioStart event
      write_event(
        AudioStart(rate=self.rate, width=self.sample_width, channels=self.channels).event(), self._write_io
      )
      logger.debug(
        f"Session {self.session_id}: Sent AudioStart event (rate={self.rate}, "
        f"width={self.sample_width}, channels={self.channels})"
      )

      self._session_started = True

    except Exception:
      logger.exception(f"Failed to begin transcription session {self.session_id}")
      self._cleanup()
      raise

  def add_chunk(self, chunk: AudioChunk) -> None:
    """Add an audio chunk to the transcription session"""
    if not self._session_started or not self._write_io:
      logger.error(f"Session {self.session_id} not started, cannot add chunk")
      return

    try:
      # Send audio chunk to Wyoming
      write_event(
        WyomingAudioChunk(
          rate=self.rate, width=self.sample_width, channels=self.channels, audio=chunk.data
        ).event(),
        self._write_io,
      )

      # Buffer for WAV file if needed
      if self.save_wav:
        self._wav_buffer.append(chunk.data)

      logger.debug(
        f"Session {self.session_id}: Added chunk {len(chunk.data)} bytes at {chunk.timestamp_delta:.0f}ms"
      )

    except Exception:
      logger.exception(f"Error adding chunk to session {self.session_id}")
      raise

  def end_session(self) -> str | None:
    """End the transcription session and get the transcript"""
    if not self._session_started:
      logger.warning(f"Session {self.session_id} not started, cannot end")
      return None

    try:
      # Send AudioStop event
      if self._write_io:
        write_event(AudioStop().event(), self._write_io)
        logger.debug(f"Session {self.session_id}: Sent AudioStop event")

      # Save WAV file if requested
      if self.save_wav and self.wav_filepath and self._wav_buffer:
        self._save_wav_file()

      # Read transcript response
      transcript = None
      if self._read_io:
        transcript_event = read_event(self._read_io)
        if transcript_event and Transcript.is_type(transcript_event.type):
          transcript_obj = Transcript.from_event(transcript_event)
          transcript = transcript_obj.text.strip()
          logger.info(f"Session {self.session_id}: Received transcript: '{transcript}'")
        else:
          logger.warning(
            f"Session {self.session_id}: Unexpected event from Wyoming server: {transcript_event}"
          )

      return transcript

    except Exception:
      logger.exception(f"Error ending transcription session {self.session_id}")
      return None
    finally:
      self._cleanup()

  def cancel_session(self) -> None:
    """Cancel the transcription session without getting transcript"""
    logger.info(f"Cancelling transcription session {self.session_id}")
    self._cleanup()

  def _save_wav_file(self) -> None:
    """Save buffered audio chunks to WAV file"""
    if not self.wav_filepath or not self._wav_buffer:
      return

    try:
      with wave.open(self.wav_filepath, "wb") as wav_file:
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(self.sample_width)
        wav_file.setframerate(self.rate)

        for chunk in self._wav_buffer:
          wav_file.writeframes(chunk)

      total_bytes = sum(len(chunk) for chunk in self._wav_buffer)
      logger.info(
        f"Session {self.session_id}: Saved {len(self._wav_buffer)} chunks ({total_bytes} bytes) "
        f"to {self.wav_filepath}"
      )

    except Exception:
      logger.exception(f"Error saving WAV file for session {self.session_id}")

  def _cleanup(self) -> None:
    """Clean up socket and file resources"""
    if self._write_io:
      try:
        self._write_io.close()
      except Exception:
        pass
      self._write_io = None

    if self._read_io:
      try:
        self._read_io.close()
      except Exception:
        pass
      self._read_io = None

    if self._socket:
      try:
        self._socket.close()
      except Exception:
        pass
      self._socket = None

    self._session_started = False
    logger.debug(f"Session {self.session_id}: Cleaned up resources")


class TranscriptionService:
  """Service for managing streaming transcription sessions with Wyoming ASR protocol"""

  def __init__(
    self,
    wyoming_server_address: str,
    rate: int = 44100,
    sample_width: int = 2,
    channels: int = 1,
    save_wav_files: bool = False,
    wav_output_path: str | None = None,
  ):
    self.wyoming_server_address = wyoming_server_address
    self.rate = rate
    self.sample_width = sample_width
    self.channels = channels
    self.save_wav_files = save_wav_files
    self.wav_output_path = wav_output_path

    logger.info(f"TranscriptionService initialized for {wyoming_server_address}")

  def create_session(self, session_id: str) -> StreamingTranscriptionSession:
    """Create a new streaming transcription session"""
    wav_filepath = None
    if self.save_wav_files and self.wav_output_path:
      if self.wav_output_path.endswith(".wav"):
        wav_filepath = self.wav_output_path
      else:
        wav_filepath = f"{self.wav_output_path}/recording_{session_id}.wav"

    return StreamingTranscriptionSession(
      session_id=session_id,
      wyoming_server_address=self.wyoming_server_address,
      rate=self.rate,
      sample_width=self.sample_width,
      channels=self.channels,
      save_wav=self.save_wav_files,
      wav_filepath=wav_filepath,
    )
