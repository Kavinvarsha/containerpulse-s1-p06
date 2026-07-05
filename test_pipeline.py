
import pytest
import pandas as pd
import json
import os
import sqlite3

# Test 1: Raw metrics CSV exists and has data
def test_raw_metrics_exists():
    assert os.path.exists("metrics_raw.csv"), "metrics_raw.csv not found"
    df = pd.read_csv("metrics_raw.csv")
    assert len(df) > 0, "metrics_raw.csv is empty"
    print(f"  ✅ metrics_raw.csv has {len(df)} rows")

# Test 2: ML-ready CSV has correct columns
def test_ml_ready_columns():
    assert os.path.exists("metrics_ml_ready.csv"), "metrics_ml_ready.csv not found"
    df = pd.read_csv("metrics_ml_ready.csv")
    required = ["timestamp", "container"]
    for col in required:
        assert col in df.columns, f"Missing column: {col}"
    print(f"  ✅ metrics_ml_ready.csv has correct columns: {list(df.columns)}")

# Test 3: No negative memory values
def test_no_negative_memory():
    df = pd.read_csv("metrics_ml_ready.csv")
    if "memory" in df.columns:
        assert (df["memory"] >= 0).all(), "Negative memory values found"
    print("  ✅ No negative memory values")

# Test 4: Anomaly report exists and has results
def test_anomaly_report():
    assert os.path.exists("anomaly_report.json"), "anomaly_report.json not found"
    with open("anomaly_report.json") as f:
        report = json.load(f)
    assert "results" in report
    assert len(report["results"]) > 0
    print(f"  ✅ Anomaly report has {len(report['results'])} containers analyzed")

# Test 5: LSTM forecast exists
def test_lstm_forecast():
    assert os.path.exists("lstm_forecast.json"), "lstm_forecast.json not found"
    with open("lstm_forecast.json") as f:
        forecast = json.load(f)
    assert "forecasts" in forecast
    assert len(forecast["forecasts"]) > 0
    for name, data in forecast["forecasts"].items():
        assert len(data["forecast"]) == 6, f"Expected 6 forecast steps for {name}"
    print(f"  ✅ LSTM forecast has {len(forecast['forecasts'])} containers")

# Test 6: SQLite database exists and has data
def test_database():
    assert os.path.exists("containerpulse.db"), "containerpulse.db not found"
    conn = sqlite3.connect("containerpulse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM anomaly_events")
    count = cursor.fetchone()[0]
    assert count > 0, "No anomaly events in database"
    conn.close()
    print(f"  ✅ Database has {count} anomaly events stored")

# Test 7: No null timestamps in raw data
def test_no_null_timestamps():
    df = pd.read_csv("metrics_raw.csv")
    assert df["timestamp"].notna().all(), "Null timestamps found"
    print("  ✅ No null timestamps")

# Test 8: Containers identified correctly
def test_known_containers_present():
    df = pd.read_csv("metrics_ml_ready.csv")
    containers = df["container"].unique().tolist()
    expected = ["api-service", "pipeline-worker", "web-service"]
    found = [c for c in expected if c in containers]
    print(f"  ✅ Found target containers: {found}")
    assert len(found) > 0, f"None of expected containers found. Got: {containers}"
