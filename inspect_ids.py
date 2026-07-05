
from prometheus_api_client import PrometheusConnect
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://127.0.0.1:43865"  # your port here
prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

end_time = datetime.now()
start_time = end_time - timedelta(minutes=2)

result = prom.custom_query_range(
    query='container_cpu_usage_seconds_total',
    start_time=start_time,
    end_time=end_time,
    step="60s",
)

print(f"Total series: {len(result)}\n")
print("All unique IDs found:")
ids = set()
for series in result:
    ids.add(series["metric"].get("id", "NO_ID"))
for i in sorted(ids):
    print(f"  {i}")
EOF