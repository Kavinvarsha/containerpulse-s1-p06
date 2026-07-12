# ContainerPulse S1-P-06 — Project Summary

## Student Details
- **Name:** Kavinvarsha Janakiram
- **Employee ID:** P497
- **Track:** Platform
- **Project:** S1-P-06 Smart Container Health Monitoring Tool

## What Was Built
A complete AI-powered container health monitoring system that:
1. Monitors 3 containers (api-service, pipeline-worker, web-service) in Minikube
2. Collects metrics every 30 seconds via Prometheus + cAdvisor
3. Detects anomalies using Isolation Forest ML model
4. Forecasts CPU usage for next 3 minutes using LSTM neural network
5. Generates automated incident reports using Groq + Gemini AI
6. Stores all results in SQLite database
7. Displays live dashboards in Grafana

## Files and Their Purpose
| File | Purpose |
|---|---|
| fetch_metrics.py | Pulls 6 metrics from Prometheus API |
| transform_data.py | Reshapes raw data into ML-ready format |
| anomaly_detection.py | Isolation Forest per container |
| lstm_forecast.py | LSTM 6-step CPU forecasting |
| incident_summary.py | Groq + Gemini AI incident reports |
| store_results.py | Saves everything to SQLite |
| test_pipeline.py | 8 automated pytest tests |
| create_test_data.py | CI/CD test data generator |
| .github/workflows/ci.yml | GitHub Actions pipeline |

## Results Achieved
- 1268 Prometheus metrics available
- Anomaly detection across all running containers
- LSTM forecasting with 6-step lookahead
- AI-generated incident reports in plain English
- 8/8 pytest tests passing
- GitHub Actions CI/CD green in 28 seconds

## Infrastructure Used
- WSL2 + Ubuntu 26.04 on Windows laptop
- Docker Engine 29.2.1 inside WSL2
- Minikube v1.38.1 with Kubernetes v1.35.1
- Python 3.11.x virtual environment
