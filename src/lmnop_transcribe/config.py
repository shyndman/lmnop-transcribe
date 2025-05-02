import os

import toml


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
      print(f"Error: {e}")
      config = {}
    except toml.TomlDecodeError as e:
      print(f"Error decoding TOML file: {e}")
      config = {}

    self._audio_cleanup_command = config.get("audio_cleanup_command", "")
    self._audio_device_name = config.get("audio_device_name", "default")
    self._block_size = config.get("block_size", 4096)
    self._channels = config.get("channels", 1)
    self._feedback_sound_start = config.get("feedback_sound_start", "")
    self._feedback_sound_stop = config.get("feedback_sound_stop", "")
    self._filename = config.get("filename", "output.wav")
    self._keyboard_device_name = config.get("xkeyboard_device_name", "")
    self._notification_sound = config.get("notification_sound", "")
    self._sample_rate = config.get("sample_rate", 44100)
    self._trim_ms = config.get("trim_ms", 50)
    self._use_desktop_notifications = config.get("use_desktop_notifications", True)
    self._use_sox_silence = config.get("use_sox_silence", False)
    self._whisper_model_name = config.get("whisper_model_name", "small")
    self._audio_sample_rate = config.get("audio_sample_rate", 16000)

  @property
  def audio_cleanup_command(self) -> str:
    return self._audio_cleanup_command

  @audio_cleanup_command.setter
  def audio_cleanup_command(self, value: str):
    self._audio_cleanup_command = value

  @property
  def audio_device_name(self) -> str:
    return self._audio_device_name

  @audio_device_name.setter
  def audio_device_name(self, value: str):
    self._audio_device_name = value

  @property
  def block_size(self) -> int:
    return self._block_size

  @block_size.setter
  def block_size(self, value: int):
    self._block_size = value

  @property
  def channels(self) -> int:
    return self._channels

  @channels.setter
  def channels(self, value: int):
    self._channels = value

  @property
  def feedback_sound_start(self) -> str:
    return self._feedback_sound_start

  @feedback_sound_start.setter
  def feedback_sound_start(self, value: str):
    self._feedback_sound_start = value

  @property
  def feedback_sound_stop(self) -> str:
    return self._feedback_sound_stop

  @feedback_sound_stop.setter
  def feedback_sound_stop(self, value: str):
    self._feedback_sound_stop = value

  @property
  def filename(self) -> str:
    return self._filename

  @filename.setter
  def filename(self, value: str):
    self._filename = value

  @property
  def keyboard_device_name(self) -> str:
    return self._keyboard_device_name

  @keyboard_device_name.setter
  def keyboard_device_name(self, value: str):
    self._keyboard_device_name = value

  @property
  def notification_sound(self) -> str:
    return self._notification_sound

  @notification_sound.setter
  def notification_sound(self, value: str):
    self._notification_sound = value

  @property
  def sample_rate(self) -> int:
    return self._sample_rate

  @sample_rate.setter
  def sample_rate(self, value: int):
    self._sample_rate = value

  @property
  def trim_ms(self) -> int:
    return self._trim_ms

  @trim_ms.setter
  def trim_ms(self, value: int):
    self._trim_ms = value

  @property
  def use_desktop_notifications(self) -> bool:
    return self._use_desktop_notifications

  @use_desktop_notifications.setter
  def use_desktop_notifications(self, value: bool):
    self._use_desktop_notifications = value

  @property
  def use_sox_silence(self) -> bool:
    return self._use_sox_silence

  @use_sox_silence.setter
  def use_sox_silence(self, value: bool):
    self._use_sox_silence = value

  @property
  def whisper_model_name(self) -> str:
    return self._whisper_model_name

  @whisper_model_name.setter
  def whisper_model_name(self, value: str):
    self._whisper_model_name = value

  @property
  def audio_sample_rate(self) -> int:
    return self._audio_sample_rate

  @audio_sample_rate.setter
  def audio_sample_rate(self, value: int):
    self._audio_sample_rate = value
