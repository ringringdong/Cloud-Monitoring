from flask import Flask, Response
from prometheus_client import Gauge, generate_latest
import subprocess
import re

app = Flask(__name__)
number_of_files_gauge = Gauge('arkfr_number_of_files', 'Total number of files processed by ARKFR')

def get_number_of_files():
    try:
        # 명령어 실행
        cmd = ["fr", "-n", "--stats", "-at", "--port=11812", "/pacs_backup/Nasbk/LT16/", "10.156.144.69::target31/"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Number of files 값 추출
        match = re.search(r'Number of files: ([\d,]+)', result.stdout)
        if match:
            number_of_files = int(match.group(1).replace(',', ''))
            number_of_files_gauge.set(number_of_files)
    except Exception as e:
        print(f"Error: {e}")

@app.route('/metrics')
def metrics():
    get_number_of_files()
    return Response(generate_latest(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
