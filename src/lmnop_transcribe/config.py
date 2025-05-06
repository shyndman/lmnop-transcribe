import os

import toml
from loguru import logger


class Config:
  _instance = None

  def __new__(cls, config_path: str = "config.toml"):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.load_config(config_path)
    return cls._instance

  def load_config(self, config_path: str):
    try:
      if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
      config = toml.load(config_path)
    except FileNotFoundError as e:
      logger.error(f"Error: {e}")
      config = {}
    except toml.TomlDecodeError as e:
      logger.error(f"Error decoding TOML file: {e}")
      config = {}

    self._audio_device_name = config.get("audio_device_name", "default")
    self._channels = config.get("channels", 1)
    self._sample_rate = config.get("sample_rate", 44100)
    self._wyoming_server_address = config.get("wyoming_server_address", "localhost:8080")
    self._filename = config.get("filename", "output.wav")
    self._block_size = config.get("block_size", 4096)
    self._min_recording_duration_ms = config.get("min_recording_duration_ms", 750)
    self._trim_duration_seconds = config.get("trim_duration_seconds", 0.5)
    self._keyboard_device_name = config.get("keyboard_device_name", "")
    self._start_trigger_type = config.get("trigger", {}).get("start_trigger_type", "caps_lock")
    self._start_trigger_param = config.get("trigger", {}).get("start_trigger_param", "")
    self._stop_trigger_type = config.get("trigger", {}).get("stop_trigger_type", "caps_lock")
    self._stop_trigger_param = config.get("trigger", {}).get("stop_trigger_param", "")
    self._use_desktop_notifications = config.get("use_desktop_notifications", True)
    self._whisper_model_name = config.get("whisper_model_name", "small")
    self._audio_sample_rate = config.get("audio_sample_rate", 16000)
    self._log_level = config.get("log_level", "INFO")

  @property
  def audio_device_name(self) -> str:
    """Returns the name of the audio device."""
    return self._audio_device_name

  @property
  def channels(self) -> int:
    """Returns the number of audio channels."""
    return self._channels

  @property
  def sample_rate(self) -> int:
    """Returns the sample rate of the audio."""
    return self._sample_rate

  @property
  def wyoming_server_address(self) -> str:
    """Returns the address of the Wyoming STT server."""
    return self._wyoming_server_address

  @property
  def filename(self) -> str:
    """Returns the filename to save the recorded audio to."""
    return self._filename

  @property
  def block_size(self) -> int:
    """Returns the block size to use when recording audio."""
    return self._block_size

  @property
  def min_recording_duration_ms(self) -> int:
    """Returns the minimum recording duration in milliseconds."""
    return self._min_recording_duration_ms

  @property
  def trim_duration_seconds(self) -> float:
    """Returns the duration to trim from the beginning of the recording in seconds."""
    return self._trim_duration_seconds

  @property
  def keyboard_device_name(self) -> str:
    """Returns the name of the keyboard device to use."""
    return self._keyboard_device_name

  @property
  def start_trigger_type(self) -> str:
    """Returns the type of trigger to start recording."""
    return self._start_trigger_type

  @property
  def start_trigger_param(self) -> str:
    """Returns the parameter for the start recording trigger (e.g., key code)."""
    return self._start_trigger_param

  @property
  def stop_trigger_type(self) -> str:
    """Returns the type of trigger to stop recording."""
    return self._stop_trigger_type

  @property
  def stop_trigger_param(self) -> str:
    """Returns the parameter for the stop recording trigger (e.g., key code)."""
    return self._stop_trigger_param

  @property
  def use_desktop_notifications(self) -> bool:
    """Returns whether to use desktop notifications to alert the user when transcription is complete."""
    return self._use_desktop_notifications

  @property
  def whisper_model_name(self) -> str:
    """Returns the name of the whisper model to use."""
    return self._whisper_model_name

  @property
  def audio_sample_rate(self) -> int:
    """Returns the audio sample rate."""
    return self._audio_sample_rate

  @property
  def log_level(self) -> str:
    """Returns the configured log level."""
    return self._log_level
