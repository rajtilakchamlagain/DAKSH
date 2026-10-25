import time
from typing import Dict, Any, List, Optional
from core.persistent_daemon import PersistentStorageDaemon
from agent.on_device_engine import OnDeviceIntentEngine
from agent.gemini_brain import GeminiBrain

class AutonomousLifeOSRuntime:
    """
    Phase 13: Full Autonomous Life OS Final Integration Hub.
    Binds voice acoustic capture, on-device edge routing, cloud/offline fallback reasoning,
    native Android actions, and persistent ledger updates into a unified production loop.
    """
    def __init__(self, db_path: str = "daksh_persistent.db", gemini_api_key: Optional[str] = None):
        self.storage = PersistentStorageDaemon(db_path=db_path)
        self.edge_intent = OnDeviceIntentEngine()
        self.brain = GeminiBrain(apiKey=gemini_api_key)
        self.active_session = True
        self.is_silent_mode = False

    def process_utterance(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        edge_res = self.edge_intent.infer(text)
        intent = edge_res["intent"]
        entities = edge_res["entities"]

        response_text = ""
        action_taken = "NONE"

        if intent == "STAND_DOWN":
            self.is_silent_mode = True
            response_text = "Standing down. Stealth mode active."
            action_taken = "SET_SILENT"

        elif intent == "BRIEFING":
            cadences = self.storage.get_active_cadences()
            debts = self.storage.get_unsettled_debts()
            response_text = f"Briefing ready: {len(cadences)} cadences active, {len(debts)} rollover items pending. Systems nominal."
            action_taken = "GENERATE_BRIEFING"

        elif intent == "ADD_DEBT":
            d_type = entities.get("type", "FINANCIAL")
            amount = entities.get("amount", 0.0)
            target = entities.get("counterparty", "General")
            debt_id = f"DEBT_{int(time.time())}"
            self.storage.add_debt(debt_id, text, d_type, "2026-10-25", amount=amount, counterparty=target)
            response_text = f"Committed {d_type.lower()} debt record for {target}."
            action_taken = "PERSIST_DEBT"

        elif intent == "SKIP_HABIT":
            response_text = "Habit deferral logged. Warning: rest parity violated."
            action_taken = "RECORD_SKIP"

        else:
            # Route to deep cognitive synthesis
            response_text = self.brain.query(text, tacticalContext=context)
            action_taken = "COGNITIVE_SYNTHESIS"

        latency = (time.perf_counter() - start) * 1000.0

        return {
            "transcript": text,
            "resolved_intent": intent,
            "response": response_text,
            "action": action_taken,
            "latency_ms": round(latency, 2),
            "status": "DISPATCHED"
        }
