# Active Context: LMNOP Transcribe

## Current Work Focus

The primary focus is currently on debugging and resolving the issue where the stop recording trigger is unresponsive when audio recording is active.

## Recent Changes

-   Added detailed logging to `src/lmnop_transcribe/trigger_handler.py` to observe all received `evdev` events.
-   Temporarily modified `src/lmnop_transcribe/recorder.py` to bypass audio recording for testing purposes (since reverted).
-   Modified `src/lmnop_transcribe/audio_recorder.py` to use `loop.run_in_executor` for non-blocking file writing (did not resolve the trigger responsiveness issue).
-   Corrected a typo in `src/lmnop_transcribe/config.py` related to loading the keyboard device name.

## Active Decisions and Considerations

-   It has been confirmed through testing that the audio recording process is the cause of the delayed `evdev` event processing and the unresponsive stop trigger.
-   The delayed event processing appears to be a known challenge with `python-evdev`'s asynchronous read loop, likely related to buffering and timing.
-   The decision has been made to refactor the application to use `multiprocessing` for audio recording to isolate this activity from the main process's event loop and improve trigger responsiveness.
-   The plan is to use a `multiprocessing.Event` for signaling between the main process and the audio process for starting and stopping recording.

## Learnings and Project Insights

-   Interactions between different libraries and the asyncio event loop can lead to unexpected blocking or delays.
-   Debugging asynchronous applications requires careful observation of event flow and potential bottlenecks.
-   Multiprocessing is a valuable pattern for isolating potentially problematic operations in Python.

## Pending Tasks and Next Steps

-   Implement the refactoring to use `multiprocessing` for audio recording as per the plan in `memory-bank/systemPatterns.md`. This involves:
    -   Creating a new function for the audio recording logic in `src/lmnop_transcribe/audio_recorder.py`.
    -   Modifying `src/lmnop_transcribe/recorder.py` to manage the multiprocessing.Process and the multiprocessing.Event.
    -   Updating the new audio recording function to use the event for stopping.
-   Test the application after implementing multiprocessing to confirm that the stop trigger is now responsive.
