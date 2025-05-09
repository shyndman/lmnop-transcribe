import evdev
import evdev.ecodes
from loguru import logger

from .config import Config


async def wait_for_start_trigger(device: evdev.InputDevice, config: Config):
  """Awaits the configured start recording trigger."""
  trigger_type = config.start_trigger_type
  # trigger_param = config.start_trigger_param # Not used in this basic example yet

  logger.info(f"Awaiting start trigger: {trigger_type}")

  async for event in device.async_read_loop():
    logger.trace(
      "Received event: type={type}, code={code}, value={value}",
      type=event.type,
      code=event.code,
      value=event.value,
    )
    if event.type == evdev.ecodes.EV_KEY:
      logger.trace("is KEY event")
      if trigger_type == "caps_lock" and event.code == evdev.ecodes.KEY_CAPSLOCK and event.value == 1:
        logger.info("Start trigger detected (Caps Lock Down)")
        return  # Trigger detected, exit the await
      # Add other trigger types here based on config and trigger_param


async def wait_for_stop_or_cancel_trigger(device: evdev.InputDevice, config: Config) -> str:
  """Awaits either the stop or cancel recording trigger."""
  stop_trigger_type = config.stop_trigger_type
  cancel_trigger_code = evdev.ecodes.KEY_LEFTSHIFT  # Assuming Left Shift for cancel

  logger.info(f"Awaiting stop trigger ({stop_trigger_type}) or cancel trigger (Left Shift Down)")

  async for event in device.async_read_loop():
    logger.trace(
      "Received event: type={type}, code={code}, value={value}",
      type=event.type,
      code=event.code,
      value=event.value,
    )
    if event.type == evdev.ecodes.EV_KEY:
      logger.trace("is KEY event")
      # Check for stop trigger
      if stop_trigger_type == "caps_lock" and event.code == evdev.ecodes.KEY_CAPSLOCK and event.value == 0:
        logger.info("Stop trigger detected (Caps Lock Up)")
        return "stop"
      # Check for cancel trigger (Left Shift Down)
      if event.code == cancel_trigger_code and event.value == 1:
        logger.info("Cancel trigger detected (Left Shift Down)")
        return "cancel"
      # Add other trigger types here based on config and trigger_param

  # Should not be reached in normal operation, but added to satisfy type checker
  return "none"
