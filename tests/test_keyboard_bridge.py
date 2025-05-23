#!/usr/bin/env python3
"""
Test script for the keyboard bridge (requires actual input device).
Run this to test keyboard event detection before full integration.
"""

from dataclasses import dataclass

import pytest

from lmnop_transcribe.keyboard_bridge import create_keyboard_bridge


@dataclass
class _TestConfig:
  """Test configuration matching your config structure (prefixed with _ to avoid pytest collection)"""

  start_trigger_type: str = "caps_lock"
  stop_trigger_type: str = "caps_lock"


def test_keyboard_bridge():
  """Test the keyboard bridge creation (without hanging on device monitoring)"""

  config = _TestConfig()

  # Try common input device paths
  device_paths = ["/dev/input/event0", "/dev/input/event1", "/dev/input/event2", "/dev/input/event3"]

  print("🔍 Testing keyboard bridge creation...")

  # List available devices
  try:
    import evdev

    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    print("Available input devices:")
    for device in devices:
      print(f"  {device.path}: {device.name}")
  except Exception as e:
    print(f"  Could not list devices: {e}")

  # Try to create bridge with first available device
  bridge = None
  for device_path in device_paths:
    try:
      bridge = create_keyboard_bridge(device_path, config)
      print(f"✅ Successfully created bridge for {device_path}")

      # Verify the bridge has the expected interface
      assert bridge is not None
      assert hasattr(bridge, "observable")
      assert hasattr(bridge, "start_monitoring")
      assert hasattr(bridge, "stop_monitoring")

      # Test that we can subscribe to the observable (without starting monitoring)
      events_received = []
      bridge.observable.subscribe(
        on_next=lambda event: events_received.append(event),
        on_error=lambda e: print(f"❌ Error: {e}"),
        on_completed=lambda: print("✅ Keyboard monitoring completed"),
      )

      print("✅ Bridge interface verification passed")
      return  # Success, exit test

    except (PermissionError, FileNotFoundError) as e:
      print(f"❌ Failed to open {device_path}: {e}")
      continue

  # If we get here, no devices were available
  print("❌ Could not open any input device")
  print("💡 This is expected in CI/testing environments without input devices")
  print("💡 Try running as root or check device permissions for real testing")

  # Don't fail the test if no devices are available (common in CI)
  pytest.skip("No accessible input devices found - skipping keyboard bridge test")
