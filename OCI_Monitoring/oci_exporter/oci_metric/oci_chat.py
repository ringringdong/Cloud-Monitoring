from prometheus_client import start_http_server, Gauge
import time
import oci

# 메트릭 정의
compute_cpu_usage = Gauge('oci_computeagent_cpu_usage', 'CPU usage of Compute instances', ['resource_id', 'resource_display_name'])
vcn_bytes_in = Gauge('oci_vcn_bytes_in', 'Bytes received on VCN', ['resource_id', 'resource_display_name'])
vcn_bytes_out = Gauge('oci_vcn_bytes_out', 'Bytes sent from VCN', ['resource_id', 'resource_display_name'])
object_storage_size = Gauge('oci_objectstorage_bucket_size', 'Bucket size in Object Storage', ['bucket_name', 'storage_tier'])

# OCI 클라이언트 생성
def create_oci_client():
    config = oci.config.from_file("~/.oci/config")  # OCI 설정 파일 경로
    monitoring_client = oci.monitoring.MonitoringClient(config)
    return monitoring_client

# 메트릭 수집 함수
def collect_metrics():
    client = create_oci_client()
    compartment_id = "ocid1.compartment.oc1..aaaaaaaadoyp2j7rtd3ce5fffov4sututn2u7gb7oouoo2vz4urdxnuvrbvq"  # 컴파트먼트 OCID를 설정하세요.

    # oci_computeagent 네임스페이스 메트릭
    query_details = oci.monitoring.models.SummarizeMetricsDataDetails(
        start_time=int(time.time() - 60),  # 최근 1분
        end_time=int(time.time()),
        query="CpuUtilization[1m].max()",
        resource_group="<your_resource_group_id>"  # 리소스 그룹 ID 설정 (필요한 경우)
    )
    compute_metrics = client.summarize_metrics_data(compartment_id, query_details)
    for metric in compute_metrics.data:
        for datapoint in metric.aggregated_datapoints:
            compute_cpu_usage.labels(resource_id=metric.resource_id, resource_display_name=metric.resource_display_name).set(datapoint.value)

    # oci_vcn 네임스페이스 메트릭 (BytesIn, BytesOut)
    query_details_vcn = oci.monitoring.models.SummarizeMetricsDataDetails(
        start_time=int(time.time() - 60),  # 최근 1분
        end_time=int(time.time()),
        query="BytesIn[1m].sum(), BytesOut[1m].sum()",
        resource_group="<your_resource_group_id>"  # 리소스 그룹 ID 설정 (필요한 경우)
    )
    vcn_metrics = client.summarize_metrics_data(compartment_id, query_details_vcn)
    for metric in vcn_metrics.data:
        for datapoint in metric.aggregated_datapoints:
            if "BytesIn" in metric.query:
                vcn_bytes_in.labels(resource_id=metric.resource_id, resource_display_name=metric.resource_display_name).set(datapoint.value)
            elif "BytesOut" in metric.query:
                vcn_bytes_out.labels(resource_id=metric.resource_id, resource_display_name=metric.resource_display_name).set(datapoint.value)

    # oci_objectstorage 네임스페이스 메트릭 (Bucket size)
    query_details_storage = oci.monitoring.models.SummarizeMetricsDataDetails(
        start_time=int(time.time() - 3600),  # 최근 1시간
        end_time=int(time.time()),
        query="StoredBytes[1h].max()",
        resource_group="<your_resource_group_id>"  # 리소스 그룹 ID 설정 (필요한 경우)
    )
    object_storage_metrics = client.summarize_metrics_data(compartment_id, query_details_storage)
    for metric in object_storage_metrics.data:
        for datapoint in metric.aggregated_datapoints:
            storage_tier = metric.dimensions.get('tier', 'UNKNOWN')  # storage_tier가 없을 경우 기본값 'UNKNOWN'
            object_storage_size.labels(bucket_name=metric.resource_display_name, storage_tier=storage_tier).set(datapoint.value)

# Prometheus Exporter 시작
if __name__ == '__main__':
    # Exporter 서버 시작
    start_http_server(9999)
    print("Custom Exporter started at port 9999")  # 포트 번호 수정

    while True:
        collect_metrics()  # 메트릭 수집
        time.sleep(60)  # 1분마다 메트릭 업데이트
