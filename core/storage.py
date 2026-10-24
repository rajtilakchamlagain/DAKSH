"""
D.A.K.S.H. Core Storage & Schema Definitions
Subphase 1.1: Encrypted/Local Persistence Schema
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'GENERAL',
    priority TEXT CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')) DEFAULT 'MEDIUM',
    status TEXT CHECK(status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'ROLLED_OVER', 'CANCELLED')) DEFAULT 'PENDING',
    target_date TEXT NOT NULL,
    target_time TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    rollover_count INTEGER DEFAULT 0,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS cadence_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cadence_type TEXT CHECK(cadence_type IN ('DAILY', 'ALTERNATE_DAYS', 'SPECIFIC_WEEKDAYS', 'CUSTOM_INTERVAL')) NOT NULL,
    anchor_date TEXT NOT NULL,
    interval_days INTEGER DEFAULT 1,
    active_weekdays TEXT,
    action_payload TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rollover_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    from_date TEXT NOT NULL,
    to_date TEXT NOT NULL,
    rolled_at TEXT NOT NULL,
    reason TEXT DEFAULT 'UNCOMPLETED_AT_MIDNIGHT',
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS action_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    payload_before TEXT,
    payload_after TEXT,
    executed_at TEXT NOT NULL,
    is_reverted INTEGER DEFAULT 0
);
"""

class StorageEngine:
    def __init__(self, db_path: str = "daksh_core.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        is_uri = self.db_path.startswith("file:")
        conn = sqlite3.connect(self.db_path, uri=is_uri)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def insert_task(self, task_data: Dict[str, Any]) -> str:
        sql = """
        INSERT INTO tasks (id, title, category, priority, status, target_date, target_time, created_at, rollover_count, tags)
        VALUES (:id, :title, :category, :priority, :status, :target_date, :target_time, :created_at, :rollover_count, :tags)
        """
        with self._get_connection() as conn:
            conn.execute(sql, task_data)
            conn.commit()
        return task_data["id"]

    def update_task_status(self, task_id: str, new_status: str) -> bool:
        completed_at = datetime.now().isoformat() if new_status == 'COMPLETED' else None
        sql = "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?"
        with self._get_connection() as conn:
            cur = conn.execute(sql, (new_status, completed_at, task_id))
            conn.commit()
            return cur.rowcount > 0

    def get_tasks_for_date(self, target_date: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM tasks WHERE target_date = ? ORDER BY priority DESC, target_time ASC"
        with self._get_connection() as conn:
            rows = conn.execute(sql, (target_date,)).fetchall()
            return [dict(r) for r in rows]

    def get_pending_tasks_before_date(self, cut_date: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM tasks WHERE target_date < ? AND status IN ('PENDING', 'IN_PROGRESS', 'ROLLED_OVER')"
        with self._get_connection() as conn:
            rows = conn.execute(sql, (cut_date,)).fetchall()
            return [dict(r) for r in rows]

    def register_cadence(self, cadence_data: Dict[str, Any]) -> str:
        sql = """
        INSERT OR REPLACE INTO cadence_rules (id, name, cadence_type, anchor_date, interval_days, active_weekdays, action_payload, is_active, created_at)
        VALUES (:id, :name, :cadence_type, :anchor_date, :interval_days, :active_weekdays, :action_payload, :is_active, :created_at)
        """
        with self._get_connection() as conn:
            conn.execute(sql, cadence_data)
            conn.commit()
        return cadence_data["id"]

    def get_active_cadences(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM cadence_rules WHERE is_active = 1"
        with self._get_connection() as conn:
            rows = conn.execute(sql).fetchall()
            return [dict(r) for r in rows]

    def log_rollover(self, task_id: str, from_date: str, to_date: str):
        sql = """
        INSERT INTO rollover_ledger (task_id, from_date, to_date, rolled_at)
        VALUES (?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(sql, (task_id, from_date, to_date, datetime.now().isoformat()))
            conn.commit()

    def record_audit(self, action_type: str, target_entity: str, before: str, after: str):
        sql = """
        INSERT INTO action_audit_log (action_type, target_entity, payload_before, payload_after, executed_at)
        VALUES (?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            conn.execute(sql, (action_type, target_entity, before, after, datetime.now().isoformat()))
            conn.commit()
