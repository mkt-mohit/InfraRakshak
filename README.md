# 🛡️ InfraRakshak AI
### Intelligent Anomaly Detection for Critical Infrastructure

[![Live App](https://img.shields.io/badge/Live%20App-infrarakshak--ai.com-blue?style=for-the-badge)](https://www.infrarakshak-ai.com)
[![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Containerised-blue?style=for-the-badge&logo=docker)](https://docker.com)
[![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20ECR%20%7C%20Route53-orange?style=for-the-badge&logo=amazonaws)](https://aws.amazon.com)

---

##  Problem Statement

Modern critical infrastructure — power grids, telecom networks, water systems, and smart cities — generates massive volumes of operational logs every second. Manual monitoring is slow, reactive, and expensive. Faults are detected only after failure, causing significant operational losses.

> **InfraRakshak** proactively detects anomalies and provides Root Cause Analysis (RCA) using ML — before failures happen.

this is the demo
---

##  Features

| Feature | Description |
|---|---|
|  Domain Selection | Choose from Power, Telecom, Water, or Smart City |
|  Time Range | Select number of days of log data to analyse |
|  ML Anomaly Detection | Real-time anomaly detection on live log streams |
|  RCA Generation | Root Cause Analysis for every detected anomaly |
|  Feedback Loop | User validates predictions; model retrains automatically |
|  Production Deployed | Live on AWS EC2 with HTTPS via custom domain |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       InfraRakshak Platform                      │
│                                                                  │
│  [Live Log Generator] ──► [ML Anomaly Engine] ──► [Dashboard]   │
│                                  │                     │         │
│                             [RCA Module]        [Feedback Loop]  │
│                                                        │         │
│                                            [Model Retraining]    │
└──────────────────────────────────────────────────────────────────┘
```

| Block | Role |
|---|---|
| **Live Log Generator** | Simulates real-time operational logs for all supported domains |
| **ML Anomaly Engine** | Core ML model that detects abnormal patterns in incoming logs |
| **RCA Module** | Explains *why* an anomaly occurred for faster operator response |
| **Streamlit Dashboard** | Web UI for domain selection, anomaly results, and RCA display |
| **Feedback Loop** | Captures user-validated True/False labels to improve the model |
| **Model Retraining** | Retrains with updated feedback and redeploys automatically |
| **MLOps CI/CD** | One `git push` triggers build → ECR → EC2 → live in production |

---

##  User Flow

```
User Opens App
     │
     ▼
Selects Domain  (Power / Telecom / Water / Smart City)
     │
     ▼
Selects Number of Days to Analyse
     │
     ▼
App Generates Dummy Live Logs (real-time simulation)
     │
     ▼
ML Model Detects Anomalies
     │
     ▼
Dashboard Shows: Anomaly List + RCA
     │
     ▼
User Reviews Prediction
     │
   ┌─┴────────────────┐
   │                  │
 TRUE              FALSE
(Confirmed)    (False Positive)
   │                  │
   └──────┬───────────┘
          ▼
   Feedback Recorded
          │
          ▼
   git push → Model Retrained → Redeployed
```

---

## 🔁 Feedback Loop & Continuous Learning

> 🔁 *"Human Feedback Today = Smarter Model Tomorrow"*

1. User reviews each flagged anomaly on the live dashboard
2. Marks it as **TRUE** (real anomaly) or **FALSE** (false alarm)
3. Feedback is stored as ground truth labels
4. A single `git push` triggers the retraining pipeline
5. New model is built, containerised, and pushed to production
6. Every feedback cycle makes the model more accurate

---

## ⚙️ MLOps Pipeline

>  *"One Push to Rule Them All — Code to Cloud in Seconds"*

```
Developer Laptop
     │  git push (Step 1)
     ▼
GitHub Repository
     │  CI trigger → build (Step 2)
     ▼
Docker Image (Built Locally) (Step 3)
     │  docker push
     ▼
AWS ECR (Elastic Container Registry) (Step 4)
     │  docker pull + run
     ▼
AWS EC2 Instance (Step 5)
     │
     ├── Route 53: infrarakshak-ai.com → EC2 Public IP (Step 6)
     │
     ├── NGINX Reverse Proxy (Step 7)
     │        │
     │        ▼
     └── Streamlit Container (Live App) (Step 8)
```

| Step | Action |
|---|---|
| 1 | Code + feedback data committed and pushed from developer laptop |
| 2 | GitHub triggers build pipeline |
| 3 | Docker image built locally with updated model |
| 4 | Image pushed to AWS ECR (Elastic Container Registry) |
| 5 | EC2 pulls latest image and spins up new container |
| 6 | Route 53 DNS record maps domain to EC2 public IP |
| 7 | NGINX routes HTTPS traffic to Streamlit container port |
| 8 | Live app serves updated model to end users |

---

##  Domains Supported

| Domain | Example Anomalies Detected |
|---|---|
| ⚡ Power | Voltage spikes, load imbalance, outage prediction |
| 📡 Telecom | Packet loss, latency spikes, tower downtime |
| 💧 Water | Pressure drops, flow anomalies, pipe leak signals |
| 🏙️ Smart City | Traffic congestion, sensor failures, energy waste |

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| ML Model | Scikit-learn / Custom Anomaly Detection |
| Log Simulation | Python (synthetic log generator) |
| Containerisation | Docker |
| Container Registry | AWS ECR |
| Cloud Compute | AWS EC2 |
| Reverse Proxy | NGINX |
| DNS & Domain | AWS Route 53 + `infrarakshak-ai.com` |
| CI/CD | Git Push → Retrain → Redeploy |
| RCA Engine | Rule-based + ML feature attribution |

---

## 🏁 Getting Started

### Prerequisites
```bash
python >= 3.10
docker
git
```

### Run Locally
```bash
# Clone the repository
git clone https://github.com/<your-username>/infrarakshak.git
cd infrarakshak

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

### Run with Docker
```bash
# Build the image
docker build -t infrarakshak .

# Run the container
docker run -p 8501:8501 infrarakshak
```

---

##  Live Demo

🔗 **[https://www.infrarakshak-ai.com](https://www.infrarakshak-ai.com)**

Fully deployed on AWS EC2 with HTTPS via Route 53 and NGINX reverse proxy.

---

##  Key Differentiators

- **End-to-End MLOps** — Laptop to production with a single `git push`
- **Multi-Domain** — One platform for Power, Telecom, Water & Smart City
- **Explainable AI** — Every anomaly comes with an RCA, not just a flag
- **Continuous Learning** — Human feedback directly retrains the model
- **Production Ready** — HTTPS domain, containerised, cloud-hosted
- **Scalable** — Docker + AWS scales horizontally on demand

---

##  License

This project is licensed under the MIT License.

---

*Built with ❤️ for Bharath | Powered by MLOps*
