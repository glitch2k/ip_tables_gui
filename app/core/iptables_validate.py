"""
Module: iptables_validate
Phase: 4
Milestone: 1
Step: 2 (with KB logging)
Purpose:
    Validate uploaded iptables ruleset syntax on a remote host
    using `iptables-restore --test`, and log the results.
"""

from __future__ import annotations
from typing import Dict
from app.core.ssh_session_manager import SSHSessionManager
from app.core.iptables_logger import log_kb_entry


def validate_iptables_rules(
    host: str,
    user: str,
    key_path: str,
    remote_rules_path: str = "/tmp/iptables.rules"
) -> Dict[str, str]:
    """
    Run iptables syntax validation remotely and log the result.
    """
    mgr = SSHSessionManager()
    print(f"🧠 Validating iptables syntax on {host} ...")

    command = f"iptables-restore --test {remote_rules_path}"
    result = mgr.exec(host, user, key_path, command)
    mgr.stop()

    if result["status"] == "success":
        final = {
            "status": "success",
            "message": f"Syntax OK for {remote_rules_path} on {host}",
        }
    else:
        final = {
            "status": "failure",
            "message": f"Syntax error in ruleset: {result.get('stderr') or result.get('message')}",
        }

    log_kb_entry("validate", host, final)
    return final


# ---------- Self-test ----------
if __name__ == "__main__":
    HOST = "10.10.0.20"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"
    RULES_PATH = "/tmp/iptables.rules"

    validation_result = validate_iptables_rules(HOST, USER, KEY, RULES_PATH)
    print(validation_result)
