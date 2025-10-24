"""
Module: iptables_apply
Phase: 4
Milestone: 1
Step: 3 (with KB logging)
Purpose:
    Apply uploaded iptables ruleset on remote host using iptables-restore,
    perform validation first, and log the outcome.
"""

from __future__ import annotations
from typing import Dict
from app.core.iptables_validate import validate_iptables_rules
from app.core.ssh_session_manager import SSHSessionManager
from app.core.iptables_logger import log_kb_entry


def apply_iptables_rules(
    host: str,
    user: str,
    key_path: str,
    remote_rules_path: str = "/tmp/iptables.rules"
) -> Dict[str, str]:
    """
    Apply uploaded iptables ruleset to remote host and log the result.
    """
    print(f"🚀 Starting iptables rule application on {host} ...")

    # Step 1: Validate before applying
    validation = validate_iptables_rules(host, user, key_path, remote_rules_path)
    if validation["status"] != "success":
        result = {
            "status": "failure",
            "message": f"Syntax validation failed: {validation['message']}",
        }
        log_kb_entry("apply", host, result)
        return result

    # Step 2: Apply rules
    mgr = SSHSessionManager()
    print(f"🧱 Applying iptables rules on {host} ...")
    command = f"iptables-restore < {remote_rules_path}"
    result = mgr.exec(host, user, key_path, command)
    mgr.stop()

    if result["status"] == "success":
        final = {
            "status": "success",
            "message": f"iptables rules applied successfully on {host}",
        }
    else:
        final = {
            "status": "failure",
            "message": f"Failed to apply ruleset: {result.get('stderr') or result.get('message')}",
        }

    log_kb_entry("apply", host, final)
    return final


# ---------- Self-test ----------
if __name__ == "__main__":
    HOST = "10.10.0.20"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"
    RULES_PATH = "/tmp/iptables.rules"

    result = apply_iptables_rules(HOST, USER, KEY, RULES_PATH)
    print(result)
