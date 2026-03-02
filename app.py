import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).parent
FEEDBACK_PATH = BASE_DIR / "feedback_history.csv"
THRESHOLD_PATH = BASE_DIR / "anomaly_threshold.json"


def estimate_severity(anomaly_score: float) -> str:
    if anomaly_score >= 0.8:
        return "CRITICAL"
    if anomaly_score >= 0.5:
        return "MEDIUM"
    if anomaly_score >= 0.2:
        return "LOW"
    return "NORMAL"


def estimate_time_to_failure(anomaly_score: float) -> int:
    if anomaly_score < 0.2:
        return 120
    x = max(0.0, min(1.0, anomaly_score))
    return int(5 + (1.0 - x) * 85)


def generate_explanation(domain: str, metrics: dict, severity: str, ttf: int, location_type: str = "unspecified") -> dict:
    base = (
        f"Domain: {domain}. Location: {location_type}. Severity: {severity}. "
        f"Estimated time to failure: {ttf} minutes."
    )

    if domain.lower() == "power":
        cause = (
            "Repeated voltage instability and rising transformer temperature may indicate "
            "overheating or cooling system degradation."
        )
        action = "Inspect cooling modules and check load balancing on the affected feeder."
    elif domain.lower() == "telecom":
        cause = (
            "Sustained high latency and packet anomalies may indicate congestion or link degradation "
            "in the backhaul network."
        )
        action = "Check backhaul links, routing tables, and recent configuration changes."
    elif domain.lower() == "water":
        cause = (
            "Irregular pressure and tank level fluctuations may indicate leakage, pump malfunction, "
            "or valve misconfiguration in the distribution network."
        )
        action = "Inspect pumps and valves for leaks or blockages and verify reservoir levels."
    elif domain.lower() == "smart_city":
        cause = (
            "High traffic density combined with reduced signal uptime or offline CCTV feeds may "
            "indicate controller faults or power issues at intersections."
        )
        action = "Inspect traffic signal controllers, local power supply, and network connectivity to CCTV nodes."
    else:
        cause = "Anomalous behavior detected in infrastructure metrics."
        action = "Investigate the affected device, review logs, and perform a quick health check."

    return {
        "root_cause": f"{base} {cause}",
        "recommendation": action,
    }


def analyze_event(event: dict) -> dict:
    domain = event.get("domain", "unknown")
    device_id = event.get("device_id", "unknown-device")
    metrics = event.get("metrics", {})
    location_type = event.get("location_type", "unspecified")

    voltage = float(metrics.get("voltage", 0.0))
    temperature = float(metrics.get("temperature", 0.0))
    latency = float(metrics.get("latency_ms", 0.0))
    load_pct = float(metrics.get("load_pct", 0.0))
    pressure_bar = float(metrics.get("pressure_bar", 0.0))
    tank_level_pct = float(metrics.get("tank_level_pct", 0.0))
    flow_lps = float(metrics.get("flow_lps", 0.0))
    traffic_density = float(metrics.get("traffic_density", 0.0))
    signal_uptime = float(metrics.get("signal_uptime_pct", 0.0))
    cctv_online = float(metrics.get("cctv_online_pct", 0.0))

    score_components = []
    if voltage:
        score_components.append(min(1.0, abs(voltage - 230.0) / 20.0))
    if temperature:
        score_components.append(min(1.0, max(0.0, (temperature - 50.0) / 40.0)))
    if latency:
        score_components.append(min(1.0, latency / 200.0))
    if load_pct:
        score_components.append(min(1.0, max(0.0, (load_pct - 60.0) / 40.0)))
    if pressure_bar:
        # assume ~3 bar nominal, +/-0.5 normal range
        score_components.append(min(1.0, abs(pressure_bar - 3.0) / 1.0))
    if tank_level_pct:
        # very low or very high tank levels are risky
        if tank_level_pct < 20 or tank_level_pct > 90:
            score_components.append(0.8)
        else:
            score_components.append(0.1)
    if flow_lps:
        # near zero flow when pumps should run or very high spikes are suspicious
        if flow_lps < 5 or flow_lps > 120:
            score_components.append(0.7)
        else:
            score_components.append(0.2)
    if traffic_density:
        # 0-100 index, near 100 means heavy congestion
        score_components.append(min(1.0, traffic_density / 100.0))
    if signal_uptime:
        # low uptime is risky
        if signal_uptime < 95:
            score_components.append(0.7)
        else:
            score_components.append(0.1)
    if cctv_online:
        # low CCTV availability is a risk for smart city ops
        if cctv_online < 80:
            score_components.append(0.8)
        else:
            score_components.append(0.2)

    anomaly_score = sum(score_components) / len(score_components) if score_components else 0.0
    severity = estimate_severity(anomaly_score)
    ttf = estimate_time_to_failure(anomaly_score)
    explanation = generate_explanation(domain, metrics, severity, ttf, location_type)

    return {
        "timestamp": event.get("timestamp"),
        "domain": domain,
        "device_id": device_id,
        "metrics": metrics,
        "location_type": location_type,
        "anomaly_score": round(anomaly_score, 3),
        "severity": severity,
        "time_to_failure_minutes": ttf,
        "explanation": explanation,
    }


