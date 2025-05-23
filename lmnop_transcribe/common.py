# Configuration
from dataclasses import dataclass
from typing import TypedDict


# Event types (equivalent to TypeScript interfaces)
@dataclass
class KeyPressEvent:
  type: str = "keypress"
  key: str = ""
  timestamp_delta: float = 0.0  # milliseconds from session start


@dataclass
class ControlEvent:
  type: str  # 'play' | 'stop' | 'cancel'
  timestamp_delta: float  # milliseconds from session start


@dataclass
class AudioChunk:
  data: bytes
  timestamp_delta: float  # milliseconds from recording start


@dataclass
class TranscriptionResult:
  text: str
  timestamp_delta: float  # milliseconds from recording start


@dataclass
class CancelEvent:
  recording_id: float
  type: str = "cancel"


# Type definitions for state management
class RecordingState(TypedDict):
  is_recording: bool
  start_time_delta: float | None
  end_time_delta: float | None
  action: str | None


class ProcessedRecording(TypedDict):
  chunks: list[AudioChunk]
  recording_id: float
  start_time_delta: float
  end_time_delta: float
  action: str


@dataclass
class Config:
  save_wav_files: bool = False
  wav_output_path: str | None = None
  wyoming_server_address: str = "localhost:10300"
  trim_duration_ms: int = 500
  minimum_recording_ms: int = 2000
  start_trigger_type: str = "caps_lock"
  stop_trigger_type: str = "caps_lock"


@dataclass
class AudioConfig:
  """Configuration for audio streaming"""

  device: str = "default"  # "default" for default device
  channels: int = 1  # Mono recording
  samplerate: float = 16000  # Whisper uses 16kHz internally
  blocksize: int | None = None  # None for device default
  chunk_poll_interval_ms: int = 10  # How often to poll audio queue
  dtype: str = "int16"  # Data type for audio samples
