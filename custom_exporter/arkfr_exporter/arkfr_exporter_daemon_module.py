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
    existing_modules = set()  # 기존 모듈을 추적할 집합
arkfr_modules_present {__name__="arkfr_modules_present", instance="172.16.10.175:9999", job="10.174_arkfr_info", module="source3"}

    while True:
        try:
            if os.path.exists(MODULE_PATH):
                modules = {f for f in os.listdir(MODULE_PATH) if os.path.isdir(os.path.join(MODULE_PATH, f))}
                new_modules = modules - existing_modules  # 새로 추가된 모듈
                removed_modules = existing_modules - modules  # 제거된 모듈

                # 새로 추가된 모듈에 대해 메트릭 업데이트
                for module in new_modules:
                    module_status.labels(module=module).set(1)

                # 제거된 모듈에 대해 메트릭 삭제
                for module in removed_modules:
                    module_status.remove(module=module)

                # 기존 모듈 목록 갱신
                existing_modules = modules

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
