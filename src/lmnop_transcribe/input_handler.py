import evdev

from .config import Config


def get_keyboard_device():
  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  print("Available devices:")
  for device in devices:
    print(f"  - {device.path}: {device.name}")
  keyboard_device = None

  print("No keyboard device name specified, attempting to use first available keyboard.")
  if keyboard_device is None:
    for device in devices:
      if Config().keyboard_device_name and Config().keyboard_device_name in device.name.lower():
        keyboard_device = device
        break
      if "keyboard" in device.name.lower():
        keyboard_device = device
        break

  if keyboard_device is None:
    print("No keyboard device found.")
    return None

  print(f"Using keyboard device: {keyboard_device.name}")
  return keyboard_device
