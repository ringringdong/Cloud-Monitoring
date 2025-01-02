from prometheus_client import start_http_server, Gauge
import hmac
import hashlib
import base64
import subprocess
import requests
import time

# 메트릭 정의
cpu_usage_gauge = Gauge('ncp_cpu_usage', 'CPU usage ratio', ['host_name', 'instance_no'])
mem_usage_gauge = Gauge('ncp_mem_usage', 'Memory usage ratio', ['host_name', 'instance_no'])
fs_usage_gauge = Gauge('ncp_fs_usage', 'Filesystem usage ratio', ['host_name', 'instance_no'])
server_status_gauge = Gauge('server_status', 'Server instance status', ['server_name', 'server_instance_no'])

# POST
def generate_signature(method, url, timestamp, access_key, secret_key):
    message = f"{method} {url}\n{timestamp}\n{access_key}"
    signing_key = bytes(secret_key, 'utf-8')
    mac = hmac.new(signing_key, message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode('utf-8')

# POST
def fetch_ncp_metrics():
    # 타임스탬프
    timestamp = subprocess.check_output(["date", "+%s%3N"]).decode("utf-8").strip()

    method = "POST"
    url = "/cw_fea/real/cw/api/servers/top?query=avg_cpu_used_rto"  
    access_key = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"  
    secret_key = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L" 

    # 서명 
    signature = generate_signature(method, url, timestamp, access_key, secret_key)

    # 헤더 
    headers = {
        "x-ncp-apigw-signature-v2": signature,
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": access_key,
    }

    # 요청 
    api_url = f"https://cw.apigw.ntruss.com/cw_fea/real/cw/api/servers/top?query=avg_cpu_used_rto"
    response = requests.post(api_url, headers=headers)

    # 결과 
    if response.status_code == 200:
        data = response.json()
        for server in data:
            host_name = server["hostName"]
            instance_no = server["instanceNo"]
            cpu_usage = server["avg_cpu_used_rto"]
            mem_usage = server["mem_usert"]
            fs_usage = server["avg_fs_usert"]

            # Prometheus 메트릭으로 상태 업데이트
            cpu_usage_gauge.labels(host_name=host_name, instance_no=instance_no).set(cpu_usage)
            mem_usage_gauge.labels(host_name=host_name, instance_no=instance_no).set(mem_usage)
            fs_usage_gauge.labels(host_name=host_name, instance_no=instance_no).set(fs_usage)
    else:
        print(f"API 요청 실패: {response.status_code} {response.text}")

# GET 
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
            
            
            server_status_gauge.labels(server_name=server_name, server_instance_no=server_instance_no).set(1 if server_status == "RUN" else 0)
    else:
        print(f"API 요청 실패: {response.status_code} {response.text}")

# Exporter 서버 시작
def run_exporter():
    start_http_server(8000)
    while True:
        fetch_ncp_metrics()  
        fetch_server_status() 
        time.sleep(60)  

if __name__ == '__main__':
    run_exporter()
