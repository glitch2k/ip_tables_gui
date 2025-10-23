"""
Module: iptables_apply
Phase: 4
Milestone: 1
Step: 3
Purpose:
    Apply uploaded iptables ruleset on remote host using iptables-restore.
    Performs syntax check before applying to prevent lockouts.

Usage:
    python3 -m app.core.iptables_apply
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
    Apply uploaded iptables ruleset to remote host after validation.

    Args:
        host (str): Remote host IP or hostname.
        user (str): SSH username.
        key_path (str): Path to private key.
        remote_rules_path (str): Remote path to ruleset (default /tmp/iptables.rules).

    Returns:
        Dict[str, str]: JSON-style result message.
    """

    print(f"🚀 Starting iptables rule application on {host} ...")

    # Step 1: Validate before applying
    validation = validate_iptables_rules(host, user, key_path, remote_rules_path)
    if validation["status"] != "success":
        return {
            "status": "failure",
            "message": f"Syntax validation failed: {validation['message']}",
        }

    # Step 2: Apply rules
    mgr = SSHSessionManager()
    print(f"🧱 Applying iptables rules on {host} ...")

    command = f"iptables-restore < {remote_rules_path}"
    result = mgr.exec(host, user, key_path, command)
    mgr.stop()

    if result["status"] == "success":
        return {
            "status": "success",
            "message": f"iptables rules applied successfully on {host}",
        }
    else:
        return {
            "status": "failure",
            "message": f"Failed to apply ruleset: {result.get('stderr') or result.get('message')}",
        }



# ---------- Self-test ----------
if __name__ == "__main__":
    HOST = "10.10.0.20"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"
    RULES_PATH = "/tmp/iptables.rules"

    result = apply_iptables_rules(HOST, USER, KEY, RULES_PATH)
    print(result)
