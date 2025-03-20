import os
import subprocess
from flask import Flask, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest

app = Flask(__name__)
registry = CollectorRegistry()

# fr_dmn_ark 프로세스 실행 여부 메트릭
daemon_status = Gauge("fr_dmn_ark_status", "Status of fr_dmn_ark process (1=running, 0=stopped)", registry=registry)

def check_daemon():
    """fr_dmn_ark 프로세스 실행 여부 확인"""
    try:
        result = subprocess.run(["pgrep", "-f", "fr_dmn_ark"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 1 if result.stdout else 0
    except Exception as e:
        print(f"Error checking process: {e}")
        return 0  # 오류 발생 시 안전하게 0 반환

@app.route("/metrics")
def metrics():
    """메트릭 업데이트 후 반환"""
    daemon_status.set(check_daemon())
    return Response(generate_latest(registry), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
