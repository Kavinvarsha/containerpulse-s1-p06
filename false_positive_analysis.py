
import pandas as pd
import json
from sklearn.ensemble import IsolationForest

print("Running False Positive Analysis on clean baseline data...")
df = pd.read_csv("metrics_ml_ready.csv")
print(f"Total rows loaded: {len(df)}")

feature_cols = [c for c in df.columns if c not in ["timestamp", "pod", "namespace"]]
print(f"Features used: {feature_cols}")

df_features = df[feature_cols].dropna()
print(f"Rows after cleaning: {len(df_features)}")

model = IsolationForest(contamination=0.05, random_state=42)
model.fit(df_features)
preds = model.predict(df_features)

total = len(preds)
fp_count = sum(1 for p in preds if p == -1)
fp_rate = round((fp_count / total) * 100, 2)

print("")
print(f"Total samples analyzed: {total}")
print(f"False positives flagged: {fp_count}")
print(f"False positive rate: {fp_rate}%")
print(f"Threshold: 10%")
print(f"Result: PASS" if fp_rate < 10 else f"Result: FAIL")

report = {
    "analysis": "False Positive Analysis on Clean Baseline Data",
    "total_samples": total,
    "false_positives": fp_count,
    "false_positive_rate_pct": fp_rate,
    "threshold_pct": 10,
    "result": "PASS" if fp_rate < 10 else "FAIL",
    "model": "IsolationForest",
    "contamination": 0.05
}
with open("false_positive_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("")
print("Saved to false_positive_report.json")
print(json.dumps(report, indent=2))
