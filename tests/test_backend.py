"""
test_backend.py
----------------
Automated verification for iptables backend functions.

Tests the following sequence:
1. List current rules
2. Add new rule (ICMP)
3. Save rules to JSON
4. Flush iptables
5. Restore from JSON
6. Validate restored rule
"""

import sys
from pathlib import Path

# Ensure the project root is importable
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.iptables_controller import (
    list_rules,
    add_rule,
    delete_rule,
    save_rules_to_json,
    load_rules_from_json,
    run_cmd,
)


def separator(title: str):
    print("\n" + "=" * 60)
    print(f"🔹 {title}")
    print("=" * 60)


def run_tests():
    # Step 1: List current rules
    separator("Step 1: Listing current rules")
    print(list_rules())

    # Step 2: Add test rule
    separator("Step 2: Adding test ICMP rule")
    print(add_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"]))

    # Step 3: Save configuration
    separator("Step 3: Saving configuration to JSON")
    save_rules_to_json()

    # Step 4: Flush rules
    separator("Step 4: Flushing rules to simulate reset")
    run_cmd(["iptables", "-F"])

    # Step 5: Validate flush
    separator("Step 5: Validating rules after flush")
    print(list_rules())

    # Step 6: Restore configuration
    separator("Step 6: Restoring configuration from JSON")
    load_rules_from_json()

    # Step 7: Verify restored rules
    separator("Step 7: Verifying restored rules (should include ICMP rule)")
    print(list_rules())

    # Step 8: Cleanup (delete ICMP rule)
    separator("Step 8: Cleanup - Deleting test ICMP rule")
    print(delete_rule("INPUT", ["-p", "icmp", "-j", "ACCEPT"]))

    separator("✅ All automated backend tests completed.")


if __name__ == "__main__":
    run_tests()
