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
