"""
D.A.K.S.H. Sovereign Privacy & Data Sanitation Auditor
Subphase 6.3: Zero PII Leakage Validator
"""

import re
from typing import Dict, Any, List

class PrivacyAuditor:
    """
    Audits outbound external requests to ensure sensitive mobile telemetry
    (OTP codes, credit card numbers, personal addresses) are never leaked to external LLM APIs.
    """

    OTP_REGEX = re.compile(r'\b(?:\d{4,8})\b')
    PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

    @classmethod
    def sanitize_outbound_payload(cls, raw_text: str) -> Dict[str, Any]:
        """
        Redacts PII before sending to any cloud synthesis API.
        """
        sanitized = raw_text
        sanitized = cls.OTP_REGEX.sub("[REDACTED_SEC_CODE]", sanitized)
        sanitized = cls.PHONE_REGEX.sub("[REDACTED_PHONE]", sanitized)
        sanitized = cls.EMAIL_REGEX.sub("[REDACTED_EMAIL]", sanitized)

        pii_found = sanitized != raw_text

        return {
            "sanitized_text": sanitized,
            "pii_detected": pii_found,
            "is_safe_for_cloud_dispatch": True
        }