def generate_power_log(device_id: str, anomaly_prob: float = 0.2) -> dict:
    base_voltage = 230.0
    base_temp = 60.0

    if random.random() < anomaly_prob:
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
    }


def generate_telecom_log(device_id: str, anomaly_prob: float = 0.2) -> dict:
    if random.random() < anomaly_prob:
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
    }


def generate_water_log(device_id: str, anomaly_prob: float = 0.2) -> dict:
    """Simulate a water infrastructure log event (pressure, flow, tank level)."""

    base_pressure = 3.0  # bar
    base_flow = 60.0  # L/s
    base_level = 60.0  # %

    if random.random() < anomaly_prob:
        # anomalies: pressure drops or spikes, near-empty/overflow tank, odd flows
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
    }


def generate_smart_city_log(device_id: str, anomaly_prob: float = 0.2) -> dict:
    """Simulate a smart city / traffic log event."""

    if random.random() < anomaly_prob:
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
    }


st.set_page_config(page_title="InfraRakshak AI", layout="wide")

st.title("InfraRakshak AI – Infra Anomaly & Failure Predictor (Prototype)")

# Simple two-step flow: 1) Configure simulation, 2) Analyze results
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "simulation"

page_choice = st.radio(
    "View",
    ["Simulation controls", "Analysis & insights"],
    index=0 if st.session_state["active_page"] == "simulation" else 1,
    horizontal=True,
)

st.session_state["active_page"] = "simulation" if page_choice == "Simulation controls" else "analysis"

st.sidebar.header("Simulation Controls")

domain = st.sidebar.selectbox("Domain", ["power", "telecom", "water", "smart_city"])
num_events = st.sidebar.slider("Number of events per day to simulate", 1, 50, 10)
num_days = st.sidebar.slider(
    "Number of days to simulate", 1, 30, 1, help="Events will be simulated across this many days."
)
anomaly_prob = st.sidebar.slider(
    "Anomaly probability (0 = only healthy, 1 = mostly faults)", 0.0, 1.0, 0.2, 0.05
)

if domain == "power":
    device_id = st.sidebar.text_input("Device ID", "transformer-3")
elif domain == "telecom":
    device_id = st.sidebar.text_input("Device ID", "cell-tower-7")
elif domain == "water":
    device_id = st.sidebar.text_input("Device ID", "pump-station-2")
else:
    device_id = st.sidebar.text_input("Device ID", "signal-junction-11")

location_type = st.sidebar.selectbox(
    "Location type",
    ["urban", "rural", "critical_facility"],
    help="Used to prioritize alerts for rural and critical locations in Bharat.",
)

if "events" not in st.session_state:
    st.session_state["events"] = []
if "feedback" not in st.session_state:
    st.session_state["feedback"] = []
