# Product Context: LMNOP Transcribe

## Purpose

The LMNOP Transcribe project aims to provide a simple and efficient tool for recording audio input and transcribing it. The primary use case is likely quick voice notes or transcriptions triggered by a user-defined action.

## Problems Solved

- Provides an easy way to start and stop audio recording using a keyboard trigger.
- Integrates with a Speech-to-Text service (Wyoming) for transcription.
- Allows configuration of audio devices and triggers.

## How it Should Work

The application should run in the background, monitoring for a specific start trigger. Once the start trigger is activated, it should begin recording audio from the configured device. Upon activation of a stop trigger, the recording should cease, and the recorded audio should be processed (e.g., saved and sent for transcription).

## User Experience Goals

- **Responsiveness:** The start and stop triggers should be detected and acted upon promptly, providing immediate feedback to the user.
- **Simplicity:** The application should be easy to configure and use with minimal user interaction beyond the defined triggers.
- **Reliability:** Recording should start and stop reliably based on the triggers, and audio data should be captured accurately.
