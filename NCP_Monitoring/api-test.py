import hmac
import hashlib
import base64
import requests
import time

# API 호출에 필요한 값들
access_key = "ncp_iam_BPASKR3NYwg5Zco0AHXZ"  # 실제 IAM 액세스 키
secret_key = "ncp_iam_BPKSKR4x2nVA9DYfBl8VA9ojwgZqFHkI0L"  # 실제 비밀 키

# 출력 활성화/비활성화 플래그
ENABLE_GET_OUTPUT = False
ENABLE_POST_OUTPUT = True

# 서명 생성 함수
def generate_signature(method, uri, timestamp, access_key, secret_key):
    message = f"{method} {uri}\n{timestamp}\n{access_key}"
    signing_key = bytes(secret_key, 'utf-8')
    mac = hmac.new(signing_key, message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode('utf-8')

# GET 방식 API 요청 함수
def fetch_get_api_data():
    method = "GET"
    uri = "/vserver/v2/getServerInstanceList?responseFormatType=json"
    api_server = "https://ncloud.apigw.ntruss.com"
    
    # 타임스탬프 생성
    timestamp = str(int(time.time() * 1000))
    
    # 서명 생성
    signature = generate_signature(method, uri, timestamp, access_key, secret_key)
    
    # 헤더 설정
    headers = {
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": access_key,
        "x-ncp-apigw-signature-v2": signature
    }
    
    # 요청 보내기
    response = requests.get(api_server + uri, headers=headers)
    
    # 결과 출력
    if ENABLE_GET_OUTPUT:
        if response.status_code == 200:
            print("GET 방식 API 요청 성공!")
            print(response.json())
        else:
            print(f"GET 방식 API 요청 실패: {response.status_code}")
            print(response.text)

# POST 방식 API 요청 함수
def fetch_post_api_data():
    method = "POST"
    uri = "/cw_fea/real/cw/api/servers/top?query=avg_cpu_user_rto"
    api_server = "https://cw.apigw.ntruss.com"
    
    # 타임스탬프 생성
    timestamp = str(int(time.time() * 1000))
    
    # 서명 생성
    signature = generate_signature(method, uri, timestamp, access_key, secret_key)
    
    # 헤더 설정
    headers = {
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": access_key,
        "x-ncp-apigw-signature-v2": signature,
        "Content-Type": "application/json"  # POST 요청에는 Content-Type을 설정
    }
    
    # 요청 본문 데이터
    payload = {
        "parameter1": "value1",  # 필요한 요청 파라미터를 여기에 추가
        "parameter2": "value2"
    }
    
    # 요청 보내기
    response = requests.post(api_server + uri, headers=headers, json=payload)
    
    # 결과 출력
    if ENABLE_POST_OUTPUT:
        if response.status_code == 200:
            print("POST 방식 API 요청 성공!")
            print(response.json())
        else:
            print(f"POST 방식 API 요청 실패: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    print("GET 방식 API 요청 실행 중...")
    fetch_get_api_data()
    print("\nPOST 방식 API 요청 실행 중...")
    fetch_post_api_data()
