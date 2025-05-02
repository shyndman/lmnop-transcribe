import socket
import wave

from loguru import logger
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import read_event, write_event


def transcribe_audio_with_wyoming(audio_file, wyoming_server_address):
  """Transcribes the audio file using Wyoming ASR via raw TCP socket."""

  try:
    host, port = wyoming_server_address.split(":")
    port = int(port)

    with socket.create_connection((host, port)) as s:
      with wave.open(audio_file, "rb") as wf:
        frame_rate = wf.getframerate()
        sample_width = wf.getsampwidth()
        num_channels = wf.getnchannels()

        # Send transcribe event
        write_event(Transcribe().event(), s.makefile("wb"))

        # Send audio start
        write_event(
          AudioStart(rate=frame_rate, width=sample_width, channels=num_channels).event(), s.makefile("wb")
        )

        # Send audio chunks
        while True:
          audio_data = wf.readframes(1024)  # Adjust chunk size as needed
          if not audio_data:
            break

          chunk = AudioChunk(
            rate=frame_rate,
            width=sample_width,
            channels=num_channels,
            audio=audio_data,
          )
          write_event(chunk.event(), s.makefile("wb"))

        # Send audio stop
        write_event(AudioStop().event(), s.makefile("wb"))

        # Receive transcript
        transcript_event = read_event(s.makefile("rb"))

        if transcript_event and Transcript.is_type(transcript_event.type):
          transcript = Transcript.from_event(transcript_event)
          transcribed_text = transcript.text.strip()
          return transcribed_text
        else:
          logger.warning(f"Unexpected event: {transcript_event}")
          return None

  except ConnectionRefusedError as e:
    logger.error(f"Error connecting to Wyoming ASR server: {e}")
    return None
  except Exception as e:
    logger.exception(f"Error transcribing audio: {e}")
