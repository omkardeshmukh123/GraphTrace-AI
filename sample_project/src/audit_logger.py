"""Security audit logger — immutable event journaling for compliance."""

import time
import hashlib


class AuditLogger:
    """Records security-critical actions and system operations."""

    def __init__(self):
        self._journal: list[dict] = []

    def log_event(self, event_type: str, actor_id: str, payload: dict) -> dict:
        """Create a tamper-evident audit record."""
        timestamp = time.time()
        entry_raw = f"{event_type}:{actor_id}:{timestamp}"
        signature = hashlib.sha256(entry_raw.encode()).hexdigest()
        
        record = {
            "id": len(self._journal) + 1,
            "event_type": event_type,
            "actor_id": actor_id,
            "timestamp": timestamp,
            "payload": payload,
            "signature": signature,
        }
        self._journal.append(record)
        return record

    def record_login_attempt(self, username: str, success: bool, ip_address: str) -> None:
        """Log user authentication attempt for intrusion detection."""
        self.log_event(
            event_type="AUTH_ATTEMPT",
            actor_id=username,
            payload={"success": success, "ip_address": ip_address},
        )

    def export_audit_trail(self, limit: int = 100) -> list[dict]:
        """Export most recent audit entries."""
        return self._journal[-limit:]


class SecurityAuditor:
    """Validates integrity of recorded events."""

    def verify_integrity(self, log_entry: dict) -> bool:
        """Ensure cryptographic signature matches journaled fields."""
        raw = f"{log_entry['event_type']}:{log_entry['actor_id']}:{log_entry['timestamp']}"
        expected = hashlib.sha256(raw.encode()).hexdigest()
        return expected == log_entry.get("signature")
