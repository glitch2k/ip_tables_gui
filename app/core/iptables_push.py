"""
Module: iptables_push
Phase: 4
Milestone: 1
Step: 1
Purpose:
    Upload iptables ruleset file to remote host via SSH using SFTP.
    Prepares for later validation and apply stages.

Usage:
    python3 -m app.core.iptables_push
"""

from __future__ import annotations
import os
from typing import Dict
from app.core.ssh_file_transfer import SSHFileTransfer
from app.core.ssh_session_manager import SSHSessionManager


def push_iptables_ruleset(
    host: str,
    user: str,
    key_path: str,
    local_rules_path: str,
    remote_rules_path: str = "/tmp/iptables.rules"
) -> Dict[str, str]:
    """
    Upload iptables ruleset to remote host.

    Args:
        host (str): Remote host IP or hostname.
        user (str): SSH username.
        key_path (str): Path to private key file.
        local_rules_path (str): Path to local rules file (e.g., ./iptables.rules).
        remote_rules_path (str): Destination on remote host (default /tmp/iptables.rules).

    Returns:
        Dict[str, str]: JSON-style result message.
    """
    mgr = SSHSessionManager()
    xfer = SSHFileTransfer(mgr)

    if not os.path.exists(local_rules_path):
        return {
            "status": "failure",
            "message": f"Local ruleset not found: {local_rules_path}",
        }

    print(f"📤 Uploading iptables ruleset to {host} ...")

    result = xfer.upload(
        host=host,
        user=user,
        key_path=key_path,
        local_path=local_rules_path,
        remote_path=remote_rules_path,
    )

    mgr.stop()
    return result


# ---------- Self-test ----------
if __name__ == "__main__":
    HOST = "10.10.0.20"  # firewall container
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"
    LOCAL_FILE = "./iptables.rules"

    # Create a sample ruleset for testing
    with open(LOCAL_FILE, "w") as f:
        f.write("*filter\n-A INPUT -p icmp -j ACCEPT\nCOMMIT\n")

    response = push_iptables_ruleset(HOST, USER, KEY, LOCAL_FILE)
    print(response)
