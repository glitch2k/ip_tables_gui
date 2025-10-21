"""
iptables_controller.py
-----------------------
This module serves as the backend control layer for managing iptables
rules from within the iptables GUI project.

Author: Sanil Tison
Phase: 2 (Core Command Layer)
Goal: Provide functions to list, add, delete, save, and restore iptables rules.
"""

import subprocess
import json
from pathlib import Path


# === GLOBAL CONFIG PATH ===
CONFIG_PATH = Path(__file__).resolve().parents[2] / "db" / "config.json"


def test_environment():
    """
    Quick test function to verify backend file and path setup.
    """
    print("✅ iptables_controller.py loaded successfully!")
    print(f"Config file path: {CONFIG_PATH}")


# === MAIN EXECUTION ENTRY POINT ===
def run_cmd(cmd: list[str]) -> str:
    """
    Executes a system command and returns its output as a string.
    Handles errors gracefully for use in backend functions.
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR] {e.stderr.strip()}"
    
def list_rules(table: str = "filter") -> str:
    """
    List all rules from a specific table (filter, nat, or mangle).
    Example:
        list_rules("nat")
    """
    cmd = ["iptables", "-t", table, "-L", "-v", "-n"]
    return run_cmd(cmd)


def add_rule(chain: str, rule_params: list[str], table: str = "filter") -> str:
    """
    Add a new rule to a chain in a given table.
    Example:
        add_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"])
    """
    cmd = ["iptables", "-t", table, "-A", chain] + rule_params
    output = run_cmd(cmd)
    return f"✅ Rule added to {table}/{chain}: {' '.join(rule_params)}\n{output}"


def delete_rule(chain: str, rule_params: list[str], table: str = "filter") -> str:
    """
    Delete a specific rule from a chain.
    Example:
        delete_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"])
    """
    cmd = ["iptables", "-t", table, "-D", chain] + rule_params
    output = run_cmd(cmd)
    return f"🗑️ Rule removed from {table}/{chain}: {' '.join(rule_params)}\n{output}"


if __name__ == "__main__":
    print("🔹 Listing existing rules...")
    print(list_rules())

    print("\n🔹 Adding test rule (allow ICMP)...")
    print(add_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"]))

    print("\n🔹 Verifying rules after addition...")
    print(list_rules())

    print("\n🔹 Deleting test rule (remove ICMP)...")
    print(delete_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"]))

    print("\n🔹 Final rule list...")
    print(list_rules())


