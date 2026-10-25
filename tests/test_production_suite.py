import unittest
import os
import gc
from core.encrypted_sync import EncryptedCloudSyncManager
from core.briefing_orchestrator import TacticalLifeBriefingOrchestrator
from core.life_os_runtime import AutonomousLifeOSRuntime

class TestProductionLifeOSSuite(unittest.TestCase):
    def setUp(self):
        self.test_db = f"test_prod_{self._testMethodName}.db"
        self.sync_mgr = EncryptedCloudSyncManager(master_key="daksh_super_secret_test_key_123")
        self.orchestrator = TacticalLifeBriefingOrchestrator(db_path=self.test_db)
        self.runtime = AutonomousLifeOSRuntime(db_path=self.test_db)

    def tearDown(self):
        del self.orchestrator
        del self.runtime
        gc.collect()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except OSError:
                pass

    def test_encrypted_sync_pipeline(self):
        payload = {"cadences": ["Gym", "Shampoo"], "user": "rajtilak"}
        envelope = self.sync_mgr.prepare_sync_bundle(payload["cadences"], [], [])
        self.assertIn("encrypted_envelope", envelope)
        self.assertIn("sha256_checksum", envelope)
        
        # Test Decryption
        decrypted = self.sync_mgr.decrypt_payload(envelope["encrypted_envelope"])
        self.assertEqual(decrypted["cadences"], ["Gym", "Shampoo"])

    def test_briefing_orchestrator_generation(self):
        sample_packets = [
            {"package": "com.whatsapp", "title": "Boss", "text": "Urgent update", "isActionable": True},
            {"package": "com.twitter", "title": "News", "text": "Headlines", "isActionable": False}
        ]
        briefing = self.orchestrator.generate_briefing(sample_packets)
        self.assertIn("verbal_script", briefing)
        self.assertEqual(briefing["metrics"]["actionable_notifications"], 1)

    def test_habit_pushback_discipline_challenge(self):
        # 1 skip
        res1 = self.orchestrator.evaluate_habit_deferral("I will skip gym workout today", consecutive_skips=0)
        self.assertTrue(res1["should_pushback"])
        self.assertEqual(res1["risk_level"], "MODERATE")
        
        # 3 consecutive skips
        res3 = self.orchestrator.evaluate_habit_deferral("Not going to gym tonight", consecutive_skips=2)
        self.assertTrue(res3["should_pushback"])
        self.assertEqual(res3["risk_level"], "HIGH")
        self.assertIn("consecutive deferrals", res3["challenge_statement"])

    def test_life_os_runtime_e2e_dispatch(self):
        # Test Debt Voice Insertion
        out1 = self.runtime.process_utterance("I owe Ram 500 rupees")
        self.assertEqual(out1["resolved_intent"], "ADD_DEBT")
        self.assertEqual(out1["action"], "PERSIST_DEBT")

        # Test Stand Down Directive
        out2 = self.runtime.process_utterance("Go silent DAKSH")
        self.assertEqual(out2["resolved_intent"], "STAND_DOWN")
        self.assertTrue(self.runtime.is_silent_mode)

if __name__ == "__main__":
    unittest.main()
