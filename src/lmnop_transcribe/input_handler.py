import evdev
from loguru import logger

from .config import Config


def get_keyboard_device():
  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  logger.info("Available devices:")
  for device in devices:
    logger.info(f"  - {device.path}: {device.name}")
  keyboard_device = None

  logger.info("No keyboard device name specified, attempting to use first available keyboard.")
  keyboard_name = Config().keyboard_device_name
  if keyboard_device is None:
    for device in devices:
      if keyboard_name and keyboard_name in device.name.lower():
        keyboard_device = device
        break
      if "keyboard" in device.name.lower():
        keyboard_device = device
        break

  if keyboard_device is None:
    logger.error("No keyboard device found.")
    return None

  logger.info(f"Using keyboard device: {keyboard_device.name}")
  return keyboard_device
