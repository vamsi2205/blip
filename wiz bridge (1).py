"""
Blip's WiZ light bridge.

Browsers can't send raw UDP packets, so this tiny server runs on your
always-on laptop (same one running Ollama) and does it on Blip's behalf.
Blip calls this over HTTP; this translates that into the real local UDP
protocol WiZ bulbs speak.

Setup:
    pip install flask flask-cors pywizlight --break-system-packages
    python wiz_bridge.py

Then expose it the same way you did Ollama:
    tailscale funnel --bg --https=8443 http://localhost:5005

That gives you a second URL like https://kv.tail1b8abe.ts.net:8443 —
put that into Blip's settings as the "Light bridge URL".
"""

import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from pywizlight import wizlight, PilotBuilder, discovery

app = Flask(__name__)
CORS(app)  # allow Blip's browser origin to call this


def run_async(coro):
    return asyncio.run(coro)


@app.route("/light/command", methods=["POST"])
def light_command():
    data = request.get_json(force=True) or {}
    ip = data.get("ip")
    action = data.get("action")

    if not ip:
        return jsonify({"error": "missing 'ip'"}), 400

    bulb = wizlight(ip)
    try:
        if action == "on":
            run_async(bulb.turn_on(PilotBuilder()))
        elif action == "off":
            run_async(bulb.turn_off())
        elif action == "brightness":
            value = max(1, min(100, int(data.get("value", 100))))
            run_async(bulb.turn_on(PilotBuilder(brightness=int(value * 2.55))))
        elif action == "color":
            r = int(data.get("r", 255))
            g = int(data.get("g", 255))
            b = int(data.get("b", 255))
            run_async(bulb.turn_on(PilotBuilder(rgb=(r, g, b))))
        elif action == "warm":
            run_async(bulb.turn_on(PilotBuilder(colortemp=2700)))
        elif action == "cool":
            run_async(bulb.turn_on(PilotBuilder(colortemp=6500)))
        else:
            return jsonify({"error": f"unknown action '{action}'"}), 400
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/light/discover", methods=["GET"])
def light_discover():
    """One-off helper: run this once to find your bulb's IP on the network.
    Visit http://localhost:5005/light/discover in a laptop browser, or
    curl it, while on the same WiFi as the bulb."""
    try:
        bulbs = run_async(discovery.find_wizlights())
        return jsonify({"bulbs": [{"ip": b.ip} for b in bulbs]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health():
    return "WiZ bridge is running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
