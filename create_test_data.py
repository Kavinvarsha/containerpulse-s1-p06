
import pandas as pd
import json
import sqlite3
from datetime import datetime

# Create metrics_raw.csv
pd.DataFrame({
    'timestamp': ['2026-06-19 08:00:00'] * 30,
    'pod': ['api-service']*10 + ['pipeline-worker']*10 + ['web-service']*10,
    'container': ['api-service']*10 + ['pipeline-worker']*10 + ['web-service']*10,
    'namespace': ['monitoring'] * 30,
    'metric': ['cpu'] * 30,
    'value': [0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1] * 3
}).to_csv('metrics_raw.csv', index=False)
print("Created metrics_raw.csv")

# Create metrics_ml_ready.csv
pd.DataFrame({
    'timestamp': ['2026-06-19 08:00:00'] * 3,
    'container': ['api-service', 'pipeline-worker', 'web-service'],
    'pod': ['api-service', 'pipeline-worker', 'web-service'],
    'namespace': ['monitoring', 'monitoring', 'monitoring'],
    'cpu': [0.1, 0.2, 0.3],
    'memory': [52428800, 62428800, 72428800],
    'memory_cache': [1000000, 2000000, 3000000],
    'network_rx': [100, 200, 300],
    'network_tx': [50, 100, 150],
    'restarts': [0, 0, 0]
}).to_csv('metrics_ml_ready.csv', index=False)
print("Created metrics_ml_ready.csv")

# Create anomaly_report.json
with open('anomaly_report.json', 'w') as f:
    json.dump({
        'generated_at': datetime.now().isoformat(),
        'total_containers_analyzed': 3,
        'results': [
            {
                'container': 'api-service',
                'total_records': 10,
                'anomaly_count': 1,
                'anomaly_percentage': 10.0,
                'anomalies': []
            },
            {
                'container': 'pipeline-worker',
                'total_records': 10,
                'anomaly_count': 0,
                'anomaly_percentage': 0.0,
                'anomalies': []
            },
            {
                'container': 'web-service',
                'total_records': 10,
                'anomaly_count': 1,
                'anomaly_percentage': 10.0,
                'anomalies': []
            }
        ]
    }, f)
print("Created anomaly_report.json")

# Create lstm_forecast.json
with open('lstm_forecast.json', 'w') as f:
    json.dump({
        'generated_at': datetime.now().isoformat(),
        'forecast_horizon': '6 steps x 30s = 180s',
        'forecasts': {
            'api-service': {
                'last_value': 0.1,
                'forecast': [0.11, 0.12, 0.11, 0.10, 0.11, 0.12],
                'unit': 'cpu_seconds_total'
            },
            'pipeline-worker': {
                'last_value': 0.2,
                'forecast': [0.21, 0.22, 0.21, 0.20, 0.21, 0.22],
                'unit': 'cpu_seconds_total'
            },
            'web-service': {
                'last_value': 0.3,
                'forecast': [0.31, 0.32, 0.31, 0.30, 0.31, 0.32],
                'unit': 'cpu_seconds_total'
            }
        }
    }, f)
print("Created lstm_forecast.json")

# Create SQLite database
conn = sqlite3.connect('containerpulse.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS anomaly_events (
        id INTEGER PRIMARY KEY,
        detected_at TEXT,
        container TEXT,
        total_records INTEGER,
        anomaly_count INTEGER,
        anomaly_percentage REAL
    )
''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS forecast_results (
        id INTEGER PRIMARY KEY,
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
    )
''')
conn.execute("INSERT INTO anomaly_events VALUES (NULL,'2026-06-19','api-service',10,1,10.0)")
conn.execute("INSERT INTO anomaly_events VALUES (NULL,'2026-06-19','pipeline-worker',10,0,0.0)")
conn.execute("INSERT INTO anomaly_events VALUES (NULL,'2026-06-19','web-service',10,1,10.0)")
conn.commit()
conn.close()
print("Created containerpulse.db")

print("\nAll test data created successfully!")
