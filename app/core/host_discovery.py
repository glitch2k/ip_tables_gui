"""
Module: host_discovery
Phase: 3
Milestone: 3
Step: 5
Purpose:
    Discover and verify reachable hosts in a subnet or host list.
    - ICMP ping check
    - Optional SSH port check (via socket)
    - Optional hostname retrieval through SSHSessionManager
"""

import ipaddress
import subprocess
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from app.core.ssh_session_manager import SSHSessionManager


def ping_host(ip: str, timeout: int = 1) -> bool:
    """Return True if ping succeeds."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_ssh_port(ip: str, port: int = 22, timeout: int = 1) -> bool:
    """Return True if TCP port 22 is open."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def discover_hosts(
    subnet: str,
    user: str,
    key_path: str,
    ssh_check: bool = True,
    fetch_hostname: bool = True,
    max_workers: int = 20,
) -> List[Dict[str, str]]:
    """
    Discover reachable SSH hosts within a subnet.

    Returns list of dicts:
        {"ip": str, "ping": bool, "ssh": bool, "hostname": str or None}
    """
    mgr = SSHSessionManager(idle_ttl_s=120)
    results = []

    ips = [str(ip) for ip in ipaddress.IPv4Network(subnet)]
    print(f"🔍 Scanning {len(ips)} IPs in {subnet}...")

    def probe(ip):
        data = {"ip": ip, "ping": False, "ssh": False, "hostname": None}
        if ping_host(ip):
            data["ping"] = True
            if ssh_check and check_ssh_port(ip):
                data["ssh"] = True
                if fetch_hostname:
                    try:
                        out = mgr.exec(ip, user, key_path, "hostname")
                        if out["status"] == "success":
                            data["hostname"] = out["stdout"]
                    except Exception:
                        pass
        return data

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(probe, ip) for ip in ips]
        for f in as_completed(futures):
            results.append(f.result())

    mgr.stop()
    reachable = [r for r in results if r["ping"] or r["ssh"]]
    print(f"✅ Discovery complete. Found {len(reachable)} reachable hosts.")
    return reachable


# ---------- Self-test ----------
if __name__ == "__main__":
    # Adjust subnet to match your Docker bridge (10.10.0.0/24)
    SUBNET = "10.10.0.0/24"
    USER = "root"
    KEY = "/home/glitch/.ssh/id_rsa"

    found = discover_hosts(SUBNET, USER, KEY)
    for entry in found:
        print(entry)
