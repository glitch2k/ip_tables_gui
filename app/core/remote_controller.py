"""
remote_controller.py
--------------------
Handles agentless SSH connectivity for remote firewall management.
"""

import paramiko
from pathlib import Path
import json
import os

def test_ssh_connection(host: str, username: str, key_path: str, port: int = 22):
    """Test SSH connectivity to a remote firewall using a private key."""
    try:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=username, pkey=key, port=port, timeout=10)
        print(f"✅ SSH connection successful: {username}@{host}")
        ssh_client.close()
        return {"status": "success", "host": host}
    except Exception as e:
        print(f"❌ SSH connection failed: {str(e)}")
        return {"status": "failed", "error": str(e)}
