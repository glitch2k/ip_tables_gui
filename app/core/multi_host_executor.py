"""
Module: multi_host_executor
Phase: 3
Milestone: 3
Step: 1
Purpose:
    Execute a single validated command across multiple SSH-accessible hosts in parallel.
    Builds upon remote_command_executor for agentless multi-host control.
"""

import concurrent.futures
import os
from typing import List, Dict
from app.core.remote_command_executor import execute_remote_command, validate_command


def execute_on_multiple_hosts(
    hosts: List[str],
    user: str,
    key_path: str,
    command: str,
    port: int = 22,
    max_workers: int = 3
) -> Dict[str, Dict[str, str]]:
    """
    Execute a command concurrently across multiple SSH hosts.

    Args:
        hosts (list): List of IPs or hostnames.
        user (str): SSH username.
        key_path (str): Path to private key file.
        command (str): Command to run remotely.
        port (int): SSH port (default 22).
        max_workers (int): Max parallel threads.

    Returns:
        dict: Structured results per host.
    """
    results = {}

    if not validate_command(command):
        return {
            "status": "rejected",
            "message": f"⚠️ Command '{command}' is not in the allowed command list."
        }

    print(f"🔧 Executing '{command}' on {len(hosts)} hosts...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_host = {
            executor.submit(execute_remote_command, host, user, key_path, command, port): host
            for host in hosts
        }

        for future in concurrent.futures.as_completed(future_to_host):
            host = future_to_host[future]
            try:
                result = future.result()
            except Exception as e:
                result = {
                    "status": "failure",
                    "exit_code": None,
                    "stdout": "",
                    "stderr": str(e),
                    "message": f"Error executing on {host}: {e}"
                }
            results[host] = result

    return results


if __name__ == "__main__":
    # Test configuration
    hosts = ["10.10.0.20", "10.10.0.30", "10.10.0.40"]  # firewall, client, server
    user = "root"
    key_path = "/home/glitch/.ssh/id_rsa"
    command = "hostname"

    results = execute_on_multiple_hosts(hosts, user, key_path, command)

    print("\n✅ Parallel Execution Results:\n")
    for host, output in results.items():
        print(f"[{host}] → {output['status']}")
        print(f"  Message: {output['message']}")
        if output["stdout"]:
            print(f"  Output: {output['stdout']}\n")
