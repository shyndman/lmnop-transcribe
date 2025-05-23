#!/usr/bin/env python3
"""
Keyboard event bridge for evdev integration with RxPY pipeline.
Converts evdev keyboard events to RxPY observable stream.
"""

import asyncio
import time

import evdev
import evdev.ecodes
from loguru import logger
from reactivex.subject import Subject

from .common import Config, KeyPressEvent


class EvdevKeyboardBridge:
  """Bridge between evdev keyboard events and RxPY observables."""

  def __init__(self, device: evdev.InputDevice, config):
    self.device = device
    self.config = config
    self.subject = Subject()
    self.session_start_time: float | None = None
    self.running = False
    self.task: asyncio.Task | None = None

  async def start_monitoring(self):
    """Start the keyboard monitoring loop"""
    if self.running:
      logger.warning("Keyboard monitoring already running")
      return

    self.running = True
    self.session_start_time = time.time() * 1000

    logger.info("Starting keyboard monitoring")
    logger.info(f"Device: {self.device.path} ({self.device.name})")
    logger.info(f"Start trigger: {self.config.start_trigger_type}")
    logger.info(f"Stop trigger: {self.config.stop_trigger_type}")

    self.task = asyncio.create_task(self._event_loop())

  async def _event_loop(self):
    """Main event monitoring loop"""
    try:
      async for event in self.device.async_read_loop():
        if not self.running:
          break

        # logger.trace(
        #   "Received event: type={type}, code={code}, value={value}",
        #   type=event.type,
        #   code=event.code,
        #   value=event.value,
        # )

        if event.type == evdev.ecodes.EV_KEY:
          # logger.trace("is KEY event")
          key_event = self._map_evdev_to_key_event(event)
          if key_event:
            logger.debug(f"Emitting key event: {key_event.key} at {key_event.timestamp_delta}ms")
            self.subject.on_next(key_event)

    except Exception as e:
      logger.exception("Error in keyboard event loop")
      self.subject.on_error(e)

  def stop_monitoring(self):
    """Stop the monitoring loop"""
    if not self.running:
      return

    logger.info("Stopping keyboard monitoring")
    self.running = False

    if self.task:
      self.task.cancel()
      self.task = None

    self.subject.on_completed()

  @property
  def observable(self):
    """Get the observable stream of keyboard events"""
    return self.subject

  def _map_evdev_to_key_event(self, event: evdev.InputEvent) -> KeyPressEvent | None:
    """Map evdev events to our KeyPressEvent format"""
    if self.session_start_time is None:
      return None

    current_time = time.time() * 1000
    timestamp_delta = current_time - self.session_start_time

    # Map start trigger
    if (
      self.config.start_trigger_type == "caps_lock"
      and event.code == evdev.ecodes.KEY_CAPSLOCK
      and event.value == 1
    ):
      logger.info("Start trigger detected (Caps Lock Down)")
      return KeyPressEvent(key="play_key", timestamp_delta=timestamp_delta)

    # Map stop trigger
    elif (
      self.config.stop_trigger_type == "caps_lock"
      and event.code == evdev.ecodes.KEY_CAPSLOCK
      and event.value == 0
    ):
      logger.info("Stop trigger detected (Caps Lock Up)")
      return KeyPressEvent(key="stop_key", timestamp_delta=timestamp_delta)

    # Map cancel trigger (Left Shift Down)
    elif event.code == evdev.ecodes.KEY_LEFTSHIFT and event.value == 1:
      logger.info("Cancel trigger detected (Left Shift Down)")
      return KeyPressEvent(key="cancel_key", timestamp_delta=timestamp_delta)

    # Add other trigger types here based on config
    # TODO: Extend this for other trigger_types and trigger_params

    # Return None for events we don't care about
    return None

  def __enter__(self):
    """Context manager entry"""
    return self

  async def __aenter__(self):
    """Async context manager entry"""
    await self.start_monitoring()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit"""
    self.stop_monitoring()

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Async context manager exit"""
    self.stop_monitoring()


def create_keyboard_bridge(device_path: str, config: Config) -> EvdevKeyboardBridge:
  """
  Convenience function to create a keyboard bridge.

  Args:
      device_path: Path to the input device (e.g., '/dev/input/event0')
      config: Configuration object with trigger settings

  Returns:
      EvdevKeyboardBridge instance

  Raises:
      OSError: If device cannot be opened
      PermissionError: If insufficient permissions to access device
  """
  try:
    device = evdev.InputDevice(device_path)
    logger.info(f"Opened device: {device.name} at {device_path}")
    return EvdevKeyboardBridge(device, config)
  except PermissionError:
    logger.error(f"Permission denied accessing {device_path}. Run as root or add user to input group.")
    raise
  except FileNotFoundError:
    logger.error(f"Device not found: {device_path}")
    raise
  except Exception:
    logger.exception(f"Failed to open device {device_path}")
    raise


# Example usage
if __name__ == "__main__":
  # This would be for testing the bridge in isolation
  import asyncio
  from dataclasses import dataclass

  @dataclass
  class MockConfig(Config):
    start_trigger_type: str = "caps_lock"
    stop_trigger_type: str = "caps_lock"

  async def test_bridge():
    config = MockConfig()

    try:
      bridge = create_keyboard_bridge("/dev/input/event0", config)

      # Subscribe to events
      bridge.observable.subscribe(
        on_next=lambda event: print(f"Key event: {event.key} at {event.timestamp_delta}ms"),
        on_error=lambda e: print(f"Error: {e}"),
        on_completed=lambda: print("Completed"),
      )

      async with bridge:
        print("Monitoring keyboard. Press Caps Lock to test...")
        await asyncio.sleep(30)  # Monitor for 30 seconds

    except Exception as e:
      print(f"Failed to start bridge: {e}")

  asyncio.run(test_bridge())
