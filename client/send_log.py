import json
import random
import time
from datetime import datetime

import requests

# TODO: replace with your deployed API Gateway URL, e.g.
# API_URL = "https://abc123.execute-api.ap-south-1.amazonaws.com/prod/log"
API_URL = "https://your-api-url-here"  # placeholder


def generate_power_log(device_id: str) -> dict:
    """Simulate a power grid log event."""
    base_voltage = 230.0
    base_temp = 60.0

    # occasionally inject anomalies
    if random.random() < 0.1:
        voltage = base_voltage + random.choice([-25, -20, 20, 25])
        temperature = base_temp + random.choice([15, 20])
        load_pct = random.randint(85, 100)
    else:
        voltage = base_voltage + random.uniform(-5, 5)
        temperature = base_temp + random.uniform(-5, 5)
        load_pct = random.randint(50, 80)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "domain": "power",
        "device_id": device_id,
        "metrics": {
            "voltage": round(voltage, 2),
            "temperature": round(temperature, 2),
            "load_pct": load_pct,
        },
        "location_type": random.choice(["urban", "rural", "critical_facility"]),
    }


def generate_telecom_log(device_id: str) -> dict:
    """Simulate a telecom network log event."""
    if random.random() < 0.1:
        latency = random.randint(150, 300)
        load_pct = random.randint(80, 100)
    else:
        latency = random.randint(20, 80)
        load_pct = random.randint(40, 75)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "domain": "telecom",
        "device_id": device_id,
        "metrics": {
            "latency_ms": latency,
            "load_pct": load_pct,
        },
        "location_type": random.choice(["urban", "rural", "critical_facility"]),
    }


def generate_water_log(device_id: str) -> dict:
    """Simulate a water infrastructure log event."""

    base_pressure = 3.0
    base_flow = 60.0
    base_level = 60.0

    if random.random() < 0.1:
        pressure = base_pressure + random.choice([-1.5, -1.0, 1.2])
        flow = base_flow + random.choice([-50.0, -40.0, 50.0])
        tank_level = base_level + random.choice([-45.0, 30.0])
    else:
        pressure = base_pressure + random.uniform(-0.3, 0.3)
        flow = base_flow + random.uniform(-10.0, 10.0)
        tank_level = base_level + random.uniform(-10.0, 10.0)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "domain": "water",
        "device_id": device_id,
        "metrics": {
            "pressure_bar": round(pressure, 2),
            "flow_lps": round(flow, 2),
            "tank_level_pct": round(tank_level, 1),
        },
        "location_type": random.choice(["urban", "rural", "critical_facility"]),
    }


def generate_smart_city_log(device_id: str) -> dict:
    """Simulate a smart city / traffic log event."""

    if random.random() < 0.1:
        traffic_density = random.randint(80, 100)
        signal_uptime = random.randint(85, 96)
        cctv_online = random.randint(50, 85)
    else:
        traffic_density = random.randint(20, 70)
        signal_uptime = random.randint(97, 100)
        cctv_online = random.randint(90, 100)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "domain": "smart_city",
        "device_id": device_id,
        "metrics": {
            "traffic_density": traffic_density,
            "signal_uptime_pct": signal_uptime,
            "cctv_online_pct": cctv_online,
        },
        "location_type": random.choice(["urban", "rural", "critical_facility"]),
    }


def send_event(event: dict):
    if "your-api-url-here" in API_URL:
        print("Please set API_URL in send_log.py to your API Gateway URL.")
        return

    headers = {"Content-Type": "application/json"}
    resp = requests.post(API_URL, headers=headers, data=json.dumps(event))
    print("Status:", resp.status_code)
    try:
        print("Response:", resp.json())
    except Exception:
        print("Raw response:", resp.text)


if __name__ == "__main__":
    device_power = "transformer-3"
    device_tel = "cell-tower-7"
    device_water = "pump-station-2"

    device_smart = "signal-junction-11"

    for i in range(20):
        r = random.random()
        if r < 0.25:
            ev = generate_power_log(device_power)
        elif r < 0.5:
            ev = generate_telecom_log(device_tel)
        elif r < 0.75:
            ev = generate_water_log(device_water)
        else:
            ev = generate_smart_city_log(device_smart)

        print("Sending event:", json.dumps(ev))
        send_event(ev)
        time.sleep(2)
