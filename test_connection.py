from prometheus_api_client import PrometheusConnect

# Replace with the URL from Step 8
PROMETHEUS_URL = "http://127.0.0.1:43865"

prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

if prom.check_prometheus_connection():
    print("✅ Successfully connected to Prometheus!")
else:
    print("❌ Connection failed")

metrics = prom.all_metrics()
print(f"\nTotal metrics available: {len(metrics)}")
print("\nSample container metrics found:")
for m in metrics:
    if "container_" in m:
        print(f"  - {m}")