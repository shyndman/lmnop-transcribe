from lmnop_transcribe.config import Config


def test_config_loads():
  config = Config()
  assert config.filename == "output.wav"
  assert config.audio_device_name == "default"
  assert config.block_size == 4096
  assert config.channels == 1
  assert config.feedback_sound_start == ""
  assert config.feedback_sound_stop == ""
  assert config.keyboard_device_name == ""
  assert config.sample_rate == 44100
  assert config.trim_ms == 50
  assert config.use_desktop_notifications is True
  assert config.use_sox_silence is False
  assert config.whisper_model_name == "small"
  assert config.audio_sample_rate == 16000
