import subprocess

from .config import Config


def send_notification(message):
  """Send a desktop notification."""
  if Config().use_desktop_notifications:
    try:
      subprocess.run(["notify-send", message], check=True)
    except FileNotFoundError:
      print("notify-send is not installed. Please install it to use desktop notifications.")
    except subprocess.CalledProcessError as e:
      print(f"Error sending notification: {e}")


def play_sound(filename):
  """Play a sound effect."""
  if filename == "start":
    filename = Config().feedback_sound_start
  elif filename == "stop":
    filename = Config().feedback_sound_stop
  if filename:
    try:
      subprocess.run(["pw-play", filename], check=True)
    except FileNotFoundError:
      try:
        subprocess.run(["paplay", filename], check=True)
      except FileNotFoundError:
        print("pw-play or paplay is not installed. Please install one to use sound effects.")
      except subprocess.CalledProcessError as e:
        print(f"Error playing sound with paplay: {e}")
    except subprocess.CalledProcessError as e:
      print(f"Error playing sound with pw-play: {e}")
