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

@app.route("/api/objective", methods=["POST"])
def api_objective():
    """
    Temporary route to test Objective Selection from frontend.
    """
    data = request.get_json(force=True, silent=False)
    return jsonify({
        "status": "received",
        "objective": data.get("objective"),
        "action": data.get("action")
    })

if __name__ == "__main__":
    print("🚀 Starting iptables GUI backend...")
    app.run(host="0.0.0.0", port=5000, debug=True)
