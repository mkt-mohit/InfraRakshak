# InfraRakshak AI – AWS Free Tier MVP

This project is a minimal MVP for InfraRakshak AI using the AWS Free Tier.

## Components

- **AWS Lambda**: Receives log events and runs simple anomaly + severity + time-to-failure logic.
- **Amazon API Gateway**: Public HTTPS endpoint to send logs to Lambda.
- **Amazon SNS**: Sends alerts (email/SMS) for critical events.
- **Local Python client**: Simulates infrastructure logs and sends them to the API.

## Local project layout

- `app.py` – Streamlit dashboard for local simulation, analysis, and feedback.
- `lambda/`
  - `lambda_function.py` – AWS Lambda handler.
- `client/`
  - `send_log.py` – Script to simulate and send logs.
- `requirements.txt` – Optional dependencies for local use.

Configure AWS (API Gateway + Lambda + SNS), then put the deployed API URL into `client/send_log.py` and run it to test your pipeline.

---

## Streamlit dashboard – flow and functionality

### Pages and overall flow

- The dashboard in `app.py` has two views controlled by the **View** toggle at the top:
  - **Simulation controls** – page for configuring and running simulations.
  - **Analysis & insights** – page for exploring outputs, anomalies, and feedback.
- When you click **Run simulation** on the Simulation page, synthetic events are generated and stored in `st.session_state["events"]`, and the app automatically switches to the **Analysis & insights** view.

### Simulation controls (first page)

Controls live in the left sidebar:

- **Domain**: `power`, `telecom`, `water`, or `smart_city`.
- **Number of events per day to simulate**: how many log events are generated per simulated day.
- **Number of days to simulate**: how many days of history to generate. Timestamps are spread across this many days.
- **Anomaly probability**: controls how often anomalous (faulty) samples are generated versus healthy ones.
- **Device ID**: domain‑specific identifier, passed into the simulator.
- **Location type**: `urban`, `rural`, or `critical_facility`, used in the explanation text.
- **Run simulation (button)**:
  - Generates events using the `generate_*_log` functions.
  - Each event is analyzed by `analyze_event` to compute `anomaly_score`, `severity`, and `time_to_failure_minutes`.
  - Saves the analyzed list into `st.session_state["events"]`.
  - Sets `st.session_state["active_page"] = "analysis"` to move you to the Analysis page.

### Analysis & insights (second page)

When there are events in session state, the Analysis page shows:

- **Live Log & Anomaly View** (left column):
  - A table of all simulated events with:
    - `timestamp`, `domain`, `device_id`.
    - `anomaly_score`, `severity`, `time_to_failure_minutes`.
    - All raw metric fields (e.g., `voltage`, `temperature`, `latency_ms`, `pressure_bar`, etc.).
  - A line chart of `anomaly_score` over time (indexed by `timestamp`).
  - **Detected anomalies section**:
    - Uses a tunable `anomaly_threshold` from `st.session_state["anomaly_threshold"]`.
    - Filters the table to only rows with `anomaly_score >= anomaly_threshold`.
    - Shows this filtered anomalies table below the main log, or a message if none.

- **Current Risk Summary** (right column):
  - **System Health Score**: derived from the latest event’s `anomaly_score`.
  - **Severity**: latest event’s severity label (`NORMAL`, `LOW`, `MEDIUM`, `CRITICAL`).
  - **Time to Failure (min)**: latest event’s `time_to_failure_minutes`.

### Drill‑down buttons (second page)

Under the summary, three buttons operate on the **latest** event:

- **View root cause**:
  - Shows **AI Root Cause Insight** using `latest["explanation"]["root_cause"]`.
  - Text combines domain, location type, severity, time to failure, and a domain‑specific cause.

- **View raw data**:
  - Shows **Raw event data (latest)** as JSON via `st.json(latest)`.
  - Includes the original `metrics`, computed fields (`anomaly_score`, `severity`, etc.), and explanation.

- **View solution**:
  - Shows **Recommended Action / Solution** using `latest["explanation"]["recommendation"]`.
  - This is the domain‑specific mitigation or operational advice.

### Feedback loop, learning, and threshold adaptation

- Session state + persisted fields:
  - `st.session_state["feedback"]`: list of feedback entries.
  - `st.session_state["anomaly_threshold"]`: current anomaly score threshold (initially `0.20`).
  - Both feedback and the current threshold are also written to disk as:
    - `feedback_history.csv`
    - `anomaly_threshold.json`
    so that the app remembers previous feedback across restarts.

- **Mark prediction as correct (button)**:
  - Appends a record to `feedback` with:
    - `timestamp`, `domain`, `device_id`, `severity`, `anomaly_score`, and `label = "correct"` for the latest event.
  - Decreases `anomaly_threshold` slightly (down to a minimum of `0.05`) and persists the new value.
    - Effect: system becomes **more sensitive** and will classify slightly lower scores as anomalies in the anomalies table on all subsequent runs.

- **Mark as false alarm (button)**:
  - Appends a record to `feedback` with the same fields but `label = "false_alarm"`.
  - Increases `anomaly_threshold` slightly (up to a maximum of `0.95`) and persists the new value.
    - Effect: system becomes **less sensitive**, reducing future false positives in the anomalies table for future runs as well.

- **Feedback history (last 10 labels)**:
  - When there is any feedback, a table shows the most recent 10 feedback entries (`correct` / `false_alarm`) to make the feedback loop transparent.

In summary, the dashboard simulates infra logs, computes anomaly scores and risk, lets you drill down into root cause, raw data, and recommended actions, and uses your feedback to adjust how strictly anomalies are flagged in subsequent analyses — even after restarting the app, thanks to the persisted feedback history and threshold.
