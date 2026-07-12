

from prometheus_api_client import PrometheusConnect
import pandas as pd
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://127.0.0.1:34601"

prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

METRICS = {
    "cpu": 'container_cpu_usage_seconds_total{job="kubernetes-pods",container_label_io_kubernetes_docker_type="container"}',
    "memory": 'container_memory_usage_bytes{job="kubernetes-pods",container_label_io_kubernetes_docker_type="container"}',
    "memory_cache": 'container_memory_cache{job="kubernetes-pods",container_label_io_kubernetes_docker_type="container"}',
    "network_rx": 'container_network_receive_bytes_total{job="kubernetes-pods"}',
    "network_tx": 'container_network_transmit_bytes_total{job="kubernetes-pods"}',
    "restarts": 'kube_pod_container_status_restarts_total{namespace="monitoring"}',
}

def fetch_metric(query, hours=1):
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    return prom.custom_query_range(
        query=query,
        start_time=start_time,
        end_time=end_time,
        step="30s",
    )

def to_dataframe(raw, metric_label):
    rows = []
    for series in raw:
        m = series["metric"]
        pod = m.get("container_label_io_kubernetes_pod_name",
              m.get("pod", "unknown"))
        container = m.get("container_label_io_kubernetes_container_name",
                   m.get("container", pod))
        namespace = m.get("container_label_io_kubernetes_pod_namespace",
                   m.get("namespace", "unknown"))
        for ts, val in series["values"]:
            rows.append({
                "timestamp": datetime.fromtimestamp(float(ts)),
                "pod": pod,
                "container": container,
                "namespace": namespace,
                "metric": metric_label,
                "value": float(val),
            })
    return pd.DataFrame(rows)

def main():
    print("📡 Fetching metrics from Prometheus...\n")
    all_dfs = []

    for label, query in METRICS.items():
        print(f"  Fetching: {label} ...")
        raw = fetch_metric(query, hours=1)
        df = to_dataframe(raw, label)
        print(f"    → {len(df)} rows, containers: {df['container'].unique().tolist()}")
        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\n✅ Total rows: {len(combined)}")
    combined.to_csv("metrics_raw.csv", index=False)
    print("💾 Saved to metrics_raw.csv")
    print("\nPreview:")
    print(combined[combined["container"] != "unknown"].head(10))

if __name__ == "__main__":
    main()
