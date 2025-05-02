import subprocess

from loguru import logger

from .config import Config


def cleanup_audio(filename):
  """Clean up the audio file using sox."""
  if Config().use_sox_silence:
    logger.info("Cleaning audio using sox silence...")
    try:
      # Trim silence from the beginning and end of the audio
      subprocess.run(
        [
          "sox",
          filename,
          filename,
          "silence",
          "1",
          "0.1",
          "0%",
          "1",
          "0.1",
          "0%",
        ],
        check=True,
      )
    except subprocess.CalledProcessError as e:
      logger.error(f"Error cleaning audio with sox: {e}")

  if Config().trim_ms > 0:
    logger.info(f"Trimming {Config().trim_ms}ms from start and end...")
    try:
      # Get the audio duration in seconds
      duration = float(subprocess.check_output(["soxi", "-D", filename]).decode("utf-8").strip())
      trim_seconds = Config().trim_ms / 1000
      if duration > 2 * trim_seconds:
        # Trim the audio using sox
        subprocess.run(
          [
            "sox",
            filename,
            filename,
            "trim",
            str(trim_seconds),
            str(duration - 2 * trim_seconds),
          ],
          check=True,
        )
      else:
        logger.warning("Audio duration is too short to trim.")
    except subprocess.CalledProcessError as e:
      logger.error(f"Error trimming audio with sox: {e}")
    except FileNotFoundError:
      logger.error("sox is not installed. Please install sox to use audio cleanup features.")
  logger.info("Audio cleanup complete.")
