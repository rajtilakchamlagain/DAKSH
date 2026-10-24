"""
Unit Tests for Phase 4: Baritone Voice & Full-Duplex Audio
Tests: Subphase 4.1 (DSP), 4.2 (Wake-Word), 4.3 (Duplex Loop & Barge-In)
"""

import unittest
import os
import sys
from datetime import date

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from voice import AudioDSPConfig, WakeWordDetector, FullDuplexAudioLoop, AudioChannelState
from agent import DakshBrainCoordinator
from core import StorageEngine

class TestPhase4Voice(unittest.TestCase):
    def setUp(self):
        self.storage = StorageEngine(f"file:memdb_voice_{id(self)}?mode=memory&cache=shared")
        self.brain = DakshBrainCoordinator(self.storage, date(2026, 10, 25))
        self.tts_calls = []

        def mock_tts(text, dsp):
            self.tts_calls.append({"text": text, "dsp": dsp})

        self.duplex = FullDuplexAudioLoop(
            brain=self.brain,
            tts_playback_sink=mock_tts
        )

    def test_01_dsp_acoustic_configuration(self):
        dsp = AudioDSPConfig()
        cfg = dsp.to_dict()
        self.assertEqual(cfg["voice_profile"], "VISION_BARITONE")
        self.assertEqual(cfg["pitch_shift_semitones"], -2.5)
        self.assertEqual(cfg["speed_rate"], 0.98)
        self.assertGreater(cfg["bass_boost_db"], 0.0)

    def test_02_wake_word_detection(self):
        # Case A: Exact keyword prefix
        is_wake, cmd = WakeWordDetector.evaluate_utterance("Daksh, rename Priya to Swimi")
        self.assertTrue(is_wake)
        self.assertEqual(cmd, "rename Priya to Swimi")

        # Case B: Casual prefix
        is_wake, cmd = WakeWordDetector.evaluate_utterance("Hey Daksh, push walk to tomorrow")
        self.assertTrue(is_wake)
        self.assertEqual(cmd, "push walk to tomorrow")

        # Case C: Irrelevant background chatter
        is_wake, cmd = WakeWordDetector.evaluate_utterance("What is the weather outside today?")
        self.assertFalse(is_wake)
        self.assertEqual(cmd, "What is the weather outside today?")

    def test_03_duplex_loop_with_wake_gating(self):
        # Chatter without wake word -> ignored (returns None)
        res = self.duplex.handle_incoming_transcript("Someone is knocking on the door.")
        self.assertIsNone(res)
        self.assertEqual(len(self.tts_calls), 0)

        # Trigger with wake word
        res = self.duplex.handle_incoming_transcript("Daksh, rename Priya to Swimi")
        self.assertIsNotNone(res)
        self.assertEqual(len(self.tts_calls), 1)
        self.assertIn("Contact priya updated to swimi, sir.", self.tts_calls[0]["text"])

    def test_04_barge_in_interruption(self):
        # Simulate active speaking state
        self.duplex.state = AudioChannelState.SPEAKING
        self.assertTrue(self.duplex.state == AudioChannelState.SPEAKING)

        # User interrupts with new speech
        self.duplex.trigger_barge_in()
        self.assertEqual(self.duplex.state, AudioChannelState.BARGE_IN_TRIGGERED)
        self.assertTrue(self.duplex._current_audio_cancel_event.is_set())

if __name__ == '__main__':
    unittest.main()
