from prometheus_client import start_http_server, Gauge
import psutil
import time

# Prometheus Gauges for different metrics
cpu_usage_metric = Gauge('cpu_usage_percent', 'CPU usage percentage', ['core'])
memory_usage_metric = Gauge('memory_usage_percent', 'Memory usage percentage')
disk_usage_metric = Gauge('disk_usage_percent', 'Disk usage percentage', ['disk'])
network_bytes_sent_metric = Gauge('network_bytes_sent', 'Total bytes sent over the network')
network_bytes_received_metric = Gauge('network_bytes_received', 'Total bytes received over the network')

def collect_cpu_metrics():
    # Get per-core CPU usage percentages
    cpu_percentages = psutil.cpu_percent(interval=1, percpu=True)
    for core_index, usage in enumerate(cpu_percentages):
        # Update the metric with core index and usage percentage
        cpu_usage_metric.labels(core=f'core_{core_index}').set(usage)

def collect_memory_metrics():
    # Get memory usage percentage
    memory_info = psutil.virtual_memory()
    memory_usage_metric.set(memory_info.percent)

def collect_disk_metrics():
    # Get disk usage percentage for each partition
    disk_partitions = psutil.disk_partitions()
    for partition in disk_partitions:
        try:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            disk_usage_metric.labels(disk=partition.device).set(disk_usage.percent)
        except PermissionError:
            # Ignore partitions we don't have permission to access
            continue

def collect_network_metrics():
    # Get network I/O statistics
    net_io = psutil.net_io_counters()
    network_bytes_sent_metric.set(net_io.bytes_sent)
    network_bytes_received_metric.set(net_io.bytes_recv)

if __name__ == '__main__':
    # Start the Prometheus HTTP server on port 8100
    start_http_server(8100)
    print("Custom Exporter is running on port 8100...")

    # Continuously collect and expose metrics
    while True:
        collect_cpu_metrics()
        collect_memory_metrics()
        collect_disk_metrics()
        collect_network_metrics()
        time.sleep(5)  # Scrape interval (adjust as needed)


