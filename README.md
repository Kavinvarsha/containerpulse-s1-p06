# ContainerPulse – Smart Container Health Monitoring Tool

**Developer:** Kavinvarsha Janakiram  
**Project:** pSiddhi S1-P-06 Platform Track

---

## Project Overview

ContainerPulse is an AI-powered Kubernetes container monitoring system. It collects live metrics from Prometheus, detects anomalies using Machine Learning, forecasts future CPU usage using LSTM, generates AI-based incident reports using Groq Llama and Google Gemini, and stores results in SQLite.

---

## Features

- Collects CPU, Memory and Network metrics from Prometheus
- Detects anomalies using Isolation Forest
- Forecasts CPU utilization using LSTM
- Generates incident summaries using Groq and Gemini
- Stores anomaly reports in SQLite
- Automated testing using Pytest
- CI/CD using GitHub Actions

---

## Technologies Used

- Python 3.11
- Docker
- Kubernetes (Minikube)
- Prometheus
- Grafana
- Pandas
- Scikit-learn
- TensorFlow
- SQLite
- Groq API
- Google Gemini API
- GitHub Actions

---

## Project Structure

```text
container-pulse/
├── .github/
│   └── workflows/
│       └── ci.yml
├── fetch_metrics.py
├── transform_data.py
├── anomaly_detection.py
├── lstm_forecast.py
├── incident_summary.py
├── store_results.py
├── test_pipeline.py
├── validate_data.py
├── README.md
└── .env
```

---

## How to Run

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run the pipeline:

```bash
python3 fetch_metrics.py
python3 transform_data.py
python3 anomaly_detection.py
python3 lstm_forecast.py
python3 incident_summary.py
python3 store_results.py
```

Run tests:

```bash
python3 -m pytest test_pipeline.py -v
```

---

## Output Files

- metrics_raw.csv
- metrics_ml_ready.csv
- anomaly_report.json
- lstm_forecast.json
- incident_report.json
- containerpulse.db

---

## Author

**Kavinvarsha Janakiram**
