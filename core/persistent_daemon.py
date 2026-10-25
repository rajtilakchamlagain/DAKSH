import sqlite3
import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "daksh_persistent.db"

class PersistentStorageDaemon:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Cadences table with parity and execution logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persistent_cadences (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    cadence_type TEXT NOT NULL,
                    target_time TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    last_completed TEXT,
                    parity_anchor TEXT DEFAULT '2026-01-01',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Rollover debt ledger (financial + task + emotional)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persistent_debt (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    debt_type TEXT NOT NULL, -- 'FINANCIAL', 'TASK', 'EMOTIONAL'
                    amount REAL DEFAULT 0.0,
                    counterparty TEXT,
                    original_date TEXT NOT NULL,
                    rollover_count INTEGER DEFAULT 0,
                    priority TEXT DEFAULT 'MEDIUM',
                    is_settled INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Intercepted notifications audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sentinel_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package TEXT NOT NULL,
                    title TEXT,
                    content TEXT,
                    is_actionable INTEGER DEFAULT 0,
                    intercepted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_cadence(self, cadence_id: str, title: str, cadence_type: str, target_time: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO persistent_cadences (id, title, cadence_type, target_time)
                VALUES (?, ?, ?, ?)
            """, (cadence_id, title, cadence_type, target_time))
            conn.commit()
            return True

    def add_debt(self, debt_id: str, title: str, debt_type: str, original_date: str, amount: float = 0.0, counterparty: str = "") -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO persistent_debt (id, title, debt_type, original_date, amount, counterparty)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (debt_id, title, debt_type, original_date, amount, counterparty))
            conn.commit()
            return True

    def roll_uncompleted_debts(self, target_date: str) -> int:
        """Midnight rollover engine: increments rollover_count for all unsettled items"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE persistent_debt
                SET rollover_count = rollover_count + 1
                WHERE is_settled = 0 AND original_date < ?
            """, (target_date,))
            count = cursor.rowcount
            conn.commit()
            return count

    def get_unsettled_debts(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persistent_debt WHERE is_settled = 0 ORDER BY rollover_count DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_active_cadences(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persistent_cadences WHERE is_active = 1")
            return [dict(row) for row in cursor.fetchall()]

    def log_notification(self, package: str, title: str, content: str, is_actionable: bool = False):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sentinel_audit_log (package, title, content, is_actionable)
                VALUES (?, ?, ?, ?)
            """, (package, title, content, 1 if is_actionable else 0))
            conn.commit()
