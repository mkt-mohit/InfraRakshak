import json
import math
from datetime import datetime


def estimate_severity(anomaly_score: float) -> str:
    """Simple rule-based severity from anomaly score."""
    if anomaly_score >= 0.8:
        return "CRITICAL"
    if anomaly_score >= 0.5:
        return "MEDIUM"
    if anomaly_score >= 0.2:
        return "LOW"
    return "NORMAL"


def estimate_time_to_failure(anomaly_score: float) -> int:
    """Rough time-to-failure in minutes based on anomaly score.

    Higher anomaly → shorter remaining time. This is just a demo heuristic.
    """
    if anomaly_score < 0.2:
        return 120  # safe
    # Map [0.2, 1.0] to [90, 5] minutes
    x = max(0.0, min(1.0, anomaly_score))
    return int(5 + (1.0 - x) * 85)


def generate_explanation(domain: str, metrics: dict, severity: str, ttf: int, location_type: str = "unspecified") -> dict:
    """Generate a simple, human-readable root-cause + recommendation.

    In a full system this would call an LLM (e.g., Amazon Bedrock).
    Here we use templates so the Lambda stays free-tier friendly.
    """
    base = (
        f"Domain: {domain}. Location: {location_type}. Severity: {severity}. "
        f"Estimated time to failure: {ttf} minutes."
    )

    if domain.lower() == "power":
        voltage = metrics.get("voltage")
        temperature = metrics.get("temperature")
        cause = (
            "Repeated voltage instability and rising transformer temperature may indicate "
            "overheating or cooling system degradation."
        )
        action = "Inspect cooling modules and check load balancing on the affected feeder."
    elif domain.lower() == "telecom":
        latency = metrics.get("latency_ms")
        cause = (
            "Sustained high latency and packet anomalies may indicate congestion or link degradation "
            "in the backhaul network."
        )
        action = "Check backhaul links, routing tables, and recent configuration changes."
    elif domain.lower() == "water":
        pressure = metrics.get("pressure_bar")
        tank_level = metrics.get("tank_level_pct")
        cause = (
            "Irregular pressure and reservoir level patterns may indicate leakage, pump malfunction, "
            "or valve misconfiguration in the water distribution network."
        )
        action = "Inspect pumps, valves, and nearby pipe sections for leaks or blockages."
    elif domain.lower() == "smart_city":
        cause = (
            "High traffic density combined with reduced signal uptime or offline CCTV feeds may "
            "indicate controller faults or power issues at intersections."
        )
        action = "Inspect traffic signal controllers, local power supply, and connectivity to CCTV nodes."
    elif domain.lower() == "water":
        pressure = metrics.get("pressure_bar")
        tank_level = metrics.get("tank_level_pct")
        cause = (
            "Irregular pressure and reservoir level patterns may indicate leakage, pump malfunction, "
            "or valve misconfiguration in the water distribution network."
        )
        action = "Inspect pumps, valves, and nearby pipe sections for leaks or blockages."
    else:
        cause = "Anomalous behavior detected in infrastructure metrics."
        action = "Investigate the affected device, review logs, and perform a quick health check."

    return {
        "root_cause": f"{base} {cause}",
        "recommendation": action,
    }


def handler(event, context):
    """AWS Lambda entry point.

    Expects a JSON body like:
    {
      "domain": "power",  # or "telecom", "water", etc.
      "device_id": "transformer-3",
      "metrics": {
        "voltage": 238.5,
        "temperature": 78.2,
        "latency_ms": 20,
        "load_pct": 85
      }
    }
    """
    try:
        if isinstance(event, str):
            body = json.loads(event)
        elif "body" in event:
            # API Gateway proxy format
            raw_body = event["body"]
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        else:
            body = event

        domain = body.get("domain", "unknown")
        device_id = body.get("device_id", "unknown-device")
        metrics = body.get("metrics", {})
        location_type = body.get("location_type", "unspecified")

        # Simple anomaly score heuristic for demo: combine a few metrics if present
        voltage = float(metrics.get("voltage", 0.0))
        temperature = float(metrics.get("temperature", 0.0))
        latency = float(metrics.get("latency_ms", 0.0))
        load_pct = float(metrics.get("load_pct", 0.0))
        pressure_bar = float(metrics.get("pressure_bar", 0.0))
        tank_level_pct = float(metrics.get("tank_level_pct", 0.0))
        flow_lps = float(metrics.get("flow_lps", 0.0))

        # Example heuristic: normalize each dimension a bit and combine
        score_components = []
        if voltage:
            # assume 230V nominal; deviation beyond +/-10V is anomalous
            score_components.append(min(1.0, abs(voltage - 230.0) / 20.0))
        if temperature:
            # assume > 70°C starts to be risky
            score_components.append(min(1.0, max(0.0, (temperature - 50.0) / 40.0)))
        if latency:
            # for telecom: > 100ms high
            score_components.append(min(1.0, latency / 200.0))
        if load_pct:
            # > 80% load is risky
            score_components.append(min(1.0, max(0.0, (load_pct - 60.0) / 40.0)))
        if pressure_bar:
            # assume ~3 bar nominal in water network
            score_components.append(min(1.0, abs(pressure_bar - 3.0) / 1.0))
        if tank_level_pct:
            if tank_level_pct < 20 or tank_level_pct > 90:
                score_components.append(0.8)
            else:
                score_components.append(0.1)
        if flow_lps:
            if flow_lps < 5 or flow_lps > 120:
                score_components.append(0.7)
            else:
                score_components.append(0.2)

        anomaly_score = sum(score_components) / len(score_components) if score_components else 0.0
        severity = estimate_severity(anomaly_score)
        time_to_failure = estimate_time_to_failure(anomaly_score)
        explanation = generate_explanation(domain, metrics, severity, time_to_failure, location_type)

        result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "domain": domain,
            "device_id": device_id,
            "metrics": metrics,
            "location_type": location_type,
            "anomaly_score": round(anomaly_score, 3),
            "severity": severity,
            "time_to_failure_minutes": time_to_failure,
            "explanation": explanation,
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }

    except Exception as exc:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(exc)}),
        }
