from prometheus_client import start_http_server, Gauge  # Prometheus 관련 라이브러리 가져오기
import requests  # HTTP 요청을 보낼 수 있는 라이브러리
import time  # 시간 관련 라이브러리
import hashlib  # 해시 함수 라이브러리
import hmac  # HMAC(해시 기반 메시지 인증 코드) 라이브러리
import base64  # Base64 인코딩/디코딩 라이브러리
import json  # JSON 처리 라이브러리

# Prometheus 메트릭 정의
# server_status_gauge: 서버 상태를 나타내는 메트릭으로, 'server_name'과 'server_instance_no'를 레이블로 사용
server_status_gauge = Gauge('server_status', 'Server instance status', ['server_name', 'server_instance_no'])

def fetch_server_status():
    # 현재 시간을 밀리초로 가져오기
    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)  # timestamp는 문자열로 변환

    # 네이버 클라우드 API 인증에 필요한 액세스 키와 시크릿 키
    ncloud_accesskey = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"
    ncloud_secretkey = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L"
    
    # API 호출 방식 (GET 요청)
    apicall_method = "GET"
    space = " "
    new_line = "\n"
    
    # 네이버 클라우드 API 서버와 URI 설정
    api_server = "https://ncloud.apigw.ntruss.com"
    api_uri = "/vserver/v2/getServerInstanceList?responseFormatType=json"

    # 서명 생성에 필요한 메시지 구성
    # 메시지 구성: HTTP 메서드 + API URI + timestamp + access key 순으로 연결
    message = apicall_method + space + api_uri + new_line + timestamp + new_line + ncloud_accesskey
    message = bytes(message, 'UTF-8')  # 메시지를 바이트 형태로 변환

    # 시크릿 키를 바이트 형태로 변환
    ncloud_secretkey = bytes(ncloud_secretkey, 'UTF-8')
    
    # 서명 생성 (HMAC + SHA256)
    signingKey = base64.b64encode(hmac.new(ncloud_secretkey, message, digestmod=hashlib.sha256).digest())

    # 요청 헤더에 필요한 값 설정
    http_header = {
        'x-ncp-apigw-timestamp': timestamp,  # 타임스탬프
        'x-ncp-iam-access-key': ncloud_accesskey,  # 액세스 키
        'x-ncp-apigw-signature-v2': signingKey  # 서명
    }

    # Naver Cloud API 호출 (서버 인스턴스 리스트 가져오기)
    response = requests.get(api_server + api_uri, headers=http_header)
    
    if response.status_code == 200:  # 요청이 성공적으로 처리되었을 경우
        data = response.json()  # 응답을 JSON 형태로 파싱
        # 서버 인스턴스 리스트를 순회
        for server in data["getServerInstanceListResponse"]["serverInstanceList"]:
            server_name = server["serverName"]  # 서버 이름
            server_instance_no = server["serverInstanceNo"]  # 서버 인스턴스 번호
            server_status = server["serverInstanceStatus"]["code"]  # 서버 상태 (RUN, STOP 등)

            # Prometheus 메트릭으로 상태 업데이트
            # 상태가 'RUN'이면 1로 설정, 'STOP'이면 0으로 설정
            server_status_gauge.labels(server_name=server_name, server_instance_no=server_
