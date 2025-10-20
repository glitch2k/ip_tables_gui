# 🧭 Phase 1 – Environment Setup (Docker Edition)
**Goal:** Build a reproducible, isolated Docker-based environment for the iptables GUI backend MVP.

---

## ✅ Phase Overview
This phase prepares your environment to:
- Develop and test the backend safely inside Docker containers.
- Simulate real packet flows (client → firewall → server).
- Capture and analyze network behavior without affecting your host.

---

## 🧱 Step 1: Prepare Your Local Machine
- [ ] **Install Docker**
  ```bash
  sudo apt update
  sudo apt install docker.io docker-compose
  sudo systemctl enable docker
  sudo systemctl start docker
