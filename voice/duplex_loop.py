"""
D.A.K.S.H. Full-Duplex Dialogue & Barge-In Coordinator
Subphase 4.3: Real-Time Acoustic Arbitration & Interruption Handling
"""

from typing import Dict, Any, Optional, Callable
from enum import Enum
import threading
from .wake_word import WakeWordDetector
from .dsp import AudioDSPConfig
from agent.coordinator import DakshBrainCoordinator

class AudioChannelState(Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    BARGE_IN_TRIGGERED = "BARGE_IN_TRIGGERED"

class FullDuplexAudioLoop:
    """
    Coordinates continuous microphone ingestion, wake word gating,
    brain dispatching, and instant barge-in playback cancellation.
    """

    def __init__(
        self,
        brain: DakshBrainCoordinator,
        audio_dsp: Optional[AudioDSPConfig] = None,
        tts_playback_sink: Optional[Callable[[str, AudioDSPConfig], None]] = None
    ):
        self.brain = brain
        self.dsp = audio_dsp or AudioDSPConfig()
        self.tts_sink = tts_playback_sink or self._default_tts_sink
        self.state = AudioChannelState.IDLE
        self._lock = threading.Lock()
        self._current_audio_cancel_event = threading.Event()

    def handle_incoming_transcript(self, transcript: str) -> Optional[Dict[str, Any]]:
        """
        Receives ASR transcript token stream.
        Handles wake-word detection or active barge-in.
        """
        with self._lock:
            # If the user speaks while D.A.K.S.H. is already speaking -> trigger barge-in
            if self.state == AudioChannelState.SPEAKING:
                self.trigger_barge_in()

        is_wake, command = WakeWordDetector.evaluate_utterance(transcript)

        # If not already listening and no wake word -> ignore ambient chatter
        if not is_wake and self.state == AudioChannelState.IDLE:
            return None

        # Set processing state
        self.state = AudioChannelState.PROCESSING

        # Dispatch to Brain
        result = self.brain.process_voice_command(command or transcript)

        # Transition to speaking response
        spoken_text = result["spoken_response"]
        if spoken_text:
            self.speak_response(spoken_text)

        return result

    def speak_response(self, text: str):
        with self._lock:
            self.state = AudioChannelState.SPEAKING
            self._current_audio_cancel_event.clear()

        # Emit to output sink (e.g. ElevenLabs or Neural TTS)
        self.tts_sink(text, self.dsp)

        with self._lock:
            if self.state == AudioChannelState.SPEAKING:
                self.state = AudioChannelState.IDLE

    def trigger_barge_in(self):
        """Immediately halts hardware speaker output when the user begins speaking"""
        self._current_audio_cancel_event.set()
        self.state = AudioChannelState.BARGE_IN_TRIGGERED

    def _default_tts_sink(self, text: str, dsp: AudioDSPConfig):
        # Simulated or local audio output
        pass
