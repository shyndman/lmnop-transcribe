import select

import evdev

from .audio_recorder import record_audio
from .user_feedback import play_sound, send_notification


def record(q, device_name, sample_rate, keyboard_device, config_instance):
  print("Starting audio stream...")
  if config_instance.use_desktop_notifications:
    send_notification("Recording started...")
  play_sound("start")

  recording = True
  for audio_written in record_audio(q, device_name, int(sample_rate)):
    if not audio_written:
      continue

    r, _, _ = select.select([keyboard_device], [], [], 0)
    if r:
      for event in keyboard_device.read():
        if event.type == evdev.ecodes.EV_KEY:
          print("Stopping recording...")
          recording = False
          break
    if not recording:
      break

  print("Audio stream stopped.")
  if config_instance.use_desktop_notifications:
    send_notification("Recording stopped.")
  play_sound("stop")
