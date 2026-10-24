"""
Comprehensive Unit Tests for DAKSH Phase 1 Core Engine
Tests Subphases: 1.1 (Storage), 1.2 (Cadence), 1.3 (Rollover), 1.4 (EventBus)
"""

import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, date
from core import StorageEngine, TemporalCadenceEngine, RolloverDaemon, EventBus, DakshEventType

class TestDakshCoreEngine(unittest.TestCase):
    def setUp(self):
        # Use an in-memory database with shared cache for fast, lock-free testing
        self.test_db = f"file:memdb_{id(self)}?mode=memory&cache=shared"
        self.storage = StorageEngine(self.test_db)
        self.event_bus = EventBus()
        self.event_bus.clear()

    def tearDown(self):
        pass

    def test_01_storage_task_lifecycle(self):
        task_id = "TASK_001"
        self.storage.insert_task({
            "id": task_id,
            "title": "Daily 5000 Step Walk",
            "category": "HEALTH",
            "priority": "HIGH",
            "status": "PENDING",
            "target_date": "2026-10-25",
            "target_time": "07:00:00",
            "created_at": datetime.now().isoformat(),
            "rollover_count": 0,
            "tags": "walk,fitness"
        })

        tasks = self.storage.get_tasks_for_date("2026-10-25")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Daily 5000 Step Walk")

        # Mark completed
        res = self.storage.update_task_status(task_id, "COMPLETED")
        self.assertTrue(res)
        updated = self.storage.get_tasks_for_date("2026-10-25")[0]
        self.assertEqual(updated["status"], "COMPLETED")
        self.assertIsNotNone(updated["completed_at"])

    def test_02_alternate_day_cadence_modulo(self):
        # Anchor date: 2026-10-20
        shampoo_rule = {
            "id": "CAD_SHAMPOO",
            "name": "Alternate Day Hair Wash",
            "cadence_type": "ALTERNATE_DAYS",
            "anchor_date": "2026-10-20",
            "interval_days": 2,
            "is_active": 1
        }

        # Day 0 (Anchor): 2026-10-20 -> (0 % 2 == 0) -> Due
        self.assertTrue(TemporalCadenceEngine.is_cadence_due_on(shampoo_rule, date(2026, 10, 20)))
        # Day 1: 2026-10-21 -> (1 % 2 != 0) -> Not Due
        self.assertFalse(TemporalCadenceEngine.is_cadence_due_on(shampoo_rule, date(2026, 10, 21)))
        # Day 2: 2026-10-22 -> (2 % 2 == 0) -> Due
        self.assertTrue(TemporalCadenceEngine.is_cadence_due_on(shampoo_rule, date(2026, 10, 22)))
        # Day 5: 2026-10-25 -> (5 % 2 != 0) -> Not Due
        self.assertFalse(TemporalCadenceEngine.is_cadence_due_on(shampoo_rule, date(2026, 10, 25)))
        # Day 6: 2026-10-26 -> (6 % 2 == 0) -> Due
        self.assertTrue(TemporalCadenceEngine.is_cadence_due_on(shampoo_rule, date(2026, 10, 26)))

    def test_03_specific_weekday_cadence(self):
        # Trash alert on Monday & Thursday
        trash_rule = {
            "id": "CAD_TRASH",
            "name": "Trash Pickup Night",
            "cadence_type": "SPECIFIC_WEEKDAYS",
            "anchor_date": "2026-10-01",
            "active_weekdays": "MON,THU",
            "is_active": 1
        }

        # 2026-10-26 is Monday -> Due
        self.assertTrue(TemporalCadenceEngine.is_cadence_due_on(trash_rule, date(2026, 10, 26)))
        # 2026-10-27 is Tuesday -> Not Due
        self.assertFalse(TemporalCadenceEngine.is_cadence_due_on(trash_rule, date(2026, 10, 27)))

    def test_04_midnight_rollover_debt_engine(self):
        daemon = RolloverDaemon(self.storage)

        # Create two tasks from yesterday (2026-10-24)
        self.storage.insert_task({
            "id": "TASK_PAST_1",
            "title": "Clean Workspace Desk",
            "category": "ORGANIZATION",
            "priority": "LOW",
            "status": "PENDING",
            "target_date": "2026-10-24",
            "target_time": "20:00:00",
            "created_at": datetime.now().isoformat(),
            "rollover_count": 0,
            "tags": "home"
        })
        self.storage.insert_task({
            "id": "TASK_PAST_2",
            "title": "Review Bank Statement",
            "category": "FINANCE",
            "priority": "HIGH",
            "status": "PENDING",
            "target_date": "2026-10-24",
            "target_time": "21:00:00",
            "created_at": datetime.now().isoformat(),
            "rollover_count": 1, # Already rolled once before
            "tags": "finance"
        })

        # Run midnight rollover sweep into today (2026-10-25)
        result = daemon.execute_rollover("2026-10-25")
        self.assertEqual(result["tasks_rolled_over"], 2)

        # Verify tasks are now in 2026-10-25 with incremented debt score
        today_tasks = self.storage.get_tasks_for_date("2026-10-25")
        self.assertEqual(len(today_tasks), 2)
        
        task_1 = next(t for t in today_tasks if t["id"] == "TASK_PAST_1")
        self.assertEqual(task_1["status"], "ROLLED_OVER")
        self.assertEqual(task_1["rollover_count"], 1)

        task_2 = next(t for t in today_tasks if t["id"] == "TASK_PAST_2")
        self.assertEqual(task_2["rollover_count"], 2)

    def test_05_reactive_event_bus(self):
        received_events = []

        def handle_signal(payload):
            received_events.append(payload)

        self.event_bus.subscribe(DakshEventType.VOICE_INTENT_TRIGGERED, handle_signal)
        self.event_bus.publish(DakshEventType.VOICE_INTENT_TRIGGERED, {"intent": "RENAME_CONTACT", "contact": "Priya", "new_name": "Swimi"})

        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0]["contact"], "Priya")
        self.assertEqual(received_events[0]["new_name"], "Swimi")

if __name__ == '__main__':
    unittest.main()
