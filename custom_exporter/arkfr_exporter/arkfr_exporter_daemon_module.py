import subprocess
import os
import threading
import time
from flask import Flask, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest

app = Flask(__name__)
registry = CollectorRegistry()

# fr_dmn_ark 프로세스 실행 여부 메트릭
daemon_status = Gauge("arkfr_dmn_status", "Status of arkfr_dmn process (1=running, 0=stopped)", registry=registry)

# /ark/fragent/conf/module 내 파일 목록 수집
module_status = Gauge("arkfr_modules_present", "Presence of modules in /ark/fragent/conf/module (1=Exists)", ["module"], registry=registry)

MODULE_PATH = "/ark/fragent/conf/module"

def check_daemon():
    """fr_dmn_ark 프로세스 실행 여부 확인"""
    try:
        result = subprocess.run(["pgrep", "-f", "fr_dmn_ark"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 1 if result.stdout else 0
    except Exception as e:
        print(f"Error checking process: {e}")
        return 0  # 오류 발생 시 안전하게 0 반환

def update_module_list():
    """/ark/fragent/conf/module 디렉토리 내 존재하는 파일 목록을 수집하여 Prometheus 메트릭에 저장"""
    while True:
        try:
            if os.path.exists(MODULE_PATH):
                modules = [f for f in os.listdir(MODULE_PATH) if os.path.isfile(os.path.join(MODULE_PATH, f))]
                module_status.clear()  # 기존 값 초기화
                for module in modules:
                    module_status.labels(module=module).set(1)  # 존재하는 모듈에 대해 1 설정
        except Exception as e:
            print(f"Error updating module list: {e}")

        time.sleep(5)  # 5초마다 갱신

@app.route("/10.174_arkfr_metrics")
def metrics():
    """메트릭 업데이트 후 반환"""
    daemon_status.set(check_daemon())
    return Response(generate_latest(registry), mimetype="text/plain")

if __name__ == "__main__":
    # 모듈 목록을 주기적으로 업데이트하는 스레드 실행
    thread = threading.Thread(target=update_module_list, daemon=True)
    thread.start()

    app.run(host="172.16.10.174", port=8000)
