"""
D.A.K.S.H. Tactical Brain - Tool Schemas & Parameter Validators
Subphase 3.1: Strict JSON Schema Contracts for Device and Temporal Actions
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import re

class IntentCategory(Enum):
    DEVICE_MUTATION = "DEVICE_MUTATION"
    TEMPORAL_OPERATION = "TEMPORAL_OPERATION"
    NOTIFICATION_QUERY = "NOTIFICATION_QUERY"
    STATUS_QUERY = "STATUS_QUERY"
    CONVERSATIONAL = "CONVERSATIONAL"

class ActionType(Enum):
    # Device actions
    RENAME_CONTACT = "RENAME_CONTACT"
    SEARCH_CONTACT = "SEARCH_CONTACT"
    SET_SYSTEM_ALARM = "SET_SYSTEM_ALARM"
    
    # Temporal actions
    CREATE_TASK = "CREATE_TASK"
    RESCHEDULE_TASK = "RESCHEDULE_TASK"
    MARK_TASK_COMPLETE = "MARK_TASK_COMPLETE"
    REGISTER_CADENCE = "REGISTER_CADENCE"
    ROLLOVER_TASKS = "ROLLOVER_TASKS"
    
    # Information & Status
    QUERY_AGENDA = "QUERY_AGENDA"
    QUERY_NOTIFICATIONS = "QUERY_NOTIFICATIONS"
    CHIT_CHAT = "CHIT_CHAT"

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    ActionType.RENAME_CONTACT.value: {
        "required": ["current_name", "new_name"],
        "types": {"current_name": str, "new_name": str}
    },
    ActionType.CREATE_TASK.value: {
        "required": ["title", "target_date"],
        "optional": ["target_time", "priority", "category", "tags"],
        "types": {"title": str, "target_date": str}
    },
    ActionType.RESCHEDULE_TASK.value: {
        "required": ["task_query", "new_date"],
        "optional": ["new_time"],
        "types": {"task_query": str, "new_date": str}
    },
    ActionType.REGISTER_CADENCE.value: {
        "required": ["name", "cadence_type", "anchor_date"],
        "optional": ["interval_days", "active_weekdays"],
        "types": {"name": str, "cadence_type": str, "anchor_date": str}
    }
}

class ToolValidator:
    """Validates and sanitizes parameters for execution"""
    
    @staticmethod
    def validate_action(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action not in TOOL_SCHEMAS:
            return {"valid": True, "action": action, "params": params}
            
        schema = TOOL_SCHEMAS[action]
        for req in schema.get("required", []):
            if req not in params or not params[req]:
                return {"valid": False, "error": f"Missing required parameter '{req}' for action '{action}'"}
                
        # String sanitization
        sanitized = {}
        for k, v in params.items():
            if isinstance(v, str):
                sanitized[k] = v.strip()
            else:
                sanitized[k] = v
                
        return {"valid": True, "action": action, "params": sanitized}
