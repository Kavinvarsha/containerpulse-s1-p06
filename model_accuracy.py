
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import precision_score, recall_score, f1_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import json
from datetime import datetime

print("=" * 60)
print("CONTAINERPULSE MODEL ACCURACY REPORT")
print("=" * 60)

df = pd.read_csv("metrics_ml_ready.csv", parse_dates=["timestamp"])
FEATURE_COLS = [c for c in ["cpu","memory","memory_cache","network_rx","network_tx"] if c in df.columns]

# ─── WEEK 6: Isolation Forest Accuracy ───────────────────────
print("\n📊 WEEK 6: Isolation Forest Accuracy")
print("-" * 40)

isolation_results = {}

for container, group in df.groupby("container"):
    if len(group) < 10:
        continue

    X = group[FEATURE_COLS].fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_scaled)
    predictions = model.predict(X_scaled)

    # Simulate 3 failure types by injecting anomalies
    # Type 1: CPU spike
    X_cpu_spike = X_scaled.copy()
    X_cpu_spike[-3:, 0] = 10.0  # extreme CPU
    pred_cpu = model.predict(X_cpu_spike)
    cpu_detected = int(sum(pred_cpu[-3:] == -1))

    # Type 2: Memory leak
    X_mem_leak = X_scaled.copy()
    X_mem_leak[-3:, 1] = 10.0  # extreme memory
    pred_mem = model.predict(X_mem_leak)
    mem_detected = int(sum(pred_mem[-3:] == -1))

    # Type 3: Crash loop (high restarts)
    X_crash = X_scaled.copy()
    if len(FEATURE_COLS) > 4:
        X_crash[-3:, 4] = 10.0
    pred_crash = model.predict(X_crash)
    crash_detected = int(sum(pred_crash[-3:] == -1))

    anomaly_count = int(sum(predictions == -1))
    total = len(predictions)

    isolation_results[container] = {
        "total_samples": total,
        "anomalies_detected": anomaly_count,
        "anomaly_rate_pct": round(anomaly_count/total*100, 2),
        "cpu_spike_detection": f"{cpu_detected}/3",
        "memory_leak_detection": f"{mem_detected}/3",
        "crash_loop_detection": f"{crash_detected}/3",
        "false_positive_rate_pct": round((1 - anomaly_count/total)*100, 2)
    }

    print(f"\n  Container: {container}")
    print(f"    Anomalies detected: {anomaly_count}/{total} ({anomaly_count/total*100:.1f}%)")
    print(f"    CPU spike detection:    {cpu_detected}/3 injected")
    print(f"    Memory leak detection:  {mem_detected}/3 injected")
    print(f"    Crash loop detection:   {crash_detected}/3 injected")

# ─── WEEK 7: LSTM Accuracy (MAE + RMSE) ──────────────────────
print("\n\n📈 WEEK 7: LSTM Accuracy (MAE & RMSE)")
print("-" * 40)

lstm_results = {}
SEQUENCE_LENGTH = 10

for container, group in df.groupby("container"):
    if "cpu" not in group.columns or len(group) < SEQUENCE_LENGTH + 5:
        continue

    group = group.sort_values("timestamp").reset_index(drop=True)
    values = group["cpu"].fillna(0).values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    for i in range(len(scaled) - SEQUENCE_LENGTH):
        X.append(scaled[i:i+SEQUENCE_LENGTH])
        y.append(scaled[i+SEQUENCE_LENGTH])
    X, y = np.array(X), np.array(y)

    if len(X) < 5:
        continue

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    if len(X_test) == 0:
        continue

    model = Sequential([
        LSTM(32, return_sequences=True, input_shape=(SEQUENCE_LENGTH, 1)),
        Dropout(0.2),
        LSTM(16),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X_train, y_train, epochs=20, batch_size=8, verbose=0)

    y_pred = model.predict(X_test, verbose=0)
    y_pred_orig = scaler.inverse_transform(y_pred)
    y_test_orig = scaler.inverse_transform(y_test)

    mae = float(np.mean(np.abs(y_pred_orig - y_test_orig)))
    rmse = float(np.sqrt(np.mean((y_pred_orig - y_test_orig)**2)))

    lstm_results[container] = {
        "mae": round(mae, 6),
        "rmse": round(rmse, 6),
        "test_samples": len(y_test)
    }

    print(f"\n  Container: {container}")
    print(f"    MAE:  {mae:.6f}")
    print(f"    RMSE: {rmse:.6f}")
    print(f"    Test samples: {len(y_test)}")

# ─── Save Report ──────────────────────────────────────────────
report = {
    "generated_at": datetime.now().isoformat(),
    "week6_isolation_forest": isolation_results,
    "week7_lstm_accuracy": lstm_results
}

with open("model_accuracy_report.json", "w") as f:
    json.dump(report, f, indent=2)

with open("model_accuracy_report.txt", "w") as f:
    f.write("CONTAINERPULSE MODEL ACCURACY REPORT\n")
    f.write("="*60 + "\n\n")
    f.write("WEEK 6 — Isolation Forest Results\n")
    f.write("-"*40 + "\n")
    for c, r in isolation_results.items():
        f.write(f"\nContainer: {c}\n")
        for k, v in r.items():
            f.write(f"  {k}: {v}\n")
    f.write("\nWEEK 7 — LSTM Accuracy\n")
    f.write("-"*40 + "\n")
    for c, r in lstm_results.items():
        f.write(f"\nContainer: {c}\n")
        f.write(f"  MAE:  {r['mae']}\n")
        f.write(f"  RMSE: {r['rmse']}\n")

print("\n\n✅ Report saved to model_accuracy_report.json and model_accuracy_report.txt")
