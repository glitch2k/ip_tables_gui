#!/usr/bin/env python3
"""
Main Flask entrypoint for the iptables GUI project.
Serves the web interface and exposes backend API routes.
"""

from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder="app/web")

# --- Base route: serve the frontend page ---
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# --- Test route: backend status check ---
@app.route("/api/status")
def api_status():
    return jsonify({
        "project": "iptables_gui",
        "status": "running",
        "phase": "5",
        "milestone": "1",
        "step": "1"
    })

if __name__ == "__main__":
    print("🚀 Starting iptables GUI backend...")
    app.run(host="0.0.0.0", port=5000, debug=True)
