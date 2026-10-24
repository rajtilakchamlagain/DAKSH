"""
Unit Tests for Phase 3: Tactical Intent Router & Multi-Agent Brain
Tests: Subphase 3.1 (Schemas), 3.2 (Router), 3.3 (Persona), 3.4 (Coordinator)
"""

import unittest
import os
import sys
from datetime import date

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent import TacticalRouter, TacticalPersonaEngine, DakshBrainCoordinator, ActionType, IntentCategory
from core import StorageEngine

class TestPhase3Brain(unittest.TestCase):
    def setUp(self):
        self.ref_date = date(2026, 10, 25) # Fixed reference Sunday
        self.router = TacticalRouter(self.ref_date)
        self.storage = StorageEngine(f"file:memdb_brain_{id(self)}?mode=memory&cache=shared")
        self.coordinator = DakshBrainCoordinator(self.storage, self.ref_date)

    def test_01_contact_rename_intent_routing(self):
        cmd = "Rename contact Priya to Swimi"
        route = self.router.route_intent(cmd)

        self.assertEqual(route["category"], IntentCategory.DEVICE_MUTATION.value)
        self.assertEqual(route["action"], ActionType.RENAME_CONTACT.value)
        self.assertEqual(route["params"]["current_name"], "priya")
        self.assertEqual(route["params"]["new_name"], "swimi")
        self.assertEqual(route["target_subsystem"], "NATIVE_CONTACTS_CONTROLLER")

    def test_02_task_reschedule_intent_routing(self):
        cmd = "Push my daily walk to tomorrow morning"
        route = self.router.route_intent(cmd)

        self.assertEqual(route["category"], IntentCategory.TEMPORAL_OPERATION.value)
        self.assertEqual(route["action"], ActionType.RESCHEDULE_TASK.value)
        self.assertEqual(route["params"]["task_query"], "daily walk")
        self.assertEqual(route["params"]["new_date"], "2026-10-26") # Tomorrow
        self.assertEqual(route["params"]["new_time"], "07:00:00") # Morning

    def test_03_alternate_day_cadence_intent(self):
        cmd = "Remind me to use shampoo on alternate days"
        route = self.router.route_intent(cmd)

        self.assertEqual(route["category"], IntentCategory.TEMPORAL_OPERATION.value)
        self.assertEqual(route["action"], ActionType.REGISTER_CADENCE.value)
        self.assertEqual(route["params"]["cadence_type"], "ALTERNATE_DAYS")
        self.assertEqual(route["params"]["interval_days"], 2)

    def test_04_tactical_persona_cadence(self):
        reply = TacticalPersonaEngine.format_contact_rename_response("Priya", "Swimi", True)
        self.assertIn("Contact Priya updated to Swimi, sir.", reply)
        self.assertNotIn("As an AI", reply)

        reschedule_reply = TacticalPersonaEngine.format_reschedule_response("workout", "2026-10-26", "18:00:00")
        self.assertEqual(reschedule_reply, "Understood, sir. Shifting workout to 2026-10-26 at 18:00:00.")

    def test_05_coordinator_end_to_end_pipeline(self):
        result = self.coordinator.process_voice_command("Change contact Priya to Swimi")
        self.assertEqual(result["dispatch_payload"]["target"], "NATIVE_BRIDGE")
        self.assertEqual(result["dispatch_payload"]["method"], "renameContact")
        self.assertEqual(result["dispatch_payload"]["args"]["newName"], "swimi")
        self.assertIn("Contact priya updated to swimi, sir.", result["spoken_response"])

if __name__ == '__main__':
    unittest.main()
