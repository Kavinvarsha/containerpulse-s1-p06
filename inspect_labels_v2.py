from prometheus_api_client import PrometheusConnect
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://127.0.0.1:43865"  # update if changed

prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

end_time = datetime.now()
start_time = end_time - timedelta(minutes=5)

# This time, filter using PromQL label matcher to exclude the generic node-level series
# and find proper per-container series with image/pod present
result = prom.custom_query_range(
    query='container_cpu_usage_seconds_total{image!=""}',
    start_time=start_time,
    end_time=end_time,
    step="15s",
)

print(f"Number of series with image label: {len(result)}\n")
for series in result[:5]:
    print(series["metric"])
    print("---")