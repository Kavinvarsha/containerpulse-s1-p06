
import pytest, json, os, sqlite3

def test_metrics_raw_exists():
    assert os.path.exists("metrics_raw.csv"), "metrics_raw.csv missing"

def test_ml_ready_exists():
    assert os.path.exists("metrics_ml_ready.csv"), "metrics_ml_ready.csv missing"

def test_three_target_pods_in_metrics():
    import pandas as pd
    df = pd.read_csv("metrics_raw.csv")
    pods = " ".join(df["pod"].unique().tolist())
    assert "api-service" in pods
    assert "pipeline-worker" in pods
    assert "web-service" in pods

def test_anomaly_report_exists():
    assert os.path.exists("anomaly_report.json"), "anomaly_report.json missing"

def test_lstm_forecast_exists():
    assert os.path.exists("lstm_forecast.json"), "lstm_forecast.json missing"

def test_false_positive_pass():
    assert os.path.exists("false_positive_report.json"), "false_positive_report.json missing"
    with open("false_positive_report.json") as f:
        r = json.load(f)
    assert r["false_positive_rate_pct"] < 10, f"FP rate {r['false_positive_rate_pct']}% exceeds 10%"

def test_three_incident_scenarios_exist():
    for f in ["incident_cpu_spike_report.json",
              "incident_crash_loop_report.json",
              "incident_memory_report.json"]:
        assert os.path.exists(f), f"Missing scenario file: {f}"

def test_langchain_reports_generated():
    reports = [f for f in os.listdir(".") if f.startswith("incident_report_langchain")]
    assert len(reports) >= 3, f"Only {len(reports)} LangChain reports found, need at least 3"

def test_sqlite_has_anomaly_data():
    conn = sqlite3.connect("containerpulse.db")
    count = conn.execute("SELECT COUNT(*) FROM anomaly_events").fetchone()[0]
    conn.close()
    assert count > 0, "anomaly_events table is empty"

def test_ml_ready_has_correct_columns():
    import pandas as pd
    df = pd.read_csv("metrics_ml_ready.csv")
    assert "cpu" in df.columns
    assert "memory" in df.columns
    assert "pod" in df.columns

def test_anomaly_report_has_three_containers():
    with open("anomaly_report.json") as f:
        data = json.load(f)
    assert len(data) >= 3, f"Only {len(data)} containers in anomaly report"

def test_no_negative_memory_values():
    import pandas as pd
    df = pd.read_csv("metrics_ml_ready.csv")
    assert (df["memory"] >= 0).all(), "Negative memory values found"
