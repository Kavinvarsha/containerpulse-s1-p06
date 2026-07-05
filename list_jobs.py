from prometheus_api_client import PrometheusConnect

PROMETHEUS_URL = "http://127.0.0.1:43415//39771http://39771"  # update if changed

prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

# Query Prometheus directly for label values of "job"
jobs = prom.get_label_values(label_name="job")
print("Available scrape jobs:")
for j in jobs:
    print(f"  - {j}")