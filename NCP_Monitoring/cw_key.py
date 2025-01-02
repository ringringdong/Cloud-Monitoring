import json
import time
import hashlib
import hmac
import base64
import requests

# API 요청에 필요한 값들
access_key = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"  # 실제 IAM 액세스 키
secret_key = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L"  # 실제 비밀 키

# 현재 타임스탬프 (초단위)
timestamp = str(int(time.time() * 1000))

# 요청 헤더 생성 (서명)
def generate_signature(secret_key, method, url, timestamp, access_key):
    message = method + " " + url + "\n" + timestamp + "\n" + access_key
    secret_key_bytes = bytes(secret_key, 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    signature = hmac.new(secret_key_bytes, message_bytes, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

# 서명 생성
signature = generate_signature(secret_key, "GET", "/cw_fea/real/cw/api/schema/system/list", timestamp, access_key)

# 요청 헤더 설정
headers = {
    "x-ncp-apigw-signature-v2": signature,
    "x-ncp-apigw-timestamp": timestamp,
    "x-ncp-iam-access-key": access_key
}

# API 요청 URL
url = "https://cw.apigw.ntruss.com/cw_fea/real/cw/api/schema/system/list"

# API 호출
response = requests.get(url, headers=headers)

# 응답 처리
if response.status_code == 200:
    print("cw_key 리스트:")
    data = response.json()
    for item in data:
        print(f"prodName: {item['prodName']}, cw_key: {item['cw_key']}")
else:
    print(f"API 호출 실패: {response.status_code}")
    print(response.text)
