# 필요한 라이브러리들을 임포트합니다.
from builtins import object, len
import time
import sys
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import oci
from datetime import datetime, timezone, timedelta

# OCI에서 사용할 compartment ID와 config 파일을 설정합니다.
compartment_id = "ocid1.compartment.oc1..aaaaaaaadoyp2j7rtd3ce5fffov4sututn2u7gb7oouoo2vz4urdxnuvrbvq"
config = oci.config.from_file("~/.oci/config", "DEFAULT")  # OCI config 파일을 읽어옵니다.
monitoring_client = oci.monitoring.MonitoringClient(config)  # OCI 모니터링 클라이언트 초기화

# 각 메트릭 종류들을 정의합니다.
COMPUTE_METRICS = [
    "CpuUtilization",  # CPU 사용률
    "DiskBytesRead",  # 디스크 읽기 바이트
    "DiskBytesWritten",  # 디스크 쓰기 바이트
    "DiskIopsRead",  # 디스크 읽기 IOPS
    "DiskIopsWritten",  # 디스크 쓰기 IOPS
    "LoadAverage",  # 로드 평균
    "MemoryAllocationStalls",  # 메모리 할당 지연
    "MemoryUtilization",  # 메모리 사용률
    "NetworksBytesIn",  # 네트워크 수신 바이트
    "NetworksBytesOut"  # 네트워크 송신 바이트
]

VCN_METRICS1 = [
    "VnicConntrackIsFull",  # VNIC 연결 추적 가득 차기 여부
    "VnicConntrackUtilPercent",  # VNIC 연결 추적 활용률
    "VnicEgressDropsConntrackFull",  # VNIC 송신 드롭 (연결 추적 가득 차기)
    "VnicEgressDropsSecurityList",  # VNIC 송신 드롭 (보안 목록)
    "VnicEgressDropsThrottle",  # VNIC 송신 드롭 (속도 제한)
    "VnicEgressMirrorDropsThrottle",  # VNIC 송신 미러 드롭 (속도 제한)
    "VnicFromNetworkBytes",  # VNIC 수신 네트워크 바이트
    "VnicFromNetworkMirrorBytes",  # VNIC 수신 네트워크 미러 바이트
    "VnicFromNetworkMirrorPackets",  # VNIC 수신 네트워크 미러 패킷
    "VnicFromNetworkPackets"  # VNIC 수신 네트워크 패킷
]
VCN_METRICS2 = [
    "VnicIngressDropsConntrackFull",  # VNIC 수신 드롭 (연결 추적 가득 차기)
    "VnicIngressDropsSecurityList",  # VNIC 수신 드롭 (보안 목록)
    "VnicIngressDropsThrottle",  # VNIC 수신 드롭 (속도 제한)
    "VnicIngressMirrorDropsConntrackFull",  # VNIC 수신 미러 드롭 (연결 추적 가득 차기)
    "VnicIngressMirrorDropsSecurityList",  # VNIC 수신 미러 드롭 (보안 목록)
    "VnicIngressMirrorDropsThrottle",  # VNIC 수신 미러 드롭 (속도 제한)
    "VnicToNetworkBytes",  # VNIC 송신 네트워크 바이트
    "VnicToNetworkMirrorBytes",  # VNIC 송신 네트워크 미러 바이트
    "VnicToNetworkMirrorPackets",  # VNIC 송신 네트워크 미러 패킷
    "VnicToNetworkPackets",  # VNIC 송신 네트워크 패킷
]
OBJECTSTORAGE_METRICS = [
    "AllRequests",  # 모든 요청
    "ListRequests",  # 리스트 요청
    "ObjectCount",  # 객체 수
    "StoredBytes",  # 저장된 바이트
    "TotalRequestLatency",  # 전체 요청 대기 시간
]
health_METRICS = [
    "instanceaccessibilitystatus",  # 모든 요청
    "instancefilesystemstatus",  # 클라이언트 오류

]

VPN_METRICS = [
    "BytesReceived",
    "BytesSent",
    "PacketsDiscarded",
    "PacketsError",
    "PacketsReceived",
    "PacketsSent",
    "TunnelState"
]

