import json
import time
import hashlib
import hmac
import base64
import requests

# API 요청에 필요한 값들
access_key = 'ncp_iam_BPASKR3NYwg5Zco0AHXZ'
secret_key = 'ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L'
cw_key = '460438474722512896'
product_name = 'System/Server'
metric = ''
instance_no = '100769593'
time_start = 1734498000000  # 예시로 설정한 시간 (timestamp)
time_end = 1734584399000  # 예시로 설정한 시간 (timestamp)
interval = 'Min1'
aggregation = 'AVG'

# 현재 타임스탬프 (초단위)
timestamp = str(int(time.time() * 1000))

# 요청 바디 구성
payload = {
    "timeStart": time_start,
    "timeEnd": time_end,
    "cw_key": cw_key,
    "productName": product_name,
    "metric": metric,
    "interval": interval,
    "aggregation": aggregation,
    "dimensions": {
        "instanceNo": instance_no
    }
}

# 요청 헤더 생성 (서명)
def generate_signature(secret_key, method, url, timestamp, access_key, payload):
    message = method + " " + url + "\n" + timestamp + "\n" + access_key + "\n" + json.dumps(payload)
    secret_key_bytes = bytes(secret_key, 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    signature = hmac.new(secret_key_bytes, message_bytes, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

signature = generate_signature("POST", "/cw_fea/real/cw/api/data/query", timestamp, access_key, secret_key, payload)

# 요청 헤더 설정
headers = {
    "Content-Type": "application/json",
    "x-ncp-apigw-signature-v2": signature,
    "x-ncp-apigw-timestamp": timestamp,
    "x-ncp-iam-access-key": access_key
}

# API 요청 URL
url = "https://cw.apigw.ntruss.com/cw_fea/real/cw/api/data/query"

# API 호출
response = requests.post(url, headers=headers, data=json.dumps(payload))

# 응답 처리
if response.status_code == 200:
    print("응답 데이터:")
    print(response.json())
else:
    print(f"API 호출 실패: {response.status_code}")
    print(response.text)
