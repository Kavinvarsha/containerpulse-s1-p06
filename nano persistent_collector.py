import time
import subprocess
import datetime

print("Starting persistent metric collection. Press Ctrl+C to stop.")
while True:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run(["python", "fetch_metrics.py"])
    subprocess.run(["python", "transform_data.py"])
    print(f"[{timestamp}] Metrics collected and saved.")
    time.sleep(300)  # collect every 5 minutes