# 특정 메트릭의 평균값을 반환하는 함수
def metric_summary(now, one_min_before, metric_name, namespace, compartment_ocid):
    # OCI 모니터링 API를 통해 메트릭 데이터를 요약해서 가져옵니다.
    summarize_metrics_data_response = monitoring_client.summarize_metrics_data(
        compartment_id=compartment_ocid,  # 모니터링할 compartment ID
        summarize_metrics_data_details=oci.monitoring.models.SummarizeMetricsDataDetails(
            namespace=namespace,  # 메트릭을 조회할 namespace
            query=f"{metric_name}[1m].mean()",  # 1분 간격으로 평균값을 계산
            start_time=one_min_before,  # 조회 시작 시간
            end_time=now  # 조회 종료 시간
        )
    )
    return summarize_metrics_data_response.data  # 메트릭 데이터를 반환


# 메트릭 데이터를 가져오는 함수
def get_metrics():
    now = (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))  # 현재 시간
    ONE_MIN_BEFORE = (datetime.utcnow() - timedelta(minutes=60)).isoformat() + 'Z'  # 1분 전 시간

    # COMPUTE_METRICS에 정의된 메트릭에 대해 데이터를 조회하고 반환합니다.
    for name in COMPUTE_METRICS:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_computeagent", compartment_id)
        if len(summary) > 0:
            yield summary  # 메트릭 데이터가 있으면 반환
        else:
            break

    time.sleep(1)  # 1초 대기 후 다음 메트릭을 조회합니다.
    
    # VCN_METRICS1에 정의된 VCN 관련 메트릭에 대해 조회
    for name in VCN_METRICS1:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_vcn", compartment_id)
        if len(summary) > 0:
            yield summary
        else:
            break

    time.sleep(1)
    
    # VCN_METRICS2에 정의된 추가적인 VCN 관련 메트릭 조회
    for name in VCN_METRICS2:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_vcn", compartment_id)
        if len(summary) > 0:
            yield summary
        else:
            break

    time.sleep(1)
    
    # OBJECTSTORAGE_METRICS에 정의된 객체 저장소 메트릭 조회
    for name in OBJECTSTORAGE_METRICS:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_objectstorage", compartment_id)
        if len(summary) > 0:
            yield summary
        else:
            break

    # OBJECTSTORAGE_METRICS에 정의된 객체 저장소 메트릭 조회
    for name in health_METRICS:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_compute_instance_health", compartment_id)
        if len(summary) > 0:
            yield summary
        else:
            break

    # VPN_METRICS에 정의된 객체 저장소 메트릭 조회
    for name in VPN_METRICS:
        summary = metric_summary(now, ONE_MIN_BEFORE, name, "oci_vpn", compartment_id)
        if len(summary) > 0:
            yield summary
        else:
            break



# Prometheus와 연동되는 Exporter 클래스
class OCIExporter(object):
    def __init__(self):
        pass

    # Prometheus에서 수집할 메트릭 데이터를 반환하는 함수
    def collect(self):
        # get_metrics 함수에서 가져온 메트릭 데이터를 리스트로 저장
        metric_data = list(get_metrics())
        
        # 각 메트릭에 대해 처리를 진행합니다.
        for metrics in metric_data:
            for metric in metrics:
                name = f'oci_{metric.name.lower()}'  # 메트릭 이름을 소문자로 변환하여 'oci_' 접두어를 붙임
                dimensions = metric.dimensions  # 메트릭의 차원 정보 (예: 리소스 이름 등)

                # resourceDisplayName 또는 resourceId로 레이블을 설정
                if dimensions.get('resourceDisplayName') is not None:
                    labels = ['resource_name']
                    resource_id = dimensions.get('resourceDisplayName')
                else:
                    labels = ['resource_id']
                    resource_id = dimensions.get('resourceId')

                # 메트릭 메타데이터에서 설명 가져오기
                metadata = metric.metadata
                description = metadata.get('displayName')
                value = metric.aggregated_datapoints[0].value  # 첫 번째 집계된 데이터 포인트의 값

                # Prometheus의 GaugeMetricFamily 객체 생성 (메트릭 값을 저장할 객체)
                g = GaugeMetricFamily(name=name, documentation=description, labels=labels)
                g.add_metric(labels=[resource_id], value=value)  # 메트릭 값 추가
                yield g  # Prometheus에 메트릭 반환


if __name__ == "__main__":
    # Prometheus 서버를 8070 포트에서 시작
    start_http_server(8070)
    
    # OCIExporter 클래스를 Prometheus 레지스트리에 등록
    REGISTRY.register(OCIExporter())
    
    # 무한 루프를 돌며 메트릭을 계속 수집합니다.
    while True:
        time.sleep(1)
