from prometheus_client import start_http_server, Gauge
import requests
import time
import hashlib
import hmac
import base64
import json

# Prometheus 메트릭 정의
server_status_gauge = Gauge('server_status', 'Server instance status', ['server_name', 'server_instance_no'])

def fetch_server_status():
    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)

    ncloud_accesskey = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"
    ncloud_secretkey = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L"
    apicall_method = "GET"
    space = " "
    new_line = "\n"
    api_server = "https://ncloud.apigw.ntruss.com"
    api_uri = "/vserver/v2/getServerInstanceList?responseFormatType=json"

    message = apicall_method + space + api_uri + new_line + timestamp + new_line + ncloud_accesskey
    message = bytes(message, 'UTF-8')

    ncloud_secretkey = bytes(ncloud_secretkey, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(ncloud_secretkey, message, digestmod=hashlib.sha256).digest())

    http_header = {
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': ncloud_accesskey,
        'x-ncp-apigw-signature-v2': signingKey
    }

    response = requests.get(api_server + api_uri, headers=http_header)
    if response.status_code == 200:
        data = response.json()
        for server in data["getServerInstanceListResponse"]["serverInstanceList"]:
            server_name = server["serverName"]
            server_instance_no = server["serverInstanceNo"]
            server_status = server["serverInstanceStatus"]["code"]
            
            # Prometheus 메트릭으로 상태 업데이트 (0: STOP, 1: RUN)
            server_status_gauge.labels(server_name=server_name, server_instance_no=server_instance_no).set(1 if server_status == "RUN" else 0)

def run_exporter():
    start_http_server(8000)  # Prometheus가 8000 포트에서 메트릭을 수집할 수 있도록 서버 시작
    while True:
        fetch_server_status()
        time.sleep(60)  # 60초마다 Naver Cloud API 호출

if __name__ == '__main__':
    run_exporter()

