import asyncio  # Import asyncio
import subprocess

from .config import Config


async def send_notification(message):  # Make async
  """Send a desktop notification."""
  if Config().use_desktop_notifications:
    loop = asyncio.get_event_loop()
    try:
      # Run subprocess.run in a thread pool executor
      await loop.run_in_executor(None, lambda: subprocess.run(["notify-send", message], check=True))
    except FileNotFoundError:
      print("notify-send is not installed. Please install it to use desktop notifications.")
    except subprocess.CalledProcessError as e:
      print(f"Error sending notification: {e}")


async def play_sound(filename):  # Make async
  """Play a sound effect."""
  if filename == "start":
    filename = Config().feedback_sound_start
  elif filename == "stop":
    filename = Config().feedback_sound_stop
  if filename:
    loop = asyncio.get_event_loop()
    try:
      # Try pw-play first
      await loop.run_in_executor(None, lambda: subprocess.run(["pw-play", filename], check=True))
    except FileNotFoundError:
      try:
        # If pw-play not found, try paplay
        await loop.run_in_executor(None, lambda: subprocess.run(["paplay", filename], check=True))
      except FileNotFoundError:
        print("pw-play or paplay is not installed. Please install one to use sound effects.")
      except subprocess.CalledProcessError as e:
        print(f"Error playing sound with paplay: {e}")
    except subprocess.CalledProcessError as e:
      print(f"Error playing sound with pw-play: {e}")
