from src.lmnop_transcribe.config import Config


def test_config_loads():
  config = Config()
  assert config.filename == "output.wav"
