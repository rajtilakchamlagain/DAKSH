"""
Unit Tests for Phase 6: Field Hardening & Sovereign Privacy
Tests: Subphase 6.1 (Battery Profiling), 6.2 (Offline Failover), 6.3 (Privacy Audit)
"""

import unittest
import os
import sys

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.battery_governor import BatteryGovernor
from core.privacy_auditor import PrivacyAuditor
from agent.offline_failover import SovereignOfflineFailover, ConnectivityState
from agent.router import TacticalRouter

class TestPhase6Hardening(unittest.TestCase):
    def setUp(self):
        self.router = TacticalRouter()
        self.failover = SovereignOfflineFailover(self.router, is_online=True)

    def test_01_battery_governor_adaptive_throttling(self):
        # 100% Battery -> TACTICAL_VIGILANT
        gov = BatteryGovernor(current_battery_pct=100.0)
        profile = gov.evaluate_duty_cycle()
        self.assertEqual(profile["profile"], "TACTICAL_VIGILANT")
        self.assertTrue(profile["hotword_active"])

        # 20% Battery -> BALANCED_PRESERVATION (hotword disabled, push-to-talk, batched triage)
        gov.battery_pct = 20.0
        profile = gov.evaluate_duty_cycle()
        self.assertEqual(profile["profile"], "BALANCED_PRESERVATION")
        self.assertFalse(profile["hotword_active"])
        self.assertEqual(profile["sentinel_batching_seconds"], 30)

        # 10% Battery -> EMERGENCY_SOVEREIGN
        gov.battery_pct = 10.0
        profile = gov.evaluate_duty_cycle()
        self.assertEqual(profile["profile"], "EMERGENCY_SOVEREIGN")
        self.assertFalse(profile["tts_streaming_enabled"])

    def test_02_24h_battery_drain_simulation(self):
        gov = BatteryGovernor(100.0)
        sim = gov.simulate_24h_drain()
        self.assertEqual(sim["duration_hours"], 24)
        # Should stay well within realistic 15% budget for background life OS
        self.assertTrue(sim["safe_for_daily_driver"])
        self.assertLess(sim["projected_total_drain_pct"], 15.0)

    def test_03_offline_sovereign_failover(self):
        # Disconnect network
        self.failover.set_connectivity(is_online=False)
        self.assertEqual(self.failover.state, ConnectivityState.OFFLINE_SOVEREIGN)

        # Command should still process completely locally
        res = self.failover.execute_request("Rename contact Priya to Swimi")
        self.assertEqual(res["engine_used"], "LOCAL_SOVEREIGN_ROUTER")
        self.assertEqual(res["tts_provider"], "ON_DEVICE_ANDROID_NEURAL_TTS")
        self.assertFalse(res["cloud_leakage"])

    def test_04_privacy_auditor_pii_redaction(self):
        raw_msg = "Your Swiggy delivery OTP is 849201. Call courier at 9876543210 or email help@swiggy.com"
        audit = PrivacyAuditor.sanitize_outbound_payload(raw_msg)

        self.assertTrue(audit["pii_detected"])
        sanitized = audit["sanitized_text"]
        self.assertNotIn("849201", sanitized)
        self.assertNotIn("9876543210", sanitized)
        self.assertNotIn("help@swiggy.com", sanitized)
        self.assertIn("[REDACTED_SEC_CODE]", sanitized)
        self.assertIn("[REDACTED_PHONE]", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)

if __name__ == '__main__':
    unittest.main()
