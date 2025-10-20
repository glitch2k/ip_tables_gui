import os
from pathlib import Path

# Base project path
base_path = Path("/glitch/Documents/projects/iptables_gui_project")

# Directory structure
folders = [
    "app/core",
    "app/gui/tabs",
    "app/utils",
    "firewall",
    "db",
    "docs",
    "tests"
]

# Common files to initialize
files = {
    "main.py": "# Entry point for iptables GUI project\n",
    "app/__init__.py": "",
    "app/core/__init__.py": "",
    "app/gui/__init__.py": "",
    "app/utils/__init__.py": "",
    "db/config.json": "{\n  \"filter\": {},\n  \"nat\": {},\n  \"mangle\": {},\n  \"logging\": {}\n}\n",
    "docker-compose.yml": "# Docker Compose file will be created in Phase 1 setup\n",
    "firewall/Dockerfile": "# Dockerfile will be added in Phase 1 setup\n",
    "docs/README.md": "# Documentation for iptables GUI project\n",
    "tests/test_backend.py": "# Placeholder for backend MVP tests\n"
}

# Create directories
print(f"📁 Creating project at: {base_path}\n")
for folder in folders:
    dir_path = base_path / folder
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created folder: {dir_path}")

# Create files
print("\n📝 Creating starter files...")
for file_path, content in files.items():
    full_path = base_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)
    print(f"✅ Created file: {full_path}")

# Summary
print("\n🎉 Project structure successfully created!")
print(f"Navigate to: {base_path}")
print("Next step: Add your docker-compose.yml and firewall/Dockerfile to begin Phase 1 setup.")
