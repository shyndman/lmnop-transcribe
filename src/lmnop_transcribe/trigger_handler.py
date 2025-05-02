import evdev
import evdev.ecodes

from .config import Config


async def wait_for_start_trigger(device: evdev.InputDevice, config: Config):
  """Awaits the configured start recording trigger."""
  trigger_type = config.start_trigger_type
  # trigger_param = config.start_trigger_param # Not used in this basic example yet

  print(f"Awaiting start trigger: {trigger_type}")

  async for event in device.async_read_loop():
    if event.type == evdev.ecodes.EV_KEY:
      if trigger_type == "caps_lock" and event.code == evdev.ecodes.KEY_CAPSLOCK and event.value == 1:
        print("Start trigger detected (Caps Lock Down)")
        return  # Trigger detected, exit the await
      # Add other trigger types here based on config and trigger_param


async def wait_for_stop_trigger(device: evdev.InputDevice, config: Config):
  """Awaits the configured stop recording trigger."""
  trigger_type = config.stop_trigger_type
  # trigger_param = config.stop_trigger_param # Not used in this basic example yet

  print(f"Awaiting stop trigger: {trigger_type}")

  async for event in device.async_read_loop():
    if event.type == evdev.ecodes.EV_KEY:
      if trigger_type == "caps_lock" and event.code == evdev.ecodes.KEY_CAPSLOCK and event.value == 0:
        print("Stop trigger detected (Caps Lock Up)")
        return  # Trigger detected, exit the await
      # Add other trigger types here based on config and trigger_param
