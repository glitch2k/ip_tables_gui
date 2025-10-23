"""
Module: test_ssh_connection
Phase: 3
Milestone: 1
Purpose:
    Implements an SSH connection testing utility for validating
    remote connectivity to Docker-based firewall or client containers.
"""

import paramiko
import socket
from typing import Dict

def test_ssh_connection(host: str, user: str, key_path: str, port: int = 22) -> Dict[str, str]:
    """
    Test SSH connectivity to a remote host using key-based authentication.

    Args:
        host (str): IP address or hostname of the target.
        user (str): Username for SSH (usually 'root').
        key_path (str): Path to private SSH key file.
        port (int): SSH port, default 22.

    Returns:
        dict: {
            "status": "success" | "failure",
            "error_type": <str>,
            "message": <str>
        }
    """
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
        ssh_client.close()
        return {
            "status": "success",
            "error_type": None,
            "message": f"SSH connection to {user}@{host}:{port} succeeded."
        }

    except paramiko.AuthenticationException:
        return {
            "status": "failure",
            "error_type": "AuthenticationError",
            "message": f"Authentication failed for {user}@{host}. Check key or permissions."
        }

    except paramiko.SSHException as e:
        return {
            "status": "failure",
            "error_type": "SSHError",
            "message": f"SSH error while connecting to {host}: {e}"
        }

    except socket.timeout:
        return {
            "status": "failure",
            "error_type": "TimeoutError",
            "message": f"Connection to {host}:{port} timed out."
        }

    except Exception as e:
        return {
            "status": "failure",
            "error_type": "GeneralError",
            "message": str(e)
        }


if __name__ == "__main__":
    # Temporary manual test harness
    host = "10.10.0.20"  # firewall container IP
    user = "root"
    key_path = "/home/glitch/.ssh/id_rsa"

    print("🔍 Testing SSH connection...\n")
    result = test_ssh_connection(host, user, key_path)
    print(result)
