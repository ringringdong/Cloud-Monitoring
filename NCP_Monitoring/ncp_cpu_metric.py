import hmac
import hashlib
import base64
import subprocess
import requests
from datetime import datetime

# 타임스탬프 생성 (밀리초 포함)
timestamp = subprocess.check_output(["date", "+%s%3N"]).decode("utf-8").strip()

# 요청에 필요한 값들
method = "POST"
url = "/cw_fea/real/cw/api/servers/top?query=avg_cpu_used_rto"  # 예시로 CPU 사용률 조회
access_key = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"  # 실제 IAM 액세스 키
secret_key = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L"  # 실제 비밀 키

# 서명 생성
message = f"{method} {url}\n{timestamp}\n{access_key}"
signing_key = bytes(secret_key, 'utf-8')
mac = hmac.new(signing_key, message.encode('utf-8'), hashlib.sha256)
signature = base64.b64encode(mac.digest()).decode('utf-8')

# 헤더 설정
headers = {
    "x-ncp-apigw-signature-v2": signature,
    "x-ncp-apigw-timestamp": timestamp,
    "x-ncp-iam-access-key": access_key,
}

# 요청 보내기
api_url = "https://cw.apigw.ntruss.com/cw_fea/real/cw/api/servers/top?query=avg_cpu_used_rto"
response = requests.post(api_url, headers=headers)

# 결과 출력
if response.status_code == 200:
    print("응답 성공:", response.json())
else:
    print("응답 실패:", response.status_code, response.text)
