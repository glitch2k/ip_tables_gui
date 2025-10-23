"""
Module: iptables_validate
Phase: 4
Milestone: 1
Step: 2
Purpose:
    Validate uploaded iptables ruleset syntax on a remote host
    using `iptables-restore --test`.

Usage:
    python3 -m app.core.iptables_validate
"""

from __future__ import annotations
from typing import Dict
from app.core.ssh_session_manager import SSHSessionManager


def validate_iptables_rules(
    host: str,
    user: str,
    key_path: str,
    remote_rules_path: str = "/tmp/iptables.rules"
) -> Dict[str, str]:
    """
    Run iptables syntax validation remotely.

    Args:
        host (str): Remote host IP or hostname.
        user (str): SSH username.
        key_path (str): Path to private key.
        remote_rules_path (str): Path to uploaded rules file.

    Returns:
        Dict[str, str]: JSON-like result indicating validation status.
    """
    mgr = SSHSessionManager()
    print(f"🧠 Validating iptables syntax on {host} ...")

    # Test syntax without applying
    command = f"iptables-restore --test {remote_rules_path}"
    result = mgr.exec(host, user, key_path, command)

    mgr.stop()

    if result["status"] == "success":
        return {
            "status": "success",
            "message": f"Syntax OK for {remote_rules_path} on {host}",
        }
    else:
        return {
            "status": "failure",
            "message": f"Syntax error in ruleset: {result.get('stderr') or result.get('message')}",
        }


# ---------- Self-test ----------
if __name__ == "__main__":
    HOST = "10.10.0.20"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"
    RULES_PATH = "/tmp/iptables.rules"

    validation_result = validate_iptables_rules(HOST, USER, KEY, RULES_PATH)
    print(validation_result)
