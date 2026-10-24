"""
D.A.K.S.H. Modulo Arithmetic Cadence & Temporal Rhythm Engine
Subphase 1.2: Deterministic Alternating Days & Periodic Schedules
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

class TemporalCadenceEngine:
    """
    Computes mathematical parity and cadence matching for tasks.
    Guarantees that alternate-day tasks (e.g. shampoo, workout splits)
    maintain an immutable invariant even across month/leap year boundaries.
    """

    @staticmethod
    def parse_date(date_str: str) -> date:
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    @staticmethod
    def format_date(d: date) -> str:
        return d.strftime("%Y-%m-%d")

    @classmethod
    def is_cadence_due_on(cls, cadence: Dict[str, Any], query_date: date) -> bool:
        """
        Determines if a given cadence rule triggers on query_date.
        """
        if not cadence.get("is_active", 1):
            return False

        cadence_type = cadence["cadence_type"]
        anchor_date = cls.parse_date(cadence["anchor_date"])

        # Cannot trigger before anchor date
        if query_date < anchor_date:
            return False

        delta_days = (query_date - anchor_date).days

        if cadence_type == "DAILY":
            return True

        elif cadence_type == "ALTERNATE_DAYS":
            # Parity modulo arithmetic: delta % 2 == 0
            return (delta_days % 2) == 0

        elif cadence_type == "CUSTOM_INTERVAL":
            interval = cadence.get("interval_days", 1)
            if interval <= 0:
                interval = 1
            return (delta_days % interval) == 0

        elif cadence_type == "SPECIFIC_WEEKDAYS":
            # active_weekdays is comma-separated: 'MON,WED,FRI' or '0,2,4' (0=Monday in Python)
            weekday_str = str(query_date.weekday()) # 0=Mon, 6=Sun
            day_name = query_date.strftime("%a").upper() # 'MON', 'TUE'
            allowed = [w.strip().upper() for w in str(cadence.get("active_weekdays", "")).split(",")]
            return (weekday_str in allowed) or (day_name in allowed)

        return False

    @classmethod
    def get_due_cadences_for_date(cls, cadences: List[Dict[str, Any]], query_date_str: str) -> List[Dict[str, Any]]:
        q_date = cls.parse_date(query_date_str)
        due = []
        for cad in cadences:
            if cls.is_cadence_due_on(cad, q_date):
                due.append(cad)
        return due

    @classmethod
    def calculate_next_due_date(cls, cadence: Dict[str, Any], start_date_str: str) -> str:
        """Finds the next upcoming date on which this cadence fires."""
        curr = cls.parse_date(start_date_str)
        # Search forward up to 365 days
        for step in range(1, 366):
            candidate = curr + timedelta(days=step)
            if cls.is_cadence_due_on(cadence, candidate):
                return cls.format_date(candidate)
        return cls.format_date(curr + timedelta(days=1))
