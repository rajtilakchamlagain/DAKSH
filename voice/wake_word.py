"""
D.A.K.S.H. Wake-Word Detector & Streaming Speech Buffer
Subphase 4.2: Low-Latency Keyword Activation ("Hey Daksh" / "Daksh")
"""

import re
from typing import Dict, Any, Optional, Tuple

class WakeWordDetector:
    """
    Evaluates real-time audio transcript stream for wake keywords:
    - 'Daksh'
    - 'Hey Daksh'
    - 'OK Daksh'
    Strips the activation phrase and yields the remaining command payload.
    """

    WAKE_PATTERNS = [
        re.compile(r'^(?:hey|ok|hello)?\s*daksh[,!\s]*(.*)$', re.IGNORECASE),
        re.compile(r'^(?:दक्ष|हे\s*दक्ष)[,!\s]*(.*)$', re.IGNORECASE)
    ]

    @classmethod
    def evaluate_utterance(cls, transcript: str) -> Tuple[bool, str]:
        """
        Returns (is_wake_triggered, stripped_command)
        """
        cleaned = transcript.strip()
        for pattern in cls.WAKE_PATTERNS:
            match = pattern.match(cleaned)
            if match:
                payload = match.group(1).strip()
                return True, payload

        # Check if "daksh" appears anywhere as an address
        if re.search(r'\bdaksh\b', cleaned, re.IGNORECASE):
            # Extract content following or surrounding "daksh"
            payload = re.sub(r'\b(?:hey|ok|hello)?\s*daksh\b[,!\s]*', '', cleaned, flags=re.IGNORECASE).strip()
            return True, payload

        return False, cleaned
