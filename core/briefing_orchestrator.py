import time
from typing import Dict, Any, List, Optional
from core.persistent_daemon import PersistentStorageDaemon
from agent.on_device_engine import OnDeviceIntentEngine
from agent.persona import TacticalPersonaEngine

class TacticalLifeBriefingOrchestrator:
    """
    Phase 12: Context-Aware Tactical Life Briefing & Habit Pushback Orchestrator.
    Synthesizes incoming notifications, pending alternate-day cadences, and debts into
    a single high-density, JARVIS-style spoken & visual operational report.
    """
    def __init__(self, db_path: str = "daksh_persistent.db"):
        self.storage = PersistentStorageDaemon(db_path=db_path)
        self.intent_engine = OnDeviceIntentEngine()
        self.persona = TacticalPersonaEngine()

    def generate_briefing(self, intercepted_packets: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        debts = self.storage.get_unsettled_debts()
        cadences = self.storage.get_active_cadences()
        packets = intercepted_packets or []

        financial_debt_total = sum(d.get("amount", 0.0) for d in debts if d.get("debt_type") == "FINANCIAL")
        emotional_debts = [d for d in debts if d.get("debt_type") == "EMOTIONAL"]
        actionable_notifs = [p for p in packets if p.get("isActionable") is True]

        verbal_parts = []
        # Sentinel status
        if packets:
            verbal_parts.append(f"{len(packets)} notifications intercepted, {len(actionable_notifs)} require action.")
        else:
            verbal_parts.append("Sentinel stream clear.")

        # Cadence status
        due_cadences = [c for c in cadences if "DAILY" in c.get("cadence_type", "") or "ALTERNATE" in c.get("cadence_type", "")]
        if due_cadences:
            verbal_parts.append(f"{len(due_cadences)} operational cadences scheduled today.")

        # Debt status
        if financial_debt_total > 0 or emotional_debts:
            verbal_parts.append(f"Active financial liabilities at Rs. {int(financial_debt_total)}, with {len(emotional_debts)} personal obligations pending.")
        else:
            verbal_parts.append("Debt ledger nominal.")

        raw_script = " ".join(verbal_parts)
        styled_briefing = f"DAKSH Tactical Report: {raw_script}"

        return {
            "verbal_script": styled_briefing,
            "metrics": {
                "total_notifications": len(packets),
                "actionable_notifications": len(actionable_notifs),
                "due_cadences_count": len(due_cadences),
                "financial_debt_total": financial_debt_total,
                "emotional_obligations_count": len(emotional_debts)
            },
            "timestamp": time.time()
        }

    def evaluate_habit_deferral(self, user_statement: str, consecutive_skips: int) -> Dict[str, Any]:
        intent_data = self.intent_engine.infer(user_statement)
        if intent_data["intent"] == "SKIP_HABIT":
            habit = intent_data["entities"].get("habit", "scheduled habit")
            if consecutive_skips >= 2:
                warning = f"Sir, that marks {consecutive_skips + 1} consecutive deferrals on your {habit}. Momentum decay is accelerating. Do you wish to override discipline?"
                return {
                    "should_pushback": True,
                    "challenge_statement": warning,
                    "risk_level": "HIGH"
                }
            else:
                return {
                    "should_pushback": True,
                    "challenge_statement": f"Acknowledged. But skipping {habit} today doubles tomorrow's cognitive load.",
                    "risk_level": "MODERATE"
                }
        return {"should_pushback": False, "challenge_statement": "", "risk_level": "NOMINAL"}
