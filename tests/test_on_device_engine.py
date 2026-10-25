import unittest
from agent.on_device_engine import OnDeviceIntentEngine

class TestOnDeviceIntentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OnDeviceIntentEngine()

    def test_briefing_intent(self):
        res = self.engine.infer("Daksh, what did I miss today?")
        self.assertEqual(res["intent"], "BRIEFING")
        self.assertGreaterEqual(res["confidence"], 0.90)
        self.assertLess(res["latency_ms"], 50.0) # Sub-50ms target

    def test_nepali_briefing_intent(self):
        res = self.engine.infer("आज के के भयो? मलाई ब्रिफिङ दिनुहोस्")
        self.assertEqual(res["intent"], "BRIEFING")

    def test_habit_pushback_intent(self):
        res = self.engine.infer("I will skip gym workout today")
        self.assertEqual(res["intent"], "SKIP_HABIT")
        self.assertEqual(res["entities"].get("habit"), "gym")

    def test_debt_intent_financial(self):
        res = self.engine.infer("I owe Ram 500 rupees")
        self.assertEqual(res["intent"], "ADD_DEBT")
        self.assertEqual(res["entities"].get("type"), "FINANCIAL")
        self.assertEqual(res["entities"].get("amount"), 500.0)

    def test_debt_intent_emotional(self):
        res = self.engine.infer("Remind me to call Mom this evening")
        self.assertEqual(res["intent"], "ADD_DEBT")
        self.assertEqual(res["entities"].get("type"), "EMOTIONAL")

    def test_stand_down_intent(self):
        res = self.engine.infer("Go silent DAKSH")
        self.assertEqual(res["intent"], "STAND_DOWN")

if __name__ == "__main__":
    unittest.main()
