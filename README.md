# ⚡ Arduino IoT Sensor Monitor Dashboard

> **Real-time multi-channel sensor monitoring system with live streaming, threshold alerts, and 60-second history charts**

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square&logo=flask)
![SSE](https://img.shields.io/badge/Streaming-Server--Sent%20Events-purple?style=flat-square)
![Realtime](https://img.shields.io/badge/Update%20Rate-1Hz-green?style=flat-square)

---

## 📌 Overview

This project simulates the software layer of an Arduino IoT monitoring system — the kind of dashboard a drone operator, electrical engineer, or embedded systems developer would use to watch hardware health in real time.

**Five sensor channels are monitored simultaneously:**

| Sensor | Range | Safe Threshold |
|--------|-------|---------------|
| Voltage | 0–20V | 9V – 15V |
| Current | 0–10A | 0.5A – 6A |
| Temperature | 0–100°C | 10°C – 65°C |
| Humidity | 0–100% | 20% – 90% |
| Vibration | 0–100Hz | 20Hz – 80Hz |

---

## ⚙️ Features

- **Live Server-Sent Events (SSE)** — no WebSocket library needed, zero-latency streaming at 1Hz
- **5 real-time gauges** — with colour-coded status bars (Normal → Warning → Critical)
- **Sparkline per sensor** — instant at-a-glance trend for each channel
- **60-second history chart** — switchable between sensors, with threshold bands overlaid
- **Automatic fault injection** — every 120 seconds, a simulated fault (overheat + voltage sag + current surge) fires to test the alert system
- **Dark terminal UI** — purpose-built for embedded/IoT engineers

---

## 🏗️ Architecture

```
Flask Background Thread
    │
    ├── Simulates Arduino sensor readings @ 1Hz
    ├── Evaluates thresholds → WARNING / CRITICAL
    └── Stores 60-point rolling history per channel
          │
          ▼
    /stream endpoint (SSE)
          │
          ▼
    Browser JavaScript
          │
          ├── Updates 5 live gauges
          ├── Draws sparklines (Canvas 2D)
          ├── Renders 60s history chart
          └── Shows active alerts panel
```

---

## 🔌 Real Arduino Integration

To connect a real Arduino instead of the simulator, replace `simulate_sensor()` in `app.py` with:

```python
import serial

ser = serial.Serial('/dev/ttyACM0', 9600)  # adjust port

def read_from_arduino():
    line = ser.readline().decode('utf-8').strip()
    # Expected Arduino output: "12.1,2.4,36.5,61.2,49.8"
    parts = [float(x) for x in line.split(',')]
    return parts[0], parts[1], parts[2], parts[3], parts[4]
```

This is exactly the serial protocol you would implement on the Arduino side with `Serial.print()`.

---

## 🚀 Setup

```bash
git clone https://github.com/chimuanya-ugochukwu/iot-sensor-dashboard
cd iot-sensor-dashboard

pip install flask

python app.py
# → Open http://localhost:5002
```

---

## 🌍 Real-World Application

This dashboard mirrors the kind of system used in:
- Drone flight controller health monitoring during pre-flight checks
- Solar power system monitoring (voltage, current, temperature)
- Industrial equipment preventive maintenance
- Smart home IoT sensor hubs

---

## 👤 Author

**Ugochukwu Chimuanya Chigozirim**  
B.Eng. Electronic & Computer Engineering (in view)  
University of Nigeria, Nsukka  
[LinkedIn](https://www.linkedin.com/in/chimuanya-ugochukwu-737a742b7) · chimuanyaugochukwu750@gmail.com
