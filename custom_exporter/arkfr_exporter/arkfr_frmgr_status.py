import subprocess
import re
from flask import Flask, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest

app = Flask(__name__)
registry = CollectorRegistry()

# 메트릭 정의
module_status = Gauge("arkfr_module_status", "Status of arkfr modules (1=Running, 0=Waiting)", ["module"], registry=registry)

def parse_frmgr_output():
    """frmgr status all 명령어 실행 후 출력 파싱"""
    try:
        result = subprocess.run(["sudo", "-u", "ark", "frmgr", "status", "all"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout

        if not output:
            print(f"Error: No output from frmgr command, stderr: {result.stderr}")
            return

        for line in output.split("\n"):
            match = re.match(r"(\S+)\s+P / Full\s+(\S+)", line)
            if match:
                module_name = match.group(1)
                status = match.group(2)
                module_status.set(labels={"module": module_name}, value=1 if status == "Running" else 0)

    except Exception as e:
        print(f"Error parsing frmgr output: {e}")

@app.route("/10.174_arkfr_metrics")
def metrics():
    """메트릭 업데이트 후 반환"""
    parse_frmgr_output()
    return Response(generate_latest(registry), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="172.16.10.174", port=8000)
