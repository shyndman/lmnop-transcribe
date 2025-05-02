import asyncio  # Import asyncio

from .audio_recorder import record_audio  # This is now an async function
from .trigger_handler import wait_for_start_trigger, wait_for_stop_trigger  # Import async trigger functions
from .user_feedback import play_sound, send_notification  # These are now async functions


async def record(q, device_name, sample_rate, keyboard_device, config_instance):
  """
  Monitors for start and stop triggers and manages audio recording.
  """
  print("Ready to start recording. Awaiting trigger...")

  recording_signal = asyncio.Event()  # Create an asyncio Event for signaling recording state
  audio_task = None  # Initialize audio task to None

  while True:  # Main loop to wait for triggers
    # Wait for the start trigger
    await wait_for_start_trigger(keyboard_device, config_instance)

    print("Starting recording...")
    # Set the recording signal
    recording_signal.set()
    # Create and start the audio recording task
    audio_task = asyncio.create_task(record_audio(q, device_name, sample_rate, recording_signal))

    if config_instance.use_desktop_notifications:
      await send_notification("Recording started...")  # Await the async function
    await play_sound("start")  # Await the async function

    # Wait for the stop trigger
    await wait_for_stop_trigger(keyboard_device, config_instance)

    print("Stopping recording...")
    # Clear the recording signal
    recording_signal.clear()
    # Cancel the audio recording task
    if audio_task:
      audio_task.cancel()
      try:
        await audio_task
      except asyncio.CancelledError:
        print("Audio recording task cancelled.")
      audio_task = None  # Reset audio task

    if config_instance.use_desktop_notifications:
      await send_notification("Recording stopped.")  # Await the async function
    await play_sound("stop")  # Await the async function

    print("Ready to start recording. Awaiting trigger...")  # Loop back to wait for the next start trigger
