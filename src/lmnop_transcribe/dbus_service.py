from sdbus import DbusInterfaceCommonAsync, dbus_signal_async

BUS_NAME = "com.lmnop_transcribe.Service"
OBJECT_PATH = "/com/lmnop_transcribe/Service"
INTERFACE_NAME = "com.lmnop_transcribe.Interface"


class DbusService(DbusInterfaceCommonAsync, interface_name=INTERFACE_NAME):
  @dbus_signal_async("")
  def ApplicationStarted(self) -> None:
    """Signal emitted when the application starts."""
    raise NotImplementedError

  @dbus_signal_async("")
  def RecordingStarted(self) -> None:
    """Signal emitted when recording starts."""
    raise NotImplementedError

  @dbus_signal_async("")
  def RecordingStopped(self) -> None:
    """Signal emitted when recording stops."""
    raise NotImplementedError

  @dbus_signal_async("")
  def TranscriptionStarted(self) -> None:
    """Signal emitted when transcription starts."""
    raise NotImplementedError

  @dbus_signal_async("s")
  def TranscriptionComplete(self) -> str:
    """Signal emitted when transcription is complete."""
    raise NotImplementedError

  @dbus_signal_async("s")
  def ErrorOccurred(self) -> str:
    """Signal emitted when an error occurs."""
    raise NotImplementedError
