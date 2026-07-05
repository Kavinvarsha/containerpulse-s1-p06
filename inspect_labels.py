from prometheus_api_client import PrometheusConnect
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://127.0.0.1:43865"  # update if changed

prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

end_time = datetime.now()
start_time = end_time - timedelta(minutes=5)

result = prom.get_metric_range_data(
    metric_name="container_cpu_usage_seconds_total",
    start_time=start_time,
    end_time=end_time,
)

print(f"Number of series: {len(result)}\n")
print("Labels on first 3 series:\n")
for series in result[:3]:
    print(series["metric"])
    print("---")