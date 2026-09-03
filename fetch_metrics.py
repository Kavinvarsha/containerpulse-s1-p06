
from prometheus_api_client import PrometheusConnect
import pandas as pd
from datetime import datetime, timedelta

PROMETHEUS_URL = "😿  service monitoring/prometheus-kube-prometheus-prometheus has no node port"

prom = PrometheusConnect(url=PROMETHEUS_URL, disable_ssl=True)

TARGET_PODS = ["api-service", "pipeline-worker", "web-service"]

METRICS = {
    "cpu":        'container_cpu_usage_seconds_total{pod=~"api-service.*|pipeline-worker.*|web-service.*",cpu="total"}',
    "memory":     'container_memory_usage_bytes{pod=~"api-service.*|pipeline-worker.*|web-service.*"}',
    "memory_cache": 'container_memory_cache{pod=~"api-service.*|pipeline-worker.*|web-service.*"}',
    "network_rx": 'container_network_receive_bytes_total{namespace="monitoring"}',
    "network_tx": 'container_network_transmit_bytes_total{namespace="monitoring"}',
    "restarts":   'kube_pod_container_status_restarts_total{namespace="monitoring"}',
}

def fetch_metric(query, hours=1):
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    try:
        return prom.custom_query_range(
            query=query,
            start_time=start_time,
            end_time=end_time,
            step="30s",
        )
    except Exception as e:
        print(f"    Warning: {e}")
        return []

def to_dataframe(raw, metric_label):
    rows = []
    for series in raw:
        m = series["metric"]
        pod = m.get("pod", m.get("container", "unknown"))
        namespace = m.get("namespace", "monitoring")
        for ts, val in series["values"]:
            rows.append({
                "timestamp": datetime.fromtimestamp(float(ts)),
                "pod": pod,
                "namespace": namespace,
                "metric": metric_label,
                "value": float(val),
            })
    return pd.DataFrame(rows)

def main():
    print("Fetching metrics from Prometheus...")
    print(f"URL: {PROMETHEUS_URL}")
    print()

    # Quick connectivity check
    try:
        test = prom.custom_query('up')
        print(f"Prometheus connected. {len(test)} targets up.")
    except Exception as e:
        print(f"Cannot reach Prometheus: {e}")
        return

    all_dfs = []
    for label, query in METRICS.items():
        print(f"  Fetching: {label} ...")
        raw = fetch_metric(query, hours=1)
        if not raw:
            print(f"    No data returned for {label} - skipping")
            continue
        df = to_dataframe(raw, label)
        if df.empty:
            print(f"    Empty dataframe for {label}")
            continue
        pods = df["pod"].unique().tolist()
        print(f"    {len(df)} rows, pods: {pods}")
        all_dfs.append(df)

    if not all_dfs:
        print()
        print("No metrics collected! Checking what is available in Prometheus...")
        available = prom.custom_query('container_cpu_usage_seconds_total{namespace="monitoring"}')
        print(f"monitoring namespace CPU metrics: {len(available)} series")
        if available:
            print("Sample labels:", available[0]["metric"])
        return

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\nTotal rows: {len(combined)}")
    combined.to_csv("metrics_raw.csv", index=False)
    print("Saved to metrics_raw.csv")
    print("\nPreview:")
    print(combined.head(10))

if __name__ == "__main__":
    main()
