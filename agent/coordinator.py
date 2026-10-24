"""
D.A.K.S.H. Multi-Agent Coordinator & Orchestrator
Subphase 3.4: Unified Brain Pipeline
"""

from typing import Dict, Any, List, Optional
from datetime import date
from .router import TacticalRouter
from .schemas import ActionType, IntentCategory
from .persona import TacticalPersonaEngine
from core.storage import StorageEngine
from core.cadence import TemporalCadenceEngine
from core.rollover import RolloverDaemon

class DakshBrainCoordinator:
    """
    Coordinates Tactical Routing, Core Database, Cadence Engine, and Persona Synthesis.
    Outputs validated execution payloads directly matching DakshNativeBridge and Storage APIs.
    """

    def __init__(self, storage: StorageEngine, reference_date: Optional[date] = None):
        self.storage = storage
        self.ref_date = reference_date or date.today()
        self.router = TacticalRouter(self.ref_date)
        self.persona = TacticalPersonaEngine()
        self.rollover_daemon = RolloverDaemon(self.storage)

    def process_voice_command(self, voice_input: str) -> Dict[str, Any]:
        """
        Processes spoken text into structured intent, dispatches core or native actions,
        and returns the cinematic spoken response.
        """
        route = self.router.route_intent(voice_input)
        action = route["action"]
        params = route["params"]

        spoken_reply = ""
        dispatch_payload = {}

        if action == ActionType.RENAME_CONTACT.value:
            # Prepare native Android mutation payload
            dispatch_payload = {
                "target": "NATIVE_BRIDGE",
                "method": "renameContact",
                "args": {
                    "currentName": params["current_name"],
                    "newName": params["new_name"]
                }
            }
            # Optimistic or simulated verbal confirmation
            spoken_reply = self.persona.format_contact_rename_response(
                params["current_name"], params["new_name"], success=True
            )

        elif action == ActionType.RESCHEDULE_TASK.value:
            # Reschedule in storage
            task_query = params["task_query"]
            new_date = params["new_date"]
            new_time = params.get("new_time")

            dispatch_payload = {
                "target": "STORAGE",
                "action": "RESCHEDULE_TASK",
                "task_query": task_query,
                "new_date": new_date,
                "new_time": new_time
            }
            spoken_reply = self.persona.format_reschedule_response(
                task_query, new_date, new_time
            )

        elif action == ActionType.REGISTER_CADENCE.value:
            cadence_id = f"CAD_{abs(hash(params['name'])) % 100000}"
            cadence_data = {
                "id": cadence_id,
                "name": params["name"],
                "cadence_type": params["cadence_type"],
                "anchor_date": params["anchor_date"],
                "interval_days": params.get("interval_days", 1),
                "active_weekdays": params.get("active_weekdays", ""),
                "action_payload": "",
                "is_active": 1,
                "created_at": self.ref_date.isoformat()
            }
            self.storage.register_cadence(cadence_data)
            next_due = TemporalCadenceEngine.calculate_next_due_date(
                cadence_data, self.ref_date.strftime("%Y-%m-%d")
            )
            dispatch_payload = {"target": "STORAGE", "action": "REGISTER_CADENCE", "id": cadence_id}
            spoken_reply = self.persona.format_cadence_registration_response(
                params["name"], params["cadence_type"], next_due
            )

        elif action == ActionType.QUERY_AGENDA.value:
            today_str = self.ref_date.strftime("%Y-%m-%d")
            cadences = self.storage.get_active_cadences()
            due_cadences = TemporalCadenceEngine.get_due_cadences_for_date(cadences, today_str)
            rolled_tasks = [t for t in self.storage.get_tasks_for_date(today_str) if t.get("status") == "ROLLED_OVER"]

            spoken_reply = self.persona.format_morning_briefing(
                today_date=today_str,
                active_cadences=due_cadences,
                rolled_over_tasks=rolled_tasks,
                urgent_notifications=[]
            )
            dispatch_payload = {"target": "UI_UPDATE", "agenda_date": today_str}

        else:
            spoken_reply = f"Standing by, sir. Awaiting instructions for '{voice_input}'."
            dispatch_payload = {"target": "NO_OP"}

        return {
            "intent": route,
            "spoken_response": spoken_reply,
            "dispatch_payload": dispatch_payload
        }
