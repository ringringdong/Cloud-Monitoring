from builtins import object, len  # 내장 함수 object, len을 명시적으로 가져옴 (사실상 불필요한 코드)
import time  # 시간 관련 기능 제공
from prometheus_client import start_http_server  # Prometheus 메트릭 HTTP 서버 시작
from prometheus_client.core import GaugeMetricFamily, REGISTRY  # Prometheus 메트릭 등록을 위한 라이브러리

import oci  # Oracle Cloud Infrastructure(OCI) SDK
from datetime import datetime, timezone, timedelta  # 날짜 및 시간 계산을 위한 라이브러리

# 모니터링할 OCI Compartment ID (OCI 환경에서 메트릭을 조회할 대상)
compartment_id = "ocid1.compartment.oc1..aaaaaaaadoyp2j7rtd3ce5fffov4sututn2u7gb7oouoo2vz4urdxnuvrbvq"

# OCI 설정 파일을 불러와서 API 요청을 수행할 클라이언트 객체 생성
config = oci.config.from_file("/root/.oci/config")
monitoring_client = oci.monitoring.MonitoringClient(config)  # OCI 모니터링 클라이언트 생성

# 조회할 Object Storage 관련 메트릭 리스트 정의
OBJECTSTORAGE_METRICS = [
    "ObjectCount",  # 오브젝트 스토리지 내 객체 개수
    "StoredBytes",  # 저장된 데이터 크기 (바이트)
    "AllRequests"   # 모든 요청 수
]

# 특정 네임스페이스(namespace)와 메트릭(metric_name)의 평균값(mean)을 조회하는 함수
def metric_summary(now, one_min_before, metric_name, namespace, compartment_ocid):
    summarize_metrics_data_response = monitoring_client.summarize_metrics_data(
        compartment_id=compartment_ocid,  # 조회할 Compartment ID
        summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace=namespace,  # 조회할 네임스페이스 (예: "oci_objectstorage")
            query=f"{metric_name}[5m].mean()",  # 5분 동안의 평균(mean) 값 조회
            start_time=one_min_before,  # 조회 시작 시간 (현재 시간에서 90분 전)
            end_time=now))  # 조회 종료 시간 (현재 시간)
    
    return summarize_metrics_data_response.data  # 조회된 메트릭 데이터를 반환

# Prometheus에서 수집할 메트릭 데이터를 가져오는 함수
def get_metrics():
    now = (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))  # 현재 시간 (ISO 8601 형식, UTC 기준)
    ONE_MIN_BEFORE = (datetime.utcnow() - timedelta(minutes=90)).isoformat() + 'Z'  # 90분 전 시간

    # Object Storage 관련 메트릭만 수집
    for name in OBJECTSTORAGE_METRICS:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_objectstorage", compartment_id)
        if len(summary) > 0:  # 수집된 데이터가 있는 경우
            yield summary  # 메트릭 데이터를 반환
        else:
            break  # 데이터가 없으면 루프 종료

    time.sleep(1)  # 1초 대기

# Prometheus Exporter 클래스 정의
class OCIExporter(object):
    def __init__(self):
        pass  # 생성자 (특별한 초기화 작업 없음)

    def collect(self):
        metric_data = list(get_metrics())  # get_metrics()를 호출하여 메트릭 데이터 가져오기
        for metrics in metric_data:
            for metric in metrics:
                name = f'oci_{metric.name.lower()}'  # 메트릭 이름을 소문자로 변환하여 Prometheus 형식으로 설정
                dimensions = metric.dimensions  # 메트릭의 차원 정보 가져오기

                # 리소스 이름이 존재하면 resource_name, 없으면 resource_id 사용
                if dimensions.get('resourceDisplayName') is not None:
                    labels = ['resource_name']
                    resource_id = dimensions.get('resourceDisplayName')
                else:
                    labels = ['resource_id']
                    resource_id = dimensions.get('resourceId')

                metadata = metric.metadata  # 메트릭의 메타데이터 가져오기
                description = metadata.get('displayName')  # 메트릭의 설명 가져오기
                value = metric.aggregated_datapoints[0].value  # 수집된 메트릭 값 가져오기

                # Prometheus GaugeMetricFamily 객체 생성 (단일 값 가짐)
                g = GaugeMetricFamily(name=name, documentation=description, labels=labels)
                g.add_metric(labels=[resource_id], value=value)  # 수집된 값 추가
                yield g  # Prometheus가 사용할 수 있도록 반환

# 메인 실행 부분
if __name__ == "__main__":
    start_http_server(9070)  # Prometheus가 데이터를 가져갈 수 있도록 HTTP 서버 시작 (포트 9070)
    REGISTRY.register(OCIExporter())  # Prometheus에 Exporter 등록
    while True:
        time.sleep(5)  # 5초마다 데이터 수집 루프 실행
