"""
D.A.K.S.H. In-Process Reactive Event Bus
Subphase 1.4: Real-Time Signal Distribution
"""

import threading
from typing import Callable, Dict, List, Any
from enum import Enum

class DakshEventType(Enum):
    VOICE_INTENT_TRIGGERED = "VOICE_INTENT_TRIGGERED"
    TASK_STATE_CHANGED = "TASK_STATE_CHANGED"
    NOTIFICATION_INGESTED = "NOTIFICATION_INGESTED"
    DEVICE_ACTION_COMMITTED = "DEVICE_ACTION_COMMITTED"
    ROLLOVER_EXECUTED = "ROLLOVER_EXECUTED"
    CADENCE_TRIGGERED = "CADENCE_TRIGGERED"
    SYSTEM_ALERT = "SYSTEM_ALERT"

class EventBus:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
                cls._instance._sub_lock = threading.Lock()
        return cls._instance

    def subscribe(self, event_type: DakshEventType, handler: Callable[[Dict[str, Any]], None]):
        with self._sub_lock:
            key = event_type.value
            if key not in self._subscribers:
                self._subscribers[key] = []
            self._subscribers[key].append(handler)

    def publish(self, event_type: DakshEventType, payload: Dict[str, Any]):
        key = event_type.value
        with self._sub_lock:
            handlers = list(self._subscribers.get(key, []))

        for h in handlers:
            try:
                h(payload)
            except Exception as e:
                print(f"[EVENT_BUS_ERROR] Exception in handler for {key}: {e}")

    def clear(self):
        with self._sub_lock:
            self._subscribers.clear()
