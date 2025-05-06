import multiprocessing
import queue
import socket

from loguru import logger
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import read_event, write_event


def transcribe_audio_with_wyoming(
  audio_queue: multiprocessing.Queue,
  wyoming_server_address: str,
  rate: int,
  sample_width: int,
  channels: int,
):
  """Transcribes audio chunks from a queue using Wyoming ASR via raw TCP socket."""

  try:
    host, port = wyoming_server_address.split(":")
    port = int(port)

    with socket.create_connection((host, port)) as s:
      io = s.makefile("wb")

      # Send transcribe event
      write_event(Transcribe().event(), io)
      write_event(AudioStart(rate=rate, width=sample_width, channels=channels).event(), io)
      logger.debug("Sent AudioStart event to Wyoming server.")

      while True:
        try:
          audio_chunk = audio_queue.get(timeout=0.1)
          if audio_chunk is None:
            break

          write_event(
            AudioChunk(rate=rate, width=sample_width, channels=channels, audio=audio_chunk).event(),
            io,
          )
          logger.debug(f"Sent audio chunk ({len(audio_chunk)} bytes) to Wyoming server.")

        except queue.Empty:
          # This assumes the audio recording process will put None when finished
          # Or the main process will close the queue
          # For now, we'll rely on a None signal or the main process joining the audio process
          pass

      # Send audio stop
      write_event(AudioStop().event(), io)
      logger.debug("Sent AudioStop event to Wyoming server.")

      # Receive transcript
      transcript_event = read_event(s.makefile("rb"))
      if transcript_event and Transcript.is_type(transcript_event.type):
        transcript = Transcript.from_event(transcript_event)
        transcribed_text = transcript.text.strip()
        logger.info(f"Received transcript: {transcribed_text}")
        return transcribed_text
      else:
        logger.warning(f"Unexpected event from Wyoming server: {transcript_event}")
        return None

  except ConnectionRefusedError as e:
    logger.error(f"Error connecting to Wyoming ASR server at {wyoming_server_address}: {e}")
    return None
  except Exception as e:
    logger.exception(f"Error transcribing audio with Wyoming: {e}")
    return None
