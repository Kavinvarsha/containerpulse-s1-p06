# ContainerPulse — Mid-Term Documentation
## pSiddhi S1-P-06 | Kavinvarsha Janakiram (P497) | Platform Track
## Submission Date: 12 July 2026

---

## WEEK 4 — Infrastructure Setup ✅

### What Was Done
- Installed WSL2 + Ubuntu 26.04 on Windows laptop
- Installed Docker Engine 29.2.1 inside WSL2
- Installed Minikube v1.38.1 with Kubernetes v1.35.1
- Deployed Prometheus v3.12.0 via Helm
- Deployed cAdvisor as DaemonSet with Prometheus scrape annotations
- Deployed Grafana v12.3.1 via Helm
- Launched 3 target containers:
  - api-service (nginx)
  - pipeline-worker (python)
  - web-service (httpd)

### Evidence
- 1268 Prometheus metrics confirmed via Python API
- All 8 pods running in monitoring namespace
- Grafana dashboard showing live CPU, Memory, Network metrics

### Tests Passed
- Metric schema validation ✅
- Scrape interval verification ✅
- Container health checks ✅

---

## WEEK 5 — Data Pipeline ✅

### What Was Done
- Built fetch_metrics.py: pulls 6 health dimensions from Prometheus API
  - CPU usage
  - Memory usage
  - Memory cache
  - Network RX bytes
  - Network TX bytes
  - Restart count
- Built transform_data.py: normalises raw data into ML-ready time-series CSV
- Built validate_data.py: Great Expectations data quality checks
- 4/4 validation checks passing

### Evidence
- metrics_raw.csv: raw Prometheus data (604,953 bytes)
- metrics_ml_ready.csv: normalised time-series format (134,727 bytes)
- Great Expectations: 4/4 checks passed
- 3115 data rows across all containers

### Tests Passed
- Data pipeline correctness ✅
- Null/gap detection ✅
- Schema validation ✅
- Integration tests ✅

---

## WEEK 6 — Isolation Forest Anomaly Detection ✅

### What Was Done
- Trained Isolation Forest model per container (17 containers total)
- contamination=0.05 (5% expected anomaly rate)
- n_estimators=100, random_state=42
- Tested on 3 simulated failure types per container:
  1. CPU spike (extreme CPU injection)
  2. Memory leak (extreme memory injection)
  3. Crash loop (extreme network/restart injection)

### Results for 3 Target Containers
| Container | Anomalies | CPU Spike | Memory Leak | Crash Loop |
|---|---|---|---|---|
| api-service | 3/55 (5.5%) | 1/3 | 1/3 | 3/3 |
| pipeline-worker | 3/55 (5.5%) | 3/3 | 1/3 | 3/3 |
| web-service | 3/55 (5.5%) | 1/3 | 1/3 | 1/3 |

### Evidence
- anomaly_detection.py: model training and scoring
- anomaly_report.json: per-container anomaly results
- model_accuracy_report.json: Week 6 accuracy metrics
- model_accuracy_report.txt: human-readable accuracy report

---

## WEEK 7 — LSTM Forecasting ✅

### What Was Done
- Trained LSTM neural network per container (17 containers)
- Architecture: LSTM(32) → Dropout(0.2) → LSTM(16) → Dense(1)
- 20 epochs, batch size 8, optimizer Adam
- 6-step ahead forecast (3 minutes at 30s intervals)
- Calculated MAE and RMSE per container

### Results for 3 Target Containers
| Container | MAE | RMSE | Test Samples |
|---|---|---|---|
| api-service | 0.026192 | 0.035141 | 9 |
| pipeline-worker | 0.087268 | 0.112160 | 9 |
| web-service | 0.182216 | 0.238923 | 9 |

### Interpretation
- api-service: Excellent forecast accuracy (MAE 0.026)
- pipeline-worker: Very good forecast accuracy (MAE 0.087)
- web-service: Good forecast accuracy (MAE 0.182)

### Evidence
- lstm_forecast.py: model training and forecasting
- lstm_forecast.json: per-container 6-step forecasts
- model_accuracy_report.json: Week 7 MAE/RMSE metrics

---

## WEEK 8 — AI Integration ✅

### What Was Done
- Integrated Groq API (Llama 3.3 70B) for log/anomaly analysis
- Integrated Google Gemini Flash for incident report generation
- Built incident_summary.py: full AI pipeline
- Groq analyzed anomaly patterns across all containers
- Gemini generated structured incident report with risk levels

### Evidence
- incident_summary.py: Groq + Gemini pipeline
- incident_report.json: AI-generated incident analysis
- incident_report.txt: human-readable incident report

---

## WEEK 9 — Testing, Bug Fixes, Documentation ✅

### Bug Fixes Completed
- Fixed cAdvisor DaemonSet for proper pod-level metrics
- Fixed Python 3.14 → 3.11 version compatibility issue
- Fixed Prometheus URL port management across sessions
- Fixed GitHub Actions YAML heredoc syntax error
- Fixed Gemini API quota by switching models

### Tests Written and Passing
1. test_raw_metrics_exists ✅
2. test_ml_ready_columns ✅
3. test_no_negative_memory ✅
4. test_anomaly_report ✅
5. test_lstm_forecast ✅
6. test_database ✅
7. test_no_null_timestamps ✅
8. test_known_containers_present ✅

### CI/CD
- GitHub Actions pipeline: GREEN ✅
- Run time: 28 seconds
- All 8 tests passing in CI

---

## GitHub Repository
https://github.com/Kavinvarsha/containerpulse-s1-p06

## Tech Stack
| Component | Technology | Version |
|---|---|---|
| OS | Ubuntu WSL2 | 26.04 |
| Container Runtime | Docker Engine | 29.2.1 |
| Orchestration | Kubernetes/Minikube | v1.35.1/v1.38.1 |
| Metrics Collection | Prometheus | v3.12.0 |
| Container Metrics | cAdvisor | latest |
| Dashboards | Grafana | v12.3.1 |
| Language | Python | 3.11 |
| Anomaly Detection | Isolation Forest | scikit-learn 1.9.0 |
| Forecasting | LSTM | TensorFlow 2.x |
| AI Log Analysis | Groq | Llama 3.3 70B |
| AI Incident Reports | Google Gemini | Flash |
| Database | SQLite | built-in |
| Testing | pytest | 8.x |
| Data Validation | Great Expectations | 1.18.1 |
| CI/CD | GitHub Actions | - |
