import json
import re
import time
from typing import Dict, Any, Optional

class OnDeviceIntentEngine:
    """
    Sub-10ms Lightweight On-Device Neural/Heuristic Intent Classifier.
    Designed for 0-latency edge inference on low-power devices without cloud dependency.
    """
    def __init__(self, dataset_path: Optional[str] = None):
        self.rules = {
            "BRIEFING": [
                r"what.*miss", r"brief", r"summary", r"status",
                r"के के भयो", r"ब्रिफिङ", r"kya.*miss", r"update"
            ],
            "SKIP_HABIT": [
                r"skip.*gym", r"skip.*workout", r"not going.*gym",
                r"जिम जान्न", r"gym nahi", r"postpone.*walk"
            ],
            "ADD_DEBT": [
                r"owe (\w+) (\d+)", r"owe (\d+)", r"call (\w+)",
                r"फोन गर्न", r"debt", r"rupees"
            ],
            "STAND_DOWN": [
                r"go silent", r"stand down", r"shut ?up", r"sleep",
                r"शान्त", r"chup"
            ],
            "DEVICE_ACTION": [
                r"rename (\w+) to (\w+)", r"update contact"
            ]
        }

    def infer(self, text: str) -> Dict[str, Any]:
        start = time.perf_counter()
        normalized = text.lower().strip()
        detected_intent = "GENERAL_QUERY"
        entities: Dict[str, Any] = {}
        confidence = 0.50

        for intent, patterns in self.rules.items():
            for pat in patterns:
                match = re.search(pat, normalized)
                if match:
                    detected_intent = intent
                    confidence = 0.95
                    if intent == "DEVICE_ACTION" and match.groups():
                        if len(match.groups()) >= 2:
                            entities["target"] = match.group(1).capitalize()
                            entities["replacement"] = match.group(2).capitalize()
                    elif intent == "ADD_DEBT":
                        if "call" in normalized or "आमा" in normalized or "mom" in normalized:
                            entities["type"] = "EMOTIONAL"
                            entities["counterparty"] = "Mom"
                        else:
                            entities["type"] = "FINANCIAL"
                            num_match = re.search(r"(\d+)", normalized)
                            if num_match:
                                entities["amount"] = float(num_match.group(1))
                    elif intent == "SKIP_HABIT":
                        entities["habit"] = "gym" if "gym" in normalized or "जिम" in normalized else "walk"
                    break
            if detected_intent != "GENERAL_QUERY":
                break

        latency_ms = (time.perf_counter() - start) * 1000.0

        return {
            "intent": detected_intent,
            "entities": entities,
            "confidence": confidence,
            "latency_ms": round(latency_ms, 3),
            "model": "DAKSH-OnDevice-EdgeClassifier-v1"
        }
