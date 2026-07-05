
import sqlite3
import json
import pandas as pd
import os
from datetime import datetime

# Connect to SQLite (creates file if not exists)
conn = sqlite3.connect("containerpulse.db")
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS anomaly_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at TEXT,
    container TEXT,
    total_records INTEGER,
    anomaly_count INTEGER,
    anomaly_percentage REAL
);

CREATE TABLE IF NOT EXISTS forecast_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_at TEXT,
    container TEXT,
    last_value REAL,
    forecast_1 REAL,
    forecast_2 REAL,
    forecast_3 REAL,
    forecast_4 REAL,
    forecast_5 REAL,
    forecast_6 REAL,
    trend TEXT
);

CREATE TABLE IF NOT EXISTS incident_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    groq_analysis TEXT,
    incident_report TEXT
);
""")

# Load and store anomaly results
with open("anomaly_report.json") as f:
    anomaly = json.load(f)

for c in anomaly["results"]:
    cursor.execute("""
        INSERT INTO anomaly_events
        (detected_at, container, total_records, anomaly_count, anomaly_percentage)
        VALUES (?, ?, ?, ?, ?)
    """, (
        anomaly["generated_at"],
        c["container"],
        c["total_records"],
        c["anomaly_count"],
        c["anomaly_percentage"]
    ))

print(f"✅ Stored {len(anomaly['results'])} anomaly records")

# Load and store forecast results
with open("lstm_forecast.json") as f:
    forecast = json.load(f)

for name, data in forecast["forecasts"].items():
    f_vals = data["forecast"]
    trend = "RISING" if f_vals[-1] > data["last_value"] else "STABLE"
    cursor.execute("""
        INSERT INTO forecast_results
        (generated_at, container, last_value,
         forecast_1, forecast_2, forecast_3,
         forecast_4, forecast_5, forecast_6, trend)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        forecast["generated_at"], name,
        data["last_value"],
        f_vals[0], f_vals[1], f_vals[2],
        f_vals[3], f_vals[4], f_vals[5],
        trend
    ))

print(f"✅ Stored {len(forecast['forecasts'])} forecast records")

# Load and store incident report
if os.path.exists("incident_report.json"):
    with open("incident_report.json") as f:
        report = json.load(f)
    cursor.execute("""
        INSERT INTO incident_reports (created_at, groq_analysis, incident_report)
        VALUES (?, ?, ?)
    """, (
        report["generated_at"],
        report["groq_analysis"],
        report["incident_report"]
    ))
    print("✅ Stored incident report")

conn.commit()
conn.close()
print("\n💾 All data saved to: containerpulse.db")

# Verify by reading back
conn = sqlite3.connect("containerpulse.db")
print("\n=== DATABASE CONTENTS ===")
print(f"Anomaly events: {pd.read_sql('SELECT COUNT(*) as count FROM anomaly_events', conn).iloc[0,0]}")
print(f"Forecast results: {pd.read_sql('SELECT COUNT(*) as count FROM forecast_results', conn).iloc[0,0]}")
print(f"\nAnomaly Summary:")
print(pd.read_sql("SELECT container, anomaly_count, anomaly_percentage FROM anomaly_events ORDER BY anomaly_percentage DESC", conn).to_string())
conn.close()
