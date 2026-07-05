# import pandas as pd

# df = pd.read_csv("metrics_raw.csv", parse_dates=["timestamp"])

# # Pivot: one row per (timestamp, container), one column per metric
# pivoted = df.pivot_table(
#     index=["timestamp", "container"],
#     columns="metric",
#     values="value",
#     aggfunc="mean"
# ).reset_index()

# # Sort chronologically
# pivoted = pivoted.sort_values(["container", "timestamp"])

# print("✅ Pivoted shape:", pivoted.shape)
# print("\nColumns:", list(pivoted.columns))
# print("\nPreview:")
# print(pivoted.head(10))

# # Save the ML-ready dataset
# pivoted.to_csv("metrics_ml_ready.csv", index=False)
# print("\n💾 Saved to metrics_ml_ready.csv")

import pandas as pd

df = pd.read_csv("metrics_raw.csv", parse_dates=["timestamp"])

# Keep only real containers (not unknown)
df = df[df["container"] != "unknown"]
df = df[df["container"] != "POD"]

print(f"Unique containers found: {df['container'].unique()}")

# Pivot to wide format: one row per (timestamp, container)
pivoted = df.pivot_table(
    index=["timestamp", "container", "pod", "namespace"],
    columns="metric",
    values="value",
    aggfunc="mean"
).reset_index()

pivoted = pivoted.sort_values(["container", "timestamp"])

# Fill missing values with forward fill then 0
pivoted = pivoted.ffill().fillna(0)

print(f"\n✅ Shape: {pivoted.shape}")
print(f"Columns: {list(pivoted.columns)}")
print(f"\nPreview:")
print(pivoted.head(10))

pivoted.to_csv("metrics_ml_ready.csv", index=False)
print("\n💾 Saved to metrics_ml_ready.csv")
