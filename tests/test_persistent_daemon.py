import unittest
import os
import gc
from core.persistent_daemon import PersistentStorageDaemon

class TestPersistentStorageDaemon(unittest.TestCase):
    def setUp(self):
        self.test_db = f"test_persistent_{self._testMethodName}.db"
        self.daemon = PersistentStorageDaemon(db_path=self.test_db)

    def tearDown(self):
        del self.daemon
        gc.collect()
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except OSError:
                pass

    def test_cadence_persistence(self):
        self.daemon.add_cadence("CAD_01", "Daily Gym", "DAILY", "07:00 AM")
        cadences = self.daemon.get_active_cadences()
        self.assertEqual(len(cadences), 1)
        self.assertEqual(cadences[0]["title"], "Daily Gym")

    def test_debt_persistence_and_rollover(self):
        self.daemon.add_debt("DEBT_01", "Pay Ram for Books", "FINANCIAL", "2026-10-23", amount=500.0, counterparty="Ram")
        self.daemon.add_debt("EMOT_01", "Call Mom this week", "EMOTIONAL", "2026-10-20")
        
        debts = self.daemon.get_unsettled_debts()
        self.assertEqual(len(debts), 2)
        
        # Test midnight rollover
        rolled = self.daemon.roll_uncompleted_debts("2026-10-25")
        self.assertEqual(rolled, 2)
        
        updated_debts = self.daemon.get_unsettled_debts()
        self.assertEqual(updated_debts[0]["rollover_count"], 1)

    def test_sentinel_audit_logging(self):
        self.daemon.log_notification("com.whatsapp", "Mom", "Are you having lunch?", is_actionable=True)
        self.assertTrue(os.path.exists(self.test_db))

if __name__ == "__main__":
    unittest.main()
