"""
D.A.K.S.H. Tactical Persona & Cinematic Briefing Engine
Subphase 3.3: Paul Bettany / Vision / JARVIS Voice Style Generator
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

class TacticalPersonaEngine:
    """
    Generates articulate, confident, terse responses adhering to the
    Paul Bettany / Vision cadence. Completely eliminates boilerplate AI phrases.
    """

    @staticmethod
    def format_contact_rename_response(current_name: str, new_name: str, success: bool, reason: str = "") -> str:
        if success:
            return f"Contact {current_name} updated to {new_name}, sir. Records synchronized."
        return f"Unable to modify contact {current_name}, sir. {reason}"

    @staticmethod
    def format_reschedule_response(task_name: str, new_date: str, new_time: Optional[str] = None) -> str:
        time_spec = f" at {new_time}" if new_time else ""
        return f"Understood, sir. Shifting {task_name} to {new_date}{time_spec}."

    @staticmethod
    def format_cadence_registration_response(cadence_name: str, cadence_type: str, next_due: str) -> str:
        if cadence_type == "ALTERNATE_DAYS":
            return f"Alternate-day rhythm locked for {cadence_name}, sir. Next execution scheduled for {next_due}."
        return f"Cadence confirmed for {cadence_name}, sir. Target locked for {next_due}."

    @staticmethod
    def format_morning_briefing(
        today_date: str,
        active_cadences: List[Dict[str, Any]],
        rolled_over_tasks: List[Dict[str, Any]],
        urgent_notifications: List[Dict[str, Any]]
    ) -> str:
        """
        Creates a structured, high-poise morning briefing script.
        """
        lines = ["Good morning, sir. Tactical overview for today:"]

        # Cadences due today
        if active_cadences:
            cadence_names = ", ".join(c["name"] for c in active_cadences)
            lines.append(f"Active cadences in effect: {cadence_names}.")

        # Rolled-over debt
        if rolled_over_tasks:
            count = len(rolled_over_tasks)
            task_titles = ", ".join(t["title"] for t in rolled_over_tasks[:2])
            suffix = f" including {task_titles}" if count <= 2 else f" including {task_titles} and {count - 2} more"
            lines.append(f"{count} backlog item{'s were' if count > 1 else ' was'} rolled forward from yesterday,{suffix}.")

        # Urgent notification context
        if urgent_notifications:
            notif_count = len(urgent_notifications)
            lines.append(f"The Sentinel has intercepted {notif_count} high-priority communication{'s' if notif_count > 1 else ''}.")

        lines.append("All subsystems standing by.")
        return " ".join(lines)
