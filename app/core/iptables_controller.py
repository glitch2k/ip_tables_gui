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

def save_rules_to_json() -> None:
    """
    Export all iptables rules (filter, nat, mangle) to a JSON file.
    The output of 'iptables-save' for each table is stored under db/config.json.
    """
    tables = ["filter", "nat", "mangle"]
    data = {}

    for table in tables:
        print(f"💾 Saving table: {table} ...")
        result = run_cmd(["iptables-save", "-t", table])
        data[table] = result

    CONFIG_PATH.write_text(json.dumps(data, indent=2))
    print(f"✅ All tables saved to {CONFIG_PATH}")


def load_rules_from_json() -> None:
    """
    Restore iptables rules from db/config.json using 'iptables-restore'.
    Each table's ruleset is loaded back into the kernel.
    """
    if not CONFIG_PATH.exists():
        print("⚠️ No saved configuration found!")
        return

    print(f"📂 Loading rules from {CONFIG_PATH} ...")
    data = json.loads(CONFIG_PATH.read_text())

    for table, ruleset in data.items():
        print(f"🔄 Restoring table: {table} ...")
        process = subprocess.run(["iptables-restore"], input=ruleset, text=True)
        if process.returncode == 0:
            print(f"✅ Successfully restored {table} table")
        else:
            print(f"❌ Failed to restore {table} table")

    print("🎯 Firewall configuration restored from JSON")



if __name__ == "__main__":
    print("\n🔹 Adding a test rule (ICMP)...")
    print(add_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"]))

    print("\n💾 Saving current rules to JSON...")
    save_rules_to_json()

    print("\n🗑️ Flushing all rules to simulate a reset...")
    run_cmd(["iptables", "-F"])

    print("\n🔍 Rules after flush (should be empty):")
    print(list_rules())

    print("\n📂 Restoring rules from JSON...")
    load_rules_from_json()

    print("\n✅ Rules after restore (should show ICMP rule again):")
    print(list_rules())


