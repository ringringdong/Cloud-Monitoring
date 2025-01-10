from prometheus_client import start_http_server, Gauge
import psutil
import time

# Prometheus Gauge to collect CPU usage information
cpu_usage_metric = Gauge('cpu_usage_percent', 'CPU usage percentage', ['core'])

def collect_cpu_metrics():
    # Get per-core CPU usage percentages
    cpu_percentages = psutil.cpu_percent(interval=1, percpu=True)
    for core_index, usage in enumerate(cpu_percentages):
        # Update the metric with core index and usage percentage
        cpu_usage_metric.labels(core=f'core_{core_index}').set(usage)

if __name__ == '__main__':
    # Start the Prometheus HTTP server on port 8100
    start_http_server(8100)
    print("Custom CPU Exporter is running on port 8100...")

    # Continuously collect and expose metrics
    while True:
        collect_cpu_metrics()
        time.sleep(5)  # Scrape interval (adjust as needed)