if "anomaly_threshold" not in st.session_state:
    # baseline anomaly score threshold used to highlight anomalies in the analysis view
    st.session_state["anomaly_threshold"] = 0.2

# Load persisted feedback and threshold once per session so the app
# remembers user feedback across restarts.
if "_state_loaded" not in st.session_state:
    try:
        if FEEDBACK_PATH.exists():
            fb_df = pd.read_csv(FEEDBACK_PATH)
            st.session_state["feedback"] = fb_df.to_dict(orient="records")
    except Exception:
        # Ignore corrupt or unreadable feedback files; start fresh in that case.
        st.session_state["feedback"] = []

    try:
        if THRESHOLD_PATH.exists():
            with THRESHOLD_PATH.open("r", encoding="utf-8") as f:
                saved = json.load(f)
                saved_thr = float(saved.get("anomaly_threshold", st.session_state["anomaly_threshold"]))
                if 0.0 < saved_thr < 1.0:
                    st.session_state["anomaly_threshold"] = saved_thr
    except Exception:
        # If threshold file is invalid, keep the default in-memory value.
        pass

    st.session_state["_state_loaded"] = True

if st.sidebar.button("Run simulation"):
    events = []

    # Adjust anomaly probability based on location type so that
    # rural and critical facilities behave differently from urban.
    location_factor = {
        "urban": 1.0,
        "rural": 1.1,
        "critical_facility": 1.3,
    }.get(location_type, 1.0)
    effective_anomaly_prob = min(1.0, anomaly_prob * location_factor)

    for day in range(num_days):
        # distribute events across the selected number of days
        simulated_date = datetime.utcnow() - timedelta(days=(num_days - 1 - day))
        for _ in range(num_events):
            if domain == "power":
                ev = generate_power_log(device_id, effective_anomaly_prob)
            elif domain == "telecom":
                ev = generate_telecom_log(device_id, effective_anomaly_prob)
            elif domain == "water":
                ev = generate_water_log(device_id, effective_anomaly_prob)
            else:
                ev = generate_smart_city_log(device_id, effective_anomaly_prob)

            # override timestamp to reflect the simulated day
            ev["timestamp"] = simulated_date.isoformat() + "Z"
            # tag with location type for explanation layer
            ev["location_type"] = location_type
            analyzed = analyze_event(ev)
            events.append(analyzed)

    st.session_state["events"] = events
    # Automatically switch to the analysis page after a run
    st.session_state["active_page"] = "analysis"

events = st.session_state.get("events", [])
if st.session_state["active_page"] == "simulation":
    st.info(
        "Configure the simulation parameters in the sidebar and click 'Run simulation'. "
        "You will then be taken to the 'Analysis & insights' page to review anomalies."
    )
