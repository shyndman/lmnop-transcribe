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
