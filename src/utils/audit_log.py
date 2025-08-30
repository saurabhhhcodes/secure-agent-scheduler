import os
import json
from datetime import datetime
from typing import List, Dict, Any

AUDIT_LOG_PATH = os.getenv("AUDIT_LOG_PATH", "audit.log")

def log_action(action: str, details: Dict[str, Any]):
    """Append an action and its details to the audit log."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details
    }
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_audit_log(limit: int = 100) -> List[Dict[str, Any]]:
    """Read the last N entries from the audit log."""
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    with open(AUDIT_LOG_PATH, "r") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(line.strip()) for line in lines if line.strip()]

