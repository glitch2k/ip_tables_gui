"""
Module: remote_command_executor
Phase: 3
Milestone: 2
Step: 3
Purpose:
    Add command validation and safety controls before remote SSH execution.
    Ensures only safe and approved commands can run on target systems.
"""

import paramiko
import socket
import json
import os
from datetime import datetime
from typing import Dict

LOG_FILE = os.path.join(os.path.dirname(__file__), "../../logs/ssh_command_log.json")

# ✅ Allowed command whitelist (expandable later)
ALLOWED_COMMANDS = [
    "iptables -L",
    "iptables -S",
    "iptables -t nat -L",
    "iptables -t mangle -L",
    "iptables-save",
    "cat /etc/os-release",
    "hostname",
    "uptime"
]

def _write_log(entry: Dict[str, str]) -> None:
    """
    Append structured SSH execution logs to a JSON file.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "3",
        "milestone": "2",
        "step": "3",
        **entry
    }

    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r+") as f:
                data = json.load(f)
                data.append(log_entry)
                f.seek(0)
                json.dump(data, f, indent=4)
        else:
            with open(LOG_FILE, "w") as f:
                json.dump([log_entry], f, indent=4)
    except Exception as e:
        print(f"⚠️ Log write error: {e}")


def validate_command(command: str) -> bool:
    """
    Check if a command is allowed for remote execution.
    """
    for allowed in ALLOWED_COMMANDS:
        if command.strip().startswith(allowed):
            return True
    return False


def execute_remote_command(host: str, user: str, key_path: str, command: str, port: int = 22) -> Dict[str, str]:
    """
    Execute a validated remote command via SSH and return structured output.
    """
    # 🧩 Step 1: Validate command safety
    if not validate_command(command):
        warning = {
            "status": "rejected",
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": f"⚠️ Command '{command}' rejected — not in allowed command list."
        }
        _write_log(warning)
        return warning

    # 🧩 Step 2: Execute command over SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        ssh_client.connect(
            hostname=host,
            username=user,
            pkey=key,
            port=port,
            timeout=5
        )

        stdin, stdout, stderr = ssh_client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        result = {
            "status": "success" if exit_code == 0 else "failure",
            "exit_code": exit_code,
            "stdout": stdout.read().decode().strip(),
            "stderr": stderr.read().decode().strip(),
            "message": f"Command '{command}' executed on {host} with exit code {exit_code}."
        }

        ssh_client.close()
        _write_log(result)
        return result

    except (paramiko.AuthenticationException, paramiko.SSHException, socket.error) as e:
        error_entry = {
            "status": "failure",
            "exit_code": None,
            "stdout": "",
            "stderr": str(e),
            "message": f"Failed to execute command on {host}: {e}"
        }
        _write_log(error_entry)
        return error_entry

    except Exception as e:
        error_entry = {
            "status": "failure",
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "message": f"Unexpected error: {str(e)}"
        }
        _write_log(error_entry)
        return error_entry


if __name__ == "__main__":
    host = "10.10.0.20"
    user = "root"
    key_path = "/home/glitch/.ssh/id_rsa"

    # 🔍 Test allowed command
    print("✅ Running allowed command test...")
    result1 = execute_remote_command(host, user, key_path, "iptables -L")
    print(result1)

    # 🔒 Test rejected command
    print("\n🚫 Running disallowed command test...")
    result2 = execute_remote_command(host, user, key_path, "rm -rf /")
    print(result2)
