
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import json
from datetime import datetime

df = pd.read_csv("metrics_ml_ready.csv", parse_dates=["timestamp"])

SEQUENCE_LENGTH = 10  # use last 10 readings to predict next one
FORECAST_STEPS = 6    # predict next 6 readings (= ~3 minutes at 30s intervals)

forecast_results = {}

for container_name, group in df.groupby("container"):
    group = group.sort_values("timestamp").reset_index(drop=True)

    if "cpu" not in group.columns or len(group) < SEQUENCE_LENGTH + 5:
        print(f"  ⚠️  Skipping {container_name} — not enough data")
        continue

    print(f"\n  🧠 Training LSTM for: {container_name}")

    # Use CPU usage for forecasting
    values = group["cpu"].values.reshape(-1, 1)

    # Normalize
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    # Build sequences
    X, y = [], []
    for i in range(len(scaled) - SEQUENCE_LENGTH):
        X.append(scaled[i:i+SEQUENCE_LENGTH])
        y.append(scaled[i+SEQUENCE_LENGTH])
    X, y = np.array(X), np.array(y)

    if len(X) < 5:
        print(f"  ⚠️  Skipping {container_name} — sequences too short")
        continue

    # Split train/test
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Build LSTM model
    model = Sequential([
        LSTM(32, return_sequences=True, input_shape=(SEQUENCE_LENGTH, 1)),
        Dropout(0.2),
        LSTM(16),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")

    # Train (silent)
    model.fit(X_train, y_train, epochs=20, batch_size=8, verbose=0)

    # Forecast next FORECAST_STEPS values
    last_sequence = scaled[-SEQUENCE_LENGTH:]
    predictions = []
    current_seq = last_sequence.copy()

    for _ in range(FORECAST_STEPS):
        pred = model.predict(current_seq.reshape(1, SEQUENCE_LENGTH, 1), verbose=0)
        predictions.append(pred[0, 0])
        current_seq = np.append(current_seq[1:], pred, axis=0)

    # Convert back to original scale
    predictions_original = scaler.inverse_transform(
        np.array(predictions).reshape(-1, 1)
    ).flatten()

    print(f"    Last CPU value: {values[-1][0]:.4f}")
    print(f"    Forecast next {FORECAST_STEPS} readings: {[round(p, 4) for p in predictions_original]}")

    forecast_results[container_name] = {
        "last_value": float(values[-1][0]),
        "forecast": predictions_original.tolist(),
        "unit": "cpu_seconds_total"
    }

# Save forecasts
output = {
    "generated_at": datetime.now().isoformat(),
    "forecast_horizon": f"{FORECAST_STEPS} steps x 30s = {FORECAST_STEPS*30}s",
    "forecasts": forecast_results
}

with open("lstm_forecast.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n📈 LSTM Forecasting complete!")
print(f"   Forecast saved to: lstm_forecast.json")
