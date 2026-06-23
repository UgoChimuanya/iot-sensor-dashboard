"""
app.py  —  Arduino IoT Sensor Monitor Dashboard
Simulates a real-time multi-channel sensor monitoring system as you would
build with an Arduino + Python serial bridge. Streams live data via
Server-Sent Events (SSE) to a web dashboard without any extra dependencies.
"""

import time, math, random, json, threading
from flask import Flask, render_template, Response, jsonify

app  = Flask(__name__)

# ── Shared sensor state (updated by background thread) ───────────────────────
_state = {
    "tick":        0,
    "voltage":     12.0,
    "current":     2.5,
    "temperature": 35.0,
    "humidity":    60.0,
    "vibration":   50.0,
    "status":      "NORMAL",   # NORMAL | WARNING | CRITICAL
    "alerts":      [],
    "history": {k: [] for k in ["voltage","current","temperature","humidity","vibration"]},
}
_lock = threading.Lock()
MAX_HISTORY = 60   # keep last 60 ticks (~60 seconds)

THRESHOLDS = {
    "voltage":     (9.0,  15.0),
    "current":     (0.5,  6.0),
    "temperature": (10.0, 65.0),
    "humidity":    (20.0, 90.0),
    "vibration":   (20.0, 80.0),
}


def simulate_sensor(tick):
    """Produce realistic-looking sensor readings with occasional fault injection."""
    t  = tick * 0.1
    fault = (tick % 120) in range(80, 95)   # inject a fault every 120 ticks

    v    = 12.0 + math.sin(t * 0.7) * 0.4  + random.gauss(0, 0.05)
    i    = 2.5  + math.sin(t * 1.1) * 0.3  + random.gauss(0, 0.03)
    temp = 35.0 + math.sin(t * 0.3) * 4.0  + random.gauss(0, 0.3)
    hum  = 60.0 + math.sin(t * 0.5) * 8.0  + random.gauss(0, 0.5)
    vib  = 50.0 + math.sin(t * 2.0) * 6.0  + random.gauss(0, 1.0)

    if fault:
        temp += random.uniform(25, 35)   # overheat spike
        v    -= random.uniform(2, 4)     # voltage sag
        i    += random.uniform(2, 4)     # current surge

    return round(v,2), round(i,2), round(temp,1), round(hum,1), round(vib,1)


def evaluate_status(readings):
    keys  = ["voltage","current","temperature","humidity","vibration"]
    alerts = []
    worst  = "NORMAL"

    for key, val in zip(keys, readings):
        lo, hi = THRESHOLDS[key]
        if val < lo or val > hi:
            severity = "CRITICAL" if (val < lo*0.85 or val > hi*1.15) else "WARNING"
            alerts.append({"sensor": key.title(), "value": val,
                           "message": f"{'Below min' if val<lo else 'Above max'} threshold",
                           "severity": severity})
            if severity == "CRITICAL":
                worst = "CRITICAL"
            elif worst != "CRITICAL":
                worst = "WARNING"

    return worst, alerts


def background_loop():
    while True:
        with _lock:
            tick = _state["tick"] + 1
            readings = simulate_sensor(tick)
            keys     = ["voltage","current","temperature","humidity","vibration"]
            status, alerts = evaluate_status(readings)

            for key, val in zip(keys, readings):
                _state["history"][key].append(val)
                if len(_state["history"][key]) > MAX_HISTORY:
                    _state["history"][key].pop(0)

            _state.update({
                "tick": tick,
                "voltage":     readings[0],
                "current":     readings[1],
                "temperature": readings[2],
                "humidity":    readings[3],
                "vibration":   readings[4],
                "status":      status,
                "alerts":      alerts,
            })
        time.sleep(1)


# Start background thread
threading.Thread(target=background_loop, daemon=True).start()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stream")
def stream():
    """Server-Sent Events endpoint — pushes sensor state every second."""
    def generate():
        last_tick = -1
        while True:
            with _lock:
                tick = _state["tick"]
            if tick != last_tick:
                last_tick = tick
                with _lock:
                    payload = json.dumps({
                        "tick":        _state["tick"],
                        "voltage":     _state["voltage"],
                        "current":     _state["current"],
                        "temperature": _state["temperature"],
                        "humidity":    _state["humidity"],
                        "vibration":   _state["vibration"],
                        "status":      _state["status"],
                        "alerts":      _state["alerts"],
                        "history":     _state["history"],
                    })
                yield f"data: {payload}\n\n"
            time.sleep(0.2)

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


if __name__ == "__main__":
    app.run(debug=False, port=5002, threaded=True)
