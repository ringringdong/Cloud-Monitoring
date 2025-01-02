from datetime import datetime, timezone, timedelta
import oci

# OCI에서 사용할 compartment ID와 config 파일을 설정합니다.
compartment_id = "ocid1.compartment.oc1..aaaaaaaadoyp2j7rtd3ce5fffov4sututn2u7gb7oouoo2vz4urdxnuvrbvq"
config = oci.config.from_file("~/.oci/config", "DEFAULT")  # OCI config 파일을 읽어옵니다.
monitoring_client = oci.monitoring.MonitoringClient(config)  # OCI 모니터링 클라이언트 초기화

# 현재 시간 및 1분 전 시간 계산
now = (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
one_min_before = (datetime.utcnow() - timedelta(minutes=60)).isoformat() + 'Z'

# oci_compute_instance_health 네임스페이스의 instance_health_status 메트릭 데이터 요약
try:
    summarize_metrics_data_response = monitoring_client.summarize_metrics_data(
        compartment_id=compartment_id,
        summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace="oci_compute_instance_health",  # 새로운 네임스페이스
            query="instanceaccessibilitystatus[1m].mean()",  # 인스턴스 상태 메트릭 조회
            start_time=one_min_before,  # 조회 시작 시간
            end_time=now  # 조회 종료 시간
        )
    )

    # 응답 데이터 출력
    if summarize_metrics_data_response.data:
        for metric in summarize_metrics_data_response.data:
            print(f"Metric Name: {metric.name}")
            print(f"Dimensions: {metric.dimensions}")
            print(f"Metadata: {metric.metadata}")
            for datapoint in metric.aggregated_datapoints:
                print(f"Timestamp: {datapoint.timestamp}, Value: {datapoint.value}")
    else:
        print("No data returned for instance_health_status.")

except oci.exceptions.ServiceError as e:
    print(f"Service error occurred: {e}")
except Exception as e:
    print(f"Unexpected error occurred: {e}")
