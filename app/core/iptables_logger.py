"""
Module: iptables_logger
Phase: 4
Milestone: 1
Step: 4
Purpose:
    Record all iptables management events (push, validate, apply)
    into a central JSON-based Knowledge Base (KB) log file.
"""

import os, json, datetime
from typing import Dict

LOG_DIR = "logs/kb"
LOG_FILE = os.path.join(LOG_DIR, "iptables_kb.jsonl")


def log_kb_entry(action: str, host: str, result: Dict[str, str]):
    """
    Append a structured entry to the KB log.

    Args:
        action (str): Type of operation (push, validate, apply)
        host (str): Target host
        result (dict): Result dictionary from the step
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "action": action,
        "host": host,
        "status": result.get("status"),
        "message": result.get("message"),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"🧾 Logged {action} result for {host}: {entry['status']}")


# ---------- Self-test ----------
if __name__ == "__main__":
    sample_result = {
        "status": "success",
        "message": "iptables rules applied successfully on 10.10.0.20",
    }
    log_kb_entry("apply", "10.10.0.20", sample_result)