else:
    st.subheader("Analysis dashboard")

    if events:
        latest = events[-1]

        # Build a single DataFrame once for all views
        df_rows = []
        for e in events:
            row = {
                "timestamp": e["timestamp"],
                "domain": e["domain"],
                "device_id": e["device_id"],
                "anomaly_score": e["anomaly_score"],
                "severity": e["severity"],
                "time_to_failure_minutes": e["time_to_failure_minutes"],
            }
            metrics = e.get("metrics", {})
            for k, v in metrics.items():
                row[k] = v
            df_rows.append(row)

        df = pd.DataFrame(df_rows)
        threshold = st.session_state.get("anomaly_threshold", 0.2)
        anomaly_df = (
            df[df["anomaly_score"] >= threshold] if "anomaly_score" in df else pd.DataFrame()
        )

        # Compact KPI row
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric("System Health Score", f"{max(0, 100 - int(latest['anomaly_score'] * 100))}%")
        with kpi_col2:
            st.metric("Severity", latest["severity"])
        with kpi_col3:
            st.metric("Time to Failure (min)", latest["time_to_failure_minutes"])
        with kpi_col4:
            st.metric("Anomaly threshold", f"{threshold:.2f}")

        overview_tab, anomalies_tab, root_tab, raw_tab, feedback_tab = st.tabs(
            ["Overview", "Anomalies", "Root cause & solution", "Raw data", "Feedback"]
        )

        with overview_tab:
            st.markdown("**Live Log & Anomaly View**")
            st.dataframe(df, use_container_width=True)
            if "anomaly_score" in df:
                st.line_chart(df.set_index("timestamp")["anomaly_score"])

        with anomalies_tab:
            st.markdown(f"**Detected anomalies (score ≥ {threshold:.2f})**")
            if not anomaly_df.empty:
                st.dataframe(anomaly_df, use_container_width=True)
            else:
                st.write("No anomalies detected under the current threshold.")

        with root_tab:
            st.markdown("**AI Root Cause Insight**")
            st.write(latest["explanation"]["root_cause"])
            st.markdown("**Recommended Action / Solution**")
            st.write(latest["explanation"]["recommendation"])

        with raw_tab:
            st.markdown("**Raw event data (latest)**")
            st.json(latest)

        with feedback_tab:
            st.markdown("**Feedback loop**")
            fb_col1, fb_col2 = st.columns(2)
            if fb_col1.button("Mark prediction as correct"):
                fb = st.session_state.get("feedback", [])
                fb.append(
                    {
                        "timestamp": latest["timestamp"],
                        "domain": latest["domain"],
                        "device_id": latest["device_id"],
                        "severity": latest["severity"],
                        "anomaly_score": latest["anomaly_score"],
                        "label": "correct",
                    }
                )
                st.session_state["feedback"] = fb
                st.session_state["anomaly_threshold"] = max(
                    0.05, st.session_state.get("anomaly_threshold", 0.2) - 0.02
                )
                # Persist feedback and updated threshold so learning carries over
                # to future app runs.
                try:
                    fb_df = pd.DataFrame(st.session_state["feedback"])
                    fb_df.to_csv(FEEDBACK_PATH, index=False)
                    with THRESHOLD_PATH.open("w", encoding="utf-8") as f:
                        json.dump({"anomaly_threshold": st.session_state["anomaly_threshold"]}, f)
                except Exception:
                    pass
                st.success(
                    f"Feedback recorded as correct. Sensitivity increased (threshold {st.session_state['anomaly_threshold']:.2f})."
                )

            if fb_col2.button("Mark as false alarm"):
                fb = st.session_state.get("feedback", [])
                fb.append(
                    {
                        "timestamp": latest["timestamp"],
                        "domain": latest["domain"],
                        "device_id": latest["device_id"],
                        "severity": latest["severity"],
                        "anomaly_score": latest["anomaly_score"],
                        "label": "false_alarm",
                    }
                )
                st.session_state["feedback"] = fb
                st.session_state["anomaly_threshold"] = min(
                    0.95, st.session_state.get("anomaly_threshold", 0.2) + 0.02
                )
                # Persist feedback and updated threshold for future runs.
                try:
                    fb_df = pd.DataFrame(st.session_state["feedback"])
                    fb_df.to_csv(FEEDBACK_PATH, index=False)
                    with THRESHOLD_PATH.open("w", encoding="utf-8") as f:
                        json.dump({"anomaly_threshold": st.session_state["anomaly_threshold"]}, f)
                except Exception:
                    pass
                st.warning(
                    f"Feedback recorded as false alarm. Sensitivity reduced (threshold {st.session_state['anomaly_threshold']:.2f})."
                )

            if st.session_state.get("feedback"):
                st.markdown("---")
                st.subheader("Feedback history (last 10 labels)")
                fb_df = pd.DataFrame(st.session_state["feedback"])
                st.dataframe(fb_df.tail(10), use_container_width=True)
    else:
        st.info("No events yet. Run a simulation from the 'Simulation controls' page.")
st.caption(
    "This Streamlit app runs the core InfraRakshak AI logic locally. In the full architecture, "
    "these predictions and explanations are served by AWS Lambda/API Gateway, and alerts are "
    "sent via Amazon SNS."
)
