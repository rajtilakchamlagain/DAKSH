"""
D.A.K.S.H. Midnight Rollover & Temporal Debt Engine
Subphase 1.3: Autonomous Ledger Re-balancing
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from .storage import StorageEngine

class RolloverDaemon:
    """
    Evaluates unresolved tasks at or after midnight.
    Carries pending tasks forward with strict accounting and debt tracking.
    """

    def __init__(self, storage: StorageEngine):
        self.storage = storage

    def execute_rollover(self, current_date_str: str) -> Dict[str, Any]:
        """
        Rolls over all uncompleted tasks from before current_date_str into current_date_str.
        """
        pending_past_tasks = self.storage.get_pending_tasks_before_date(current_date_str)
        rolled_count = 0
        rollover_details = []

        with self.storage._get_connection() as conn:
            for task in pending_past_tasks:
                task_id = task["id"]
                original_date = task["target_date"]
                new_rollover_count = task["rollover_count"] + 1

                # Update task to new target date with ROLLED_OVER status tag
                update_sql = """
                UPDATE tasks
                SET target_date = ?,
                    status = 'ROLLED_OVER',
                    rollover_count = ?
                WHERE id = ?
                """
                conn.execute(update_sql, (current_date_str, new_rollover_count, task_id))

                # Log to rollover ledger
                ledger_sql = """
                INSERT INTO rollover_ledger (task_id, from_date, to_date, rolled_at, reason)
                VALUES (?, ?, ?, ?, ?)
                """
                conn.execute(
                    ledger_sql,
                    (task_id, original_date, current_date_str, datetime.now().isoformat(), "AUTONOMOUS_MIDNIGHT_SWEEP")
                )

                rolled_count += 1
                rollover_details.append({
                    "task_id": task_id,
                    "title": task["title"],
                    "from_date": original_date,
                    "to_date": current_date_str,
                    "debt_score": new_rollover_count
                })

            conn.commit()

        return {
            "execution_time": datetime.now().isoformat(),
            "target_date": current_date_str,
            "tasks_rolled_over": rolled_count,
            "details": rollover_details
        }
