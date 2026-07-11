import pytest
import pandas as pd
import json
import os
import sqlite3

def test_raw_metrics_exists():
    assert os.path.exists("metrics_raw.csv")
    df = pd.read_csv("metrics_raw.csv")
    assert len(df) > 0
    print(f"\n  metrics_raw.csv has {len(df)} rows")

def test_ml_ready_columns():
    assert os.path.exists("metrics_ml_ready.csv")
    df = pd.read_csv("metrics_ml_ready.csv")
    assert "timestamp" in df.columns
    assert "container" in df.columns
    print(f"\n  Columns: {list(df.columns)}")

def test_no_negative_memory():
    df = pd.read_csv("metrics_ml_ready.csv")
    if "memory" in df.columns:
        assert (df["memory"] >= 0).all()
    print("\n  No negative memory values")

def test_anomaly_report():
    assert os.path.exists("anomaly_report.json")
    with open("anomaly_report.json") as f:
        report = json.load(f)
    assert "results" in report
    assert len(report["results"]) > 0
    print(f"\n  {len(report['results'])} containers analyzed")

def test_lstm_forecast():
    assert os.path.exists("lstm_forecast.json")
    with open("lstm_forecast.json") as f:
        forecast = json.load(f)
    assert "forecasts" in forecast
    assert len(forecast["forecasts"]) > 0
    for name, data in forecast["forecasts"].items():
        assert len(data["forecast"]) == 6
    print(f"\n  {len(forecast['forecasts'])} container forecasts")

def test_database():
    assert os.path.exists("containerpulse.db")
    conn = sqlite3.connect("containerpulse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM anomaly_events")
    count = cursor.fetchone()[0]
    conn.close()
    assert count > 0
    print(f"\n  {count} anomaly events in database")

def test_no_null_timestamps():
    df = pd.read_csv("metrics_raw.csv")
    assert df["timestamp"].notna().all()
    print("\n  All timestamps valid")

def test_known_containers_present():
    df = pd.read_csv("metrics_ml_ready.csv")
    containers = df["container"].unique().tolist()
    expected = ["api-service", "pipeline-worker", "web-service"]
    found = [c for c in expected if c in containers]
    assert len(found) > 0, f"No target containers found. Got: {containers}"
    print(f"\n  Found: {found}")
