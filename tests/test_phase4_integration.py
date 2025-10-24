"""
Integration Test: Phase 4 (Push → Validate → Apply → Log)
This verifies that all iptables modules work together correctly.
"""

import os
import json
from app.core.iptables_push import push_iptables_ruleset
from app.core.iptables_validate import validate_iptables_rules
from app.core.iptables_apply import apply_iptables_rules

LOG_FILE = "logs/kb/iptables_kb.jsonl"


def read_last_log_entry():
    """Return the last KB log entry (if any)."""
    if not os.path.exists(LOG_FILE):
        return None
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    return json.loads(lines[-1]) if lines else None


def run_integration_test():
    # Define test environment
    host = "10.10.0.20"
    user = "root"
    key = "/home/glitch/.ssh/id_rsa"
    local_file = "./iptables.rules"

    print("\n🧪 Starting Phase 4 Integration Test...\n")

    # Step 1: Create a test ruleset
    with open(local_file, "w") as f:
        f.write("*filter\n-A INPUT -p tcp --dport 22 -j ACCEPT\nCOMMIT\n")
    print(f"✅ Created local ruleset: {local_file}")

    # Step 2: Push ruleset
    result_push = push_iptables_ruleset(host, user, key, local_file)
    print(f"📤 Push Result: {result_push}\n")

    # Step 3: Validate syntax
    result_validate = validate_iptables_rules(host, user, key)
    print(f"🧠 Validation Result: {result_validate}\n")

    # Step 4: Apply ruleset
    result_apply = apply_iptables_rules(host, user, key)
    print(f"🚀 Apply Result: {result_apply}\n")

    # Step 5: Confirm KB log entry
    last_log = read_last_log_entry()
    if last_log:
        print("🧾 Last KB Log Entry:")
        print(json.dumps(last_log, indent=4))
    else:
        print("⚠️ No log entries found.")

    print("\n✅ Integration test completed.\n")


if __name__ == "__main__":
    run_integration_test()
