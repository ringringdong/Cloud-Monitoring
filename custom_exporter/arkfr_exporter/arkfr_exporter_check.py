from flask import Flask, Response
from prometheus_client import Gauge, generate_latest
import subprocess
import re

app = Flask(__name__) # Flask 인스턴스 생성 코드 / 모듈 이름을 나타내는 파이썬 내장 변수 다른 파일에서 조회 했을 때 파일 이름으로 설정 됨

# Prometheus의 Gauge 메트릭을 설정
# Gauge는 값이 증가하거나 감소 할 수 있는 메트릭릭
number_of_files_gauge = Gauge('arkfr_number_of_files', 'Total number of files processed by ARKFR') # 메트릭 정의 구문 / 메트릭 이름, 설명 / 웹에서 조회 했을 때 출력 값값
number_of_created_files_gauge = Gauge('arkfr_number_of_created_files', 'Number of files created by ARKFR')
total_file_size_gauge = Gauge('arkfr_total_file_size', 'Total file size processed by ARKFR')

def get_metrics():
    try:
        # 명령어 실행 (여기서는 예시 경로로 설정)
        cmd = ["sudo", "-i", "-u", "ark", "/ark/fragent/bin/fr", "-n", "--stats", "-at", "--port=11812", "/pacs_backup/Nasbk/LT03/", "172.16.10.174::target/"]

        # 명령어 실행 결과
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # 명령어 출력에서 필요한 값들 추출
        #/d는 숫자 그리고 쉼표가 포함된 부분을 그룹으로 추출 / number_of_files_match = 'Number of files: 1,234'
        number_of_files_match = re.search(r'Number of files: ([\d,]+)', result.stdout) 
        number_of_created_files_match = re.search(r'Number of created files: ([\d,]+)', result.stdout)
        total_file_size_match = re.search(r'Total file size: ([\d,]+) bytes', result.stdout)

        # Number of files
        if number_of_files_match:
            number_of_files = int(number_of_files_match.group(1).replace(',', '')) #쉼표를 공백으로 변환 후 추출출
            number_of_files_gauge.set(number_of_files)  # Prometheus 메트릭에 값 설정

        # Number of created files
        if number_of_created_files_match:
            number_of_created_files = int(number_of_created_files_match.group(1).replace(',', ''))
            number_of_created_files_gauge.set(number_of_created_files)  

        # Total file size
        if total_file_size_match:
            total_file_size = int(total_file_size_match.group(1).replace(',', ''))
            total_file_size_gauge.set(total_file_size)  

    except Exception as e:
        print(f"Error: {e}")

@app.route('/arkfr_metrics')
def metrics():
    get_metrics()

    # Prometheus 포맷으로 메트릭 반환
    # Flask 애플리케이션에 등록된 모든 Prometheus 메트릭을 Prometheus 포맷
    # 메트릭 데이터를 텍스트 형식으로 HTTP 응답에 담아서 클라이언트에게 반환
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    # Flask 애플리케이션 실행 (0.0.0.0 주소로 설정하여 외부에서 접속 가능)
    app.run(host='0.0.0.0', port=8000)
