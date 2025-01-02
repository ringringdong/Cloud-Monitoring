from prometheus_client import start_http_server, Gauge  # Prometheus 클라이언트 라이브러리에서 필요한 함수들 임포트
import requests  # HTTP 요청을 보내기 위한 라이브러리
import time  # 시간 관련 함수들 임포트
import hashlib  # 해싱을 위한 라이브러리
import hmac  # HMAC 서명 생성을 위한 라이브러리
import base64  # Base64 인코딩을 위한 라이브러리
import json  # JSON 데이터를 처리하기 위한 라이브러리

# Prometheus 메트릭 정의 (서버 상태를 나타낼 게이지 메트릭)
server_status_gauge = Gauge('server_status', 'Server instance status', ['server_name', 'server_instance_no'])

# 서버 상태를 조회하는 함수
def fetch_server_status():
    timestamp = int(time.time() * 1000)  # 현재 시간의 타임스탬프 (밀리초 단위로 변환)
    timestamp = str(timestamp)  # 타임스탬프를 문자열로 변환

    # Naver Cloud API 인증에 필요한 정보들
    ncloud_accesskey = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"  # Naver Cloud Access Key
    ncloud_secretkey = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L"  # Naver Cloud Secret Key
    apicall_method = "GET"  # API 호출 방법 (GET)
    space = " "  # 공백 문자 (서명 생성에 사용)
    new_line = "\n"  # 새로운 줄 문자 (서명 생성에 사용)
    api_server = "https://ncloud.apigw.ntruss.com"  # Naver Cloud API 서버 URL
    api_uri = "/vserver/v2/getServerInstanceList?responseFormatType=json"  # 서버 인스턴스 목록을 가져오는 API 경로

    # API 서명 생성
    message = apicall_method + space + api_uri + new_line + timestamp + new_line + ncloud_accesskey  # 서명에 사용할 메시지 작성
    message = bytes(message, 'UTF-8')  # 메시지를 바이트로 변환

    ncloud_secretkey = bytes(ncloud_secretkey, 'UTF-8')  # Secret Key를 바이트로 변환
    signingKey = base64.b64encode(hmac.new(ncloud_secretkey, message, digestmod=hashlib.sha256).digest())  # HMAC SHA256 서명 생성 후 Base64 인코딩

    # HTTP 헤더에 서명 및 인증 정보 포함
    http_header = {
        'x-ncp-apigw-timestamp': timestamp,  # 타임스탬프
        'x-ncp-iam-access-key': ncloud_accesskey,  # Access Key
        'x-ncp-apigw-signature-v2': signingKey  # 서명
    }

    # API 호출t
    response = requests.get(api_server + api_uri, headers=http_header)  # GET 요청을 보내고 응답 받기
    if response.status_code == 200:  # 응답 코드가 200이면 정상 처리
        data = response.json()  # JSON 응답을 파싱
        for server in data["getServerInstanceListResponse"]["serverInstanceList"]:  # 서버 인스턴스 목록 순회
            server_name = server["serverName"]  # 서버 이름
            server_instance_no = server["serverInstanceNo"]  # 서버 인스턴스 번호
            server_status = server["serverInstanceStatus"]["code"]  # 서버 상태 (RUN, STOP 등)
            
            # Prometheus 메트릭으로 서버 상태 업데이트 (RUN 상태는 1, STOP 상태는 0)
            server_status_gauge.labels(server_name=server_name, server_instance_no=server_instance_no).set(1 if server_status == "RUN" else 0)

# 메트릭 수집을 위한 HTTP 서버를 실행하는 함수
def run_exporter():
    start_http_server(8000)  # Prometheus가 8000 포트에서 메트릭을 수집할 수 있도록 HTTP 서버 시작
    while True:  # 무한 루프
        fetch_server_status()  # 서버 상태를 가져와서 Prometheus 메트릭을 갱신
        time.sleep(60)  # 60초마다 Naver Cloud API 호출

# 메인 함수, exporter를 실행
if __name__ == '__main__':
    run_exporter()  # exporter 실행
