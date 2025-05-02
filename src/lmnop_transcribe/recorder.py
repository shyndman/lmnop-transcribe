import argparse
import queue
import select
from typing import cast

import evdev
import sounddevice as sd
import soundfile as sf

# Configuration constants
KEYBOARD_DEVICE_NAME = "AT Translated Set 2 keyboard"  # Replace with your keyboard device name
CHANNELS = 1
BLOCK_SIZE = 2048
FILENAME = "output.wav"
NOTIFICATION_SOUND = "path/to/notification.wav"  # Optional
AUDIO_CLEANUP_COMMAND = "command to clean up audio"  # Optional


def main():
  parser = argparse.ArgumentParser(description="Record audio from keyboard input.")
  parser.add_argument("--device", type=str, default=None, help="Audio device index or 'list'.")
  parser.add_argument("--rate", type=int, default=44100, help="Sample rate.")
  args = parser.parse_args()

  print("Starting recorder.py")

  if args.device == "list":
    print("Available audio devices:")
    devices = cast(tuple[dict[str, str | int], ...], sd.query_devices())
    for i, device in enumerate(devices):
      is_input = cast(int, device["max_input_channels"]) > 0
      print(f"  - {i}: {device['name']} (input={is_input})")
    return

  devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
  print("Available devices:")
  for device in devices:
    print(f"  - {device.path}: {device.name}")
  keyboard_device = None
  if KEYBOARD_DEVICE_NAME != "your_keyboard_device_name":
    for device in devices:
      if device.name == KEYBOARD_DEVICE_NAME:
        keyboard_device = device
        break
  else:
    print("No keyboard device name specified, attempting to use first available keyboard.")

  if keyboard_device is None:
    for device in devices:
      if "keyboard" in device.name.lower():
        keyboard_device = device
        break

  if keyboard_device is None:
    print("No keyboard device found.")
    return

  print(f"Using keyboard device: {keyboard_device.name}")

  q = queue.Queue()

  def audio_callback(indata, frames, time, status):
    if status:
      print(status)
    q.put(indata.copy())

  try:
    device_id = int(args.device) if args.device else None
    stream = sd.InputStream(
      device=device_id,
      samplerate=args.rate,
      channels=CHANNELS,
      blocksize=BLOCK_SIZE,
      callback=audio_callback,
    )
    print(
      f"Audio stream initialized with device={device_id}, "
      + "samplerate={args.rate}, channels={CHANNELS}, blocksize={BLOCK_SIZE}"
    )

    print("Starting audio stream...")
    with stream:
      print("Recording... Press any key to stop.")
      recording = True
      with sf.SoundFile(FILENAME, mode="w", samplerate=args.rate, channels=CHANNELS) as file:
        while recording:
          try:
            data = q.get(timeout=0.1)
            file.write(data)
            print(f"Wrote {len(data)} samples to file")

            # Implement user feedback with console messages and optional desktop
            # notifications and sound effects
            # TODO: Implement desktop notifications and sound effects

            r, _, _ = select.select([keyboard_device], [], [], 0)
            if r:
              for event in keyboard_device.read():
                if event.type == evdev.ecodes.EV_KEY:
                  print("Stopping recording...")
                  recording = False
                  break
          except queue.Empty:
            pass
    print("Audio stream stopped.")
  except Exception as e:
    print(f"Error: {e}")
    return


if __name__ == "__main__":
  main()
