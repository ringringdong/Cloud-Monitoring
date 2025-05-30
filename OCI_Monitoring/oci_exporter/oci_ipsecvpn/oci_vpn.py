from builtins import object, len
import time
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

import oci
from datetime import datetime, timezone, timedelta

compartment_id = "ocid1.compartment.oc1..aaaaaaaarped4jmus336d6dbhd5hc7ejdnyaplxby4kavr5c3yqakdkrdh5a"
config = oci.config.from_file("/root/.oci/config")
monitoring_client = oci.monitoring.MonitoringClient(config)

VPN_METRICS = [
    "TunnelState",
    "BytesReceived",
    "BytesSent",
    "PacketsDiscarded",
    "PacketsError",
    "PacketsReceived",
    "PacketsSent"
]

# function to retrieve mean statistic for specific namespace and metric
def metric_summary(now, one_min_before, metric_name, namespace, compartment_ocid):
    summarize_metrics_data_response = monitoring_client.summarize_metrics_data(
        compartment_id=compartment_ocid,
        summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace=namespace,
            query=f"{metric_name}[5m].mean()",
            start_time=one_min_before,
            end_time=now))
    return summarize_metrics_data_response.data


def get_metrics():
    now = (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    ONE_MIN_BEFORE = (datetime.utcnow() - timedelta(minutes=60)).isoformat() + 'Z'

    # Collect only Compute metrics
    for name in VPN_METRICS:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_vpn", compartment_id)
        if len(summary) > 0:
            yield summary
        else:
            break

    time.sleep(1)

class OCIExporter(object):
    def __init__(self):
        pass

    def collect(self):
        metric_data = list(get_metrics())
        for metrics in metric_data:
            for metric in metrics:
                name = f'oci_{metric.name.lower()}'
                dimensions = metric.dimensions
                
                # 터널을 구별할 수 있는 resourceName 사용
                resource_name = dimensions.get('resourceName', "unknown")
                
                labels = ['resource_name']
                metadata = metric.metadata
                description = metadata.get('displayName')
                value = metric.aggregated_datapoints[0].value

                g = GaugeMetricFamily(name=name, documentation=description, labels=labels)
                g.add_metric(labels=[resource_name], value=value)
                yield g


if __name__ == "__main__":
    start_http_server(8070)
    REGISTRY.register(OCIExporter())
    while True:
        time.sleep(5)
