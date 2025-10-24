"""
Module: iptables_push
Phase: 4
Milestone: 1
Step: 1 (with KB logging)
Purpose:
    Upload iptables ruleset file to remote host via SSH using SFTP,
    and log the action to the Knowledge Base.
"""

from __future__ import annotations
import os
from typing import Dict
from app.core.ssh_file_transfer import SSHFileTransfer
from app.core.ssh_session_manager import SSHSessionManager
from app.core.iptables_logger import log_kb_entry


def push_iptables_ruleset(
    host: str,
    user: str,
    key_path: str,
    local_rules_path: str,
    remote_rules_path: str = "/tmp/iptables.rules"
) -> Dict[str, str]:
    """
    Upload iptables ruleset to remote host and log the result.
    """
    mgr = SSHSessionManager()
    xfer = SSHFileTransfer(mgr)

    if not os.path.exists(local_rules_path):
        result = {
            "status": "failure",
            "message": f"Local ruleset not found: {local_rules_path}",
        }
        log_kb_entry("push", host, result)
        return result

    print(f"📤 Uploading iptables ruleset to {host} ...")
    result = xfer.upload(
        host=host,
        user=user,
        key_path=key_path,
        local_path=local_rules_path,
        remote_path=remote_rules_path,
    )

    log_kb_entry("push", host, result)
    mgr.stop()
    return result


# ---------- Self-test ----------
if __name__ == "__main__":
    HOST = "10.10.0.20"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"
    LOCAL_FILE = "./iptables.rules"

    # Create a sample ruleset for testing
    with open(LOCAL_FILE, "w") as f:
        f.write("*filter\n-A INPUT -p icmp -j ACCEPT\nCOMMIT\n")

    response = push_iptables_ruleset(HOST, USER, KEY, LOCAL_FILE)
    print(response)
