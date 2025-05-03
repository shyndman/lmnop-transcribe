import asyncio  # Import asyncio
import subprocess

from loguru import logger

from .config import Config


async def send_notification(message):  # Make async
  """Send a desktop notification."""
  if Config().use_desktop_notifications:
    loop = asyncio.get_event_loop()
    try:
      # Run subprocess.run in a thread pool executor
      await loop.run_in_executor(None, lambda: subprocess.run(["notify-send", message], check=True))
    except FileNotFoundError:
      logger.error("notify-send is not installed. Please install it to use desktop notifications.")
    except subprocess.CalledProcessError as e:
      logger.error(f"Error sending notification: {e}")


async def play_sound(role):
  """Play a sound effect."""
  filename = None
  if role == "start":
    filename = Config().feedback_sound_start
  elif role == "stop":
    filename = Config().feedback_sound_stop

  if filename:
    loop = asyncio.get_event_loop()
    try:
      await loop.run_in_executor(
        None, lambda: subprocess.run(["pw-play", "--volume", "0.6", filename], check=True)
      )
    except subprocess.CalledProcessError:
      logger.exception("Error playing sound with pw-play")
