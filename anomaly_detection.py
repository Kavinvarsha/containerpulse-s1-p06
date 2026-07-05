
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import json
from datetime import datetime

df = pd.read_csv("metrics_ml_ready.csv", parse_dates=["timestamp"])

# Features used for anomaly detection
FEATURE_COLS = [col for col in ["cpu", "memory", "memory_cache", "network_rx", "network_tx"]
                if col in df.columns]

print(f"Using features: {FEATURE_COLS}")
print(f"Total containers: {df['container'].nunique()}")
print(f"Containers: {df['container'].unique()}\n")

results = []

# Train one Isolation Forest per container
for container_name, group in df.groupby("container"):
    group = group.sort_values("timestamp").reset_index(drop=True)

    if len(group) < 10:
        print(f"  ⚠️  Skipping {container_name} — not enough data ({len(group)} rows)")
        continue

    X = group[FEATURE_COLS].values

    # Normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,  # expect ~5% anomalies
        random_state=42
    )
    model.fit(X_scaled)

    # Predict: -1 = anomaly, 1 = normal
    predictions = model.predict(X_scaled)
    scores = model.decision_function(X_scaled)

    group["anomaly"] = predictions
    group["anomaly_score"] = scores
    group["is_anomaly"] = group["anomaly"] == -1

    anomaly_count = group["is_anomaly"].sum()
    total = len(group)

    print(f"  ✅ {container_name}: {anomaly_count}/{total} anomalies detected ({anomaly_count/total*100:.1f}%)")

    # Save anomaly details
    anomalies = group[group["is_anomaly"]][["timestamp", "container", "pod"] + FEATURE_COLS + ["anomaly_score"]]
    results.append({
        "container": container_name,
        "total_records": total,
        "anomaly_count": int(anomaly_count),
        "anomaly_percentage": round(anomaly_count/total*100, 2),
        "anomalies": anomalies.to_dict(orient="records")
    })

    # Save per-container results
    group.to_csv(f"anomaly_{container_name.replace('/', '_')}.csv", index=False)

# Save summary report
summary = {
    "generated_at": datetime.now().isoformat(),
    "total_containers_analyzed": len(results),
    "results": results
}

with open("anomaly_report.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\n📊 Anomaly detection complete!")
print(f"   Analyzed: {len(results)} containers")
print(f"   Report saved to: anomaly_report.json")
print(f"   Per-container CSVs saved as: anomaly_<container>.csv")
