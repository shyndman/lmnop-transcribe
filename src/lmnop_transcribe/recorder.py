import aiomultiprocess  # Import aiomultiprocess
from loguru import logger

from .audio_recorder import audio_recording_process  # Import the new multiprocessing function
from .config import Config  # Import Config to pass necessary values to the process
from .trigger_handler import wait_for_start_trigger, wait_for_stop_trigger  # Import async trigger functions
from .user_feedback import play_sound, send_notification  # These are now async functions


async def record(keyboard_device, config: Config):
  """
  Monitors for start and stop triggers and manages audio recording process using aiomultiprocess.
  """
  logger.info("Ready to start recording. Awaiting trigger...")

  audio_process = None  # Initialize audio process to None
  stop_event = None  # Initialize stop event to None

  while True:  # Main loop to wait for triggers
    # Wait for the start trigger
    await wait_for_start_trigger(keyboard_device, config)

    # Create a multiprocessing Event to signal the process to stop
    logger.info("Starting recording process using aiomultiprocess...")
    stop_event = aiomultiprocess.core.get_manager().Event()

    # Create an aiomultiprocess Process targeting the audio recording function
    # Pass necessary config values and the stop_event to the process
    audio_process = aiomultiprocess.Process(
      target=audio_recording_process,
      args=(
        config.audio_device_name,
        config.sample_rate,
        config.filename,
        config.channels,
        config.block_size,
        stop_event,
      ),
    )
    # Start the audio recording process asynchronously
    audio_process.start()
    logger.info("Audio recording process started.")

    if config.use_desktop_notifications:
      await send_notification("Recording started...")  # Await the async function
    _ignore = play_sound("start")  # Await the async function

    # Wait for the stop trigger
    await wait_for_stop_trigger(keyboard_device, config)

    logger.info("Stopping recording process...")
    # Set the stop event to signal the audio process to stop
    if stop_event:
      stop_event.set()
    # Wait for the audio process to finish asynchronously
    if audio_process and audio_process.is_alive():
      await audio_process.join()
      logger.info("Audio recording process joined.")
    audio_process = None  # Reset audio process
    stop_event = None  # Reset stop event

    if config.use_desktop_notifications:
      await send_notification("Recording stopped.")  # Await the async function
    await play_sound("stop")  # Await the async function

    # Loop back to wait for the next start trigger
    logger.info("Ready to start recording. Awaiting trigger...")